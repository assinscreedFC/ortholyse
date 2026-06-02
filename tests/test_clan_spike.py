"""Tests du spike CLAN — Plan 01-03.

Couvre :
  - SPIKE-03 : parsing du tier %mor + calcul MLU morphèmes (CI sans CLAN)
  - Intégration run_mor (gated sur présence du binaire mor)
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constantes de test
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CHA = FIXTURES_DIR / "sample_fra.cha"
MTLN_CHA = FIXTURES_DIR / "mtln_sample.cha"

# Oracle déterministe sample_fra.cha :
# Énoncé 1 : det|le n|chat v|manger-PRES&3S        -> 3 tokens
# Énoncé 2 : pro|il v|vouloir-PRES&3S det:art|de+det|le n|lait -> 4 tokens
# Énoncé 3 : n|maman                                -> 1 token
# MLU = (3 + 4 + 1) / 3 = 2.667
ORACLE_MLU = 2.667

# MTLN 30 mois (Parisse & Le Normand 2002) :
MLU_M_ATTENDUE = 3.02  # plage normative 30 mois
MLU_TOLERANCE = 0.5  # D-08 : souple sur la métrique


# ---------------------------------------------------------------------------
# Tests unitaires — parsing %mor (sans CLAN, CI-safe)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_mor_tier_renvoie_trois_enonces() -> None:
    """parse_mor_tier doit retourner exactement 3 énoncés depuis sample_fra.cha."""
    from app.models.clan_wrapper import parse_mor_tier

    texte = SAMPLE_CHA.read_text(encoding="utf-8")
    enonces = parse_mor_tier(texte)
    assert len(enonces) == 3, f"Attendu 3 énoncés, obtenu {len(enonces)}"


@pytest.mark.unit
def test_parse_mor_tier_premier_enonce_contient_tokens() -> None:
    """Le 1er énoncé contient les tokens det|le, n|chat, v|manger-PRES&3S."""
    from app.models.clan_wrapper import parse_mor_tier

    texte = SAMPLE_CHA.read_text(encoding="utf-8")
    enonces = parse_mor_tier(texte)
    premier = enonces[0]
    assert "det|le" in premier
    assert "n|chat" in premier
    assert len(premier) == 3, f"Attendu 3 tokens dans le 1er énoncé, obtenu {len(premier)}"


@pytest.mark.unit
def test_parse_mor_tier_troisieme_enonce_un_token() -> None:
    """Le 3e énoncé (maman) ne contient qu'un seul token n|maman."""
    from app.models.clan_wrapper import parse_mor_tier

    texte = SAMPLE_CHA.read_text(encoding="utf-8")
    enonces = parse_mor_tier(texte)
    assert enonces[2] == ["n|maman"], f"Attendu ['n|maman'], obtenu {enonces[2]}"


@pytest.mark.unit
def test_parse_mor_tier_ponctuation_absente() -> None:
    """La ponctuation (.) ne doit jamais apparaître comme token."""
    from app.models.clan_wrapper import parse_mor_tier

    texte = SAMPLE_CHA.read_text(encoding="utf-8")
    enonces = parse_mor_tier(texte)
    for i, enonce in enumerate(enonces):
        for token in enonce:
            assert "|" in token, (
                f"Énoncé {i}, token '{token}' : tout token doit contenir '|'"
            )
        assert "." not in enonce, f"Ponctuation trouvée dans l'énoncé {i}"


@pytest.mark.unit
def test_parse_mor_tier_exclut_xxx() -> None:
    """Un énoncé %mor contenant 'xxx' est exclu (0 énoncé valide)."""
    from app.models.clan_wrapper import parse_mor_tier

    cha_xxx = "@UTF8\n@Begin\n*CHI:\txxx .\n%mor:\txxx .\n@End\n"
    enonces = parse_mor_tier(cha_xxx)
    assert enonces == [], f"Attendu [], obtenu {enonces}"


@pytest.mark.unit
def test_parse_mor_tier_sans_mor_retourne_vide() -> None:
    """Un fichier .cha sans aucun tier %mor retourne une liste vide."""
    from app.models.clan_wrapper import parse_mor_tier

    cha_sans_mor = "@UTF8\n@Begin\n*CHI:\tle chat mange .\n@End\n"
    assert parse_mor_tier(cha_sans_mor) == []


@pytest.mark.unit
def test_compute_mlu_morphemes_sample() -> None:
    """compute_mlu_morphemes(sample_fra.cha) doit retourner ~2.667 (oracle déterministe)."""
    from app.models.clan_wrapper import compute_mlu_morphemes

    mlu = compute_mlu_morphemes(str(SAMPLE_CHA))
    # Vérification exacte contre l'oracle
    assert mlu == ORACLE_MLU, f"Attendu {ORACLE_MLU}, obtenu {mlu}"
    # Vérification de plausibilité (D-08)
    assert 2.0 <= mlu <= 3.5, f"MLU hors plage de plausibilité [2.0, 3.5] : {mlu}"


@pytest.mark.unit
def test_compute_mlu_morphemes_aucun_enonce() -> None:
    """Un .cha sans tier %mor valide doit lever ValueError."""
    from app.models.clan_wrapper import compute_mlu_morphemes

    import tempfile, os

    cha_vide = "@UTF8\n@Begin\n*CHI:\tle chat mange .\n@End\n"
    fd, tmp = tempfile.mkstemp(suffix=".cha")
    try:
        os.close(fd)
        Path(tmp).write_text(cha_vide, encoding="utf-8")
        with pytest.raises(ValueError, match="Aucun énoncé valide"):
            compute_mlu_morphemes(tmp)
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Tests unitaires — find_clan_mor + run_mor (mock subprocess, CI-safe)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_find_clan_mor_retourne_une_chaine() -> None:
    """find_clan_mor() doit toujours retourner une chaîne non vide."""
    from app.models.clan_wrapper import find_clan_mor

    resultat = find_clan_mor()
    assert isinstance(resultat, str)
    assert len(resultat) > 0


@pytest.mark.unit
def test_find_clan_mor_contient_pattern_frozen() -> None:
    """find_clan_mor doit utiliser getattr(sys, 'frozen', False) (preuve du pattern find_ffmpeg)."""
    import inspect
    import app.models.clan_wrapper as module

    source = inspect.getsource(module.find_clan_mor)
    assert "frozen" in source, "find_clan_mor doit tester sys.frozen"


@pytest.mark.unit
def test_run_mor_args_liste_pas_shell(mocker) -> None:
    """run_mor doit construire une liste d'arguments et ne jamais utiliser shell=True."""
    from app.models.clan_wrapper import run_mor

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

    run_mor(
        cha_path="test.cha",
        grammar_dir="/some/fra",
        mor_bin="/fake/mor",
    )

    call_args, call_kwargs = mock_run.call_args
    # Les args doivent être une liste (jamais une chaîne shell)
    args_passed = call_args[0]
    assert isinstance(args_passed, list), "run_mor doit passer une liste, pas une chaîne"
    assert "/fake/mor" in args_passed, "Le binaire mor doit figurer dans les args"
    # shell=True interdit (T-01-07)
    assert call_kwargs.get("shell", False) is False, "shell=True est interdit"
    # encoding UTF-8 obligatoire (T-01-09, Pitfall 2)
    assert call_kwargs.get("encoding") == "utf-8", "encoding='utf-8' obligatoire"


@pytest.mark.unit
def test_run_mor_leve_runtime_error_si_echec(mocker) -> None:
    """run_mor doit lever RuntimeError si le returncode != 0."""
    from app.models.clan_wrapper import run_mor

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = mocker.Mock(returncode=1, stdout="", stderr="échec mor")

    with pytest.raises(RuntimeError, match="mor a échoué"):
        run_mor(cha_path="test.cha", grammar_dir="/some/fra", mor_bin="/fake/mor")


# ---------------------------------------------------------------------------
# Test d'intégration — MLU vs oracle MTLN (gated : requiert binaire mor)
# ---------------------------------------------------------------------------


_mor_disponible = shutil.which("mor") is not None


@pytest.mark.integration
@pytest.mark.skipif(not _mor_disponible, reason="Binaire 'mor' absent du PATH — test sauté en CI")
def test_mlu_morphemes_vs_oracle(tmp_path: Path) -> None:
    """MLU calculée sur mtln_sample.cha après run_mor doit être dans la plage normative ±0.5.

    Enfant : 30 mois. MLU-morphèmes MTLN normative : 3.02 (Parisse & Le Normand 2002).
    Plage acceptée : [2.52, 3.52].
    """
    from app.models.clan_wrapper import compute_mlu_morphemes, find_clan_mor, run_mor

    # Pitfall 3 : travailler sur une copie, jamais sur la fixture originale
    copie = tmp_path / "mtln_sample.cha"
    copie.write_text(MTLN_CHA.read_text(encoding="utf-8"), encoding="utf-8")

    grammar_dir = shutil.which("mor")  # le binaire est dans son répertoire d'install
    # On suppose que la grammaire FR est configurée via MORLIB ou dans le répertoire par défaut
    run_mor(str(copie), grammar_dir=str(Path(grammar_dir).parent / "fra"))

    mlu = compute_mlu_morphemes(str(copie))
    assert (
        MLU_M_ATTENDUE - MLU_TOLERANCE <= mlu <= MLU_M_ATTENDUE + MLU_TOLERANCE
    ), (
        f"MLU {mlu:.3f} hors de la plage normative "
        f"[{MLU_M_ATTENDUE - MLU_TOLERANCE}, {MLU_M_ATTENDUE + MLU_TOLERANCE}] "
        f"pour un enfant de 30 mois (D-08)"
    )
