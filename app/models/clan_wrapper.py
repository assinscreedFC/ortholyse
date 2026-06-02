# =============================================================================
# Auteur  : Ortholyse
# Version : 0.1 (amorce spike Phase 1 — réutilisable Phase 2)
# =============================================================================
"""Amorce réutilisable pour l'intégration CLAN/MOR (Phase 2).

Ce module fournit :
  - ``find_clan_mor`` : résolution du binaire ``mor`` (pattern find_ffmpeg)
  - ``run_mor``       : wrapper subprocess pour annoter un fichier .cha
  - ``parse_mor_tier``: extraction des tokens du tier ``%mor`` depuis le texte .cha
  - ``compute_mlu_morphemes`` : calcul de la MLU en morphèmes depuis un fichier .cha

Contraintes de sécurité (T-01-07 / T-01-09) :
  - ``run_mor`` utilise une liste d'arguments, jamais ``shell=True``.
  - L'encodage UTF-8 est forcé pour éviter les corruptions CP-1252 (Pitfall 2).
  - Aucune donnée patient n'est loggée (l'échantillon CHILDES est public).
"""
from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes internes
# ---------------------------------------------------------------------------

# Un token %mor valide contient au moins un '|' (ex : det|le, v|manger-PRES&3S)
_MOR_TOKEN = re.compile(r"\S+\|\S+")

# Codes à exclure — si présents dans un énoncé %mor, l'énoncé entier est ignoré
_CODES_EXCLUS: frozenset[str] = frozenset({"xxx", "yyy", "www", "0"})


# ---------------------------------------------------------------------------
# Résolution du binaire mor (pattern calqué sur find_ffmpeg)
# ---------------------------------------------------------------------------


def find_clan_mor() -> str:
    """Retourne un chemin utilisable vers le binaire ``mor`` de CLAN.

    Ordre de résolution (calqué sur ``operation_fichier.find_ffmpeg``) :

    1. Bundle PyInstaller (frozen) → ``_internal/clan/mor``
    2. Binaire embarqué en développement → ``app/../bin/clan/mor``
    3. ``mor`` détecté dans le PATH système (CLAN installé globalement)
    4. Littéral ``'mor'`` — lèvera ``FileNotFoundError`` si absent

    Sur Windows, ``shutil.which('mor')`` trouve ``mor.exe`` automatiquement.
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
        return os.path.abspath(os.path.join(base, "_internal", "clan", "mor"))

    vendored = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "bin", "clan", "mor")
    )
    if os.path.isfile(vendored):
        return vendored

    system = shutil.which("mor")
    if system:
        return system

    return "mor"


# ---------------------------------------------------------------------------
# Wrapper subprocess run_mor
# ---------------------------------------------------------------------------


def run_mor(cha_path: str, grammar_dir: str, mor_bin: str | None = None) -> str:
    """Appelle le binaire ``mor`` de CLAN sur un fichier ``.cha`` et annote le tier ``%mor``.

    Arguments :
        cha_path    : chemin absolu vers le fichier ``.cha`` à annoter.
        grammar_dir : chemin vers le répertoire de la grammaire française (``fra/``).
        mor_bin     : chemin vers l'exécutable ``mor`` ; si ``None``, résolu via
                      ``find_clan_mor()``.

    Retourne :
        Le chemin ``cha_path`` après annotation (``mor +1`` écrit directement dans
        le fichier d'entrée — **toujours travailler sur une copie**, jamais sur la
        fixture originale — Pitfall 3).

    Lève :
        RuntimeError si le binaire ``mor`` retourne un code non nul.

    Sécurité (T-01-07) : les arguments sont toujours passés en liste, jamais via
    ``shell=True``. Encodage UTF-8 forcé (T-01-09, Pitfall 2).
    """
    mor_bin = mor_bin or find_clan_mor()

    env = os.environ.copy()
    # MORLIB indique à mor le répertoire de la grammaire (variable d'environnement
    # utilisée en mode headless ; alternative au flag +l)
    env["MORLIB"] = grammar_dir

    args: list[str] = [
        mor_bin,
        "+l",
        grammar_dir,
        "+1",          # +1 : écrire le résultat dans le fichier d'entrée (overwrite)
        cha_path,
    ]

    logger.info("Exécution mor sur %s (grammaire : %s)", cha_path, grammar_dir)

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(f"mor a échoué (code {result.returncode}) : {result.stderr}")

    logger.info("mor terminé avec succès sur %s", cha_path)
    return cha_path


# ---------------------------------------------------------------------------
# Parsing du tier %mor
# ---------------------------------------------------------------------------


def parse_mor_tier(cha_text: str) -> list[list[str]]:
    """Extrait les tokens morphémiques depuis le texte d'un fichier ``.cha``.

    Pour chaque ligne commençant par ``%mor:``, extrait les tokens via le regex
    ``\\S+\\|\\S+`` (tout token contenant ``|`` = une unité ``POS|lemme``).
    Un énoncé entier est exclu si l'un de ses éléments bruts appartient à
    ``{xxx, yyy, www, 0}``.

    Arguments :
        cha_text : contenu complet d'un fichier ``.cha`` (UTF-8).

    Retourne :
        Liste d'énoncés ; chaque énoncé est une liste de tokens ``POS|lemme``.
        La ponctuation (``.``, ``?``, ``!``) n'est jamais incluse car elle ne
        contient pas de ``|``.
    """
    enonces: list[list[str]] = []

    for ligne in cha_text.splitlines():
        ligne = ligne.strip()
        if not ligne.startswith("%mor:"):
            continue

        contenu = ligne[len("%mor:"):].strip()

        # Exclure l'énoncé si un token brut est un code exclus
        tokens_bruts = contenu.split()
        if any(tok in _CODES_EXCLUS for tok in tokens_bruts):
            continue

        # Extraire uniquement les tokens contenant '|' (exclut la ponctuation)
        tokens = _MOR_TOKEN.findall(contenu)
        if tokens:
            enonces.append(tokens)

    return enonces


# ---------------------------------------------------------------------------
# Calcul de la MLU en morphèmes
# ---------------------------------------------------------------------------


def compute_mlu_morphemes(cha_path: str) -> float:
    """Calcule la MLU (Mean Length of Utterance) en morphèmes depuis un fichier ``.cha``.

    Méthode CLAN : compte les tokens ``POS|lemme`` sur les lignes ``%mor:``,
    en excluant les énoncés contenant ``xxx``/``yyy``/``www``/``0`` et la ponctuation.
    Chaque token ``POS|...`` est compté comme 1 unité morphologique (A4 / D-08 :
    la décomposition fine des suffixes est reportée à la Phase 2).

    Arguments :
        cha_path : chemin vers un fichier ``.cha`` annoté (contenant un tier ``%mor:``).

    Retourne :
        MLU en morphèmes, arrondie à 3 décimales.

    Lève :
        ValueError si aucun énoncé valide n'est trouvé dans le tier ``%mor``.
    """
    texte = Path(cha_path).read_text(encoding="utf-8")
    enonces = parse_mor_tier(texte)

    if not enonces:
        raise ValueError(
            f"Aucun énoncé valide trouvé dans le tier %mor de '{cha_path}'"
        )

    total_morphemes = sum(len(e) for e in enonces)
    mlu = round(total_morphemes / len(enonces), 3)

    logger.info(
        "MLU-morphèmes calculée : %.3f (%d énoncés, %d morphèmes) — fichier : %s",
        mlu,
        len(enonces),
        total_morphemes,
        cha_path,
    )

    return mlu
