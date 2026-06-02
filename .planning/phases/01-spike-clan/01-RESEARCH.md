# Phase 1: Spike CLAN - Research

**Researched:** 2026-06-02
**Domain:** CLAN/TalkBank binaries (Windows), MOR French grammar, CHILDES corpus oracle, parsing %mor tier
**Confidence:** MEDIUM — licence vérifiée HIGH, invocation CLI MEDIUM (documentation officielle partielle), parsing %mor MEDIUM (format connu, détails fins à confirmer sur le fichier fra grammar)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Valider CLAN + `mor` sur **Windows d'abord** (plateforme primaire de dev et cible des orthophonistes).
- **D-02:** Tester la build CLAN qui fournit la commande `mor` sur Windows (CLANWin / Windows-CLAN selon disponibilité de `mor`).
- **D-03:** L'échantillon de référence est un **`.cha` issu du corpus French CHILDES avec MLU documentée/publiée**.
- **D-04:** La validation compare la MLU morphèmes calculée par notre parsing à la MLU de référence de cet échantillon.
- **D-05:** Le code du spike est une **amorce réutilisable pour la Phase 2** : appel `mor` en sous-process + parsing du tier `%mor` écrits proprement, en suivant le pattern `operation_fichier.find_ffmpeg`.
- **D-06:** Seule l'exploration de la licence et les essais en ligne de commande exploratoires peuvent rester jetables ; le bout « appel `mor` + parsing → MLU » doit être propre.
- **D-07:** **Strict sur la licence** : Go uniquement si redistribution binaires CLAN + grammaire MOR FR **totalement libre**, compatible MIT/commercial sans restriction bloquante.
- **D-08:** **Souple sur la métrique** : MLU « plausible et explicable », pas exacte au centième.

### Claude's Discretion

- Choix exact du `.cha` CHILDES FR de référence parmi les corpus avec MLU publiée.
- Forme précise du rapport de spike (Markdown dans le répertoire de phase).
- Détails d'implémentation du wrapper subprocess (gestion des chemins, encodage de la sortie CLAN).
- Stratégie de repli précise si No-Go.

### Deferred Ideas (OUT OF SCOPE)

- Format précis et gabarit du rapport de spike.
- Stratégies de repli si No-Go (demande de permission écrite à TalkBank, ré-implémentation MOR-lite via Démonette/UD, amélioration de l'heuristique existante) — à documenter dans le rapport de spike lui-même.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SPIKE-01 | Vérifier que la licence CLAN/TalkBank autorise la redistribution des binaires CLAN | Licence BSD-3 vérifiée sur GitHub TalkBank/Windows-CLAN — voir §Licence CLAN |
| SPIKE-02 | Appeler `mor` avec la grammaire MOR française en CLI sur un `.cha` de test et obtenir le tier `%mor` | Syntaxe CLI documentée dans §Invocation `mor` ; installation Windows documentée |
| SPIKE-03 | Parser la sortie CLAN (`%mor` + `mlu`) et valider une MLU en morphèmes sur un échantillon de référence | Corpus MTLN identifié comme oracle ; format `%mor` documenté dans §Parsing `%mor` |
</phase_requirements>

---

## Summary

CLAN (Windows-CLAN) est distribué sous **BSD-3-Clause** par TalkBank. La redistribution de binaires est explicitement autorisée, compatible avec un projet MIT. La grammaire MOR française, développée par Christophe Parisse et Brian MacWhinney, est hébergée sur les serveurs TalkBank (`talkbank.org/morgrams/`) et téléchargeable sous forme de ZIP (`fra.zip`). Sa licence propre n'est pas documentée sur la page officielle — c'est la principale zone d'ombre du critère D-07. Une confirmation directe auprès de TalkBank ou de Parisse est recommandée en début de spike.

L'exécution de `mor` depuis la ligne de commande Windows est possible mais comporte une ambiguïté : la documentation officielle décrit essentiellement un workflow GUI (bouton "mor lib" dans la fenêtre Commands). Toutefois, CLAN inclut `mor` comme commande du CLI interne (les commandes comme `freq`, `mor`, `mlu` sont invoquables sans GUI), et la communauté confirme l'usage batch. Le spike doit confirmer la syntaxe exacte sur Windows. Une alternative Python officielle existe — **Batchalign2** (TalkBank, BSD-3, PyPI) — qui wrape les analyses CLAN/UD via Stanza mais ne remplace pas le `mor` classique avec grammaire Parisse.

L'oracle de validation recommandé est le corpus **MTLN** (Le Normand, 1990 ; CHILDES français), avec les valeurs de MLU publiées par la littérature : MLU-m entre 1,86 (24 mois) et 4,82 (48 mois). Ces chiffres sont vérifiables et cités dans un article PMC peer-reviewed.

**Recommandation primaire :** Go — si la grammaire MOR FR est confirmée libre à redistribuer (vérification email ou GitHub Issue à faire en Wave 0 du spike).

---

## Project Constraints (from CLAUDE.md)

| Directive | Implication pour ce spike |
|-----------|--------------------------|
| Python 3.12+ obligatoire | Le wrapper subprocess doit être compatible 3.12 ; pas de walrus operator < 3.8, etc. |
| Offline/RGPD — zéro cloud | Le corpus CHILDES MTLN est public (pas de données patient) ; le spike peut logger les valeurs calculées |
| MIT — dépendances embarquées | La BSD-3 CLAN est compatible MIT. La grammaire MOR FR doit être vérifiée séparément |
| Gate couverture 80 % sur modules métier | Le code amorce (appel subprocess + parsing) doit être testable dès Phase 2 ; pour le spike, viser isolation propre |
| RGPD : ne jamais logger de texte patient | Non applicable ici — le corpus CHILDES est public |
| Pattern `find_ffmpeg` à réutiliser | `find_clan_mor()` suit la même séquence : frozen `_MEIPASS` → vendored `bin/` → PATH → littéral |
| Docstrings en français | Appliquer au code amorce |
| `subprocess` déjà utilisé dans le projet | Cohérence avec `audio_worker.py` et `operation_fichier.py` |

---

## Licence CLAN (SPIKE-01)

### Windows-CLAN

**Verdict : BSD-3-Clause — redistribution binaire AUTORISÉE** [VERIFIED: github.com/TalkBank/Windows-CLAN/blob/master/LICENSE]

- Copyright : 1990-2024 TalkBank WinCLAN
- Redistribution source et binaire autorisée avec ou sans modification
- Conditions : (1) conserver le copyright notice dans le source, (2) reproduire le copyright dans la documentation des binaires redistribués, (3) ne pas utiliser le nom TalkBank pour promouvoir des produits dérivés sans permission écrite
- Aucune restriction non-commercial, aucune copyleft
- Compatible MIT dans un projet commercial

**Compatibilité D-07 :** GO pour le binaire CLAN lui-même.

### OSX-CLAN

**Verdict : BSD-3-Clause identique** [VERIFIED: github.com/TalkBank/OSX-CLAN]

### Grammaire MOR française (fra.zip)

**Verdict : INCERTAIN — licence non documentée publiquement** [ASSUMED]

- Développée par Christophe Parisse (CNRS/MoDyCo, Université Paris Nanterre) et Brian MacWhinney (CMU) [CITED: talkbank.org/0info/mor/index.html]
- Hébergée sur `talkbank.org/morgrams/fra.zip` [VERIFIED: talkbank.org/0info/mor/index.html]
- La page officielle ne mentionne aucune licence explicite
- Parisse a contribué la grammaire française au projet TalkBank/CHILDES (projet NIH, open science)
- Aucun avertissement "non-commercial" ou restriction visible dans les publications associées

**Action requise en Wave 0 :** Ouvrir un GitHub Issue sur TalkBank/Windows-CLAN ou envoyer un email à macw@cmu.edu en demandant : "Can the French MOR grammar (fra.zip) be redistributed in binary/data form inside a MIT-licensed desktop application?" Si pas de réponse en 5 jours ouvrés → vérifier si les fichiers `.cut` / `.lex` du grammar contiennent un header de licence.

**Compatibilité D-07 :** À confirmer. Le spike PEUT procéder techniquement (SPIKE-02, SPIKE-03) en parallèle, mais la conclusion Go/No-Go officielle sur SPIKE-01 attend cette confirmation.

---

## Standard Stack

### Core

| Composant | Version | Rôle | Source |
|-----------|---------|------|--------|
| CLANWin (Windows-CLAN) | V 01-May-2026 | Suite d'analyse CHAT, inclut `mor`, `mlu`, `freq`, `check` | [VERIFIED: dali.talkbank.org/clan/] |
| Grammaire MOR FR (fra.zip) | 2009+ (Parisse) | Lexique et règles morphologiques pour l'annotation `%mor` en français | [VERIFIED: talkbank.org/0info/mor/index.html] |
| Python 3.12 | ≥3.12 | Wrapper subprocess + parsing | [VERIFIED: pyproject.toml] |
| `subprocess` (stdlib) | N/A | Appel `mor` headless | [VERIFIED: pattern existant dans audio_worker.py] |
| `re` (stdlib) | N/A | Parsing du tier `%mor` | [ASSUMED] |

### Alternatives Considérées

| Standard recommandé | Alternative | Pourquoi rejeté |
|--------------------|-------------|-----------------|
| CLANWin + grammaire Parisse | **Batchalign2** (TalkBank, BSD-3, PyPI) | Batchalign2 utilise Stanford Stanza pour UD tagging — ce n'est pas la grammaire MOR de Parisse. Compatible pour UD, mais ne répond pas à la question du spike (validation de CLAN/MOR FR classique). À réévaluer si CLAN No-Go. |
| CLANWin + grammaire Parisse | Heuristique existante Analyse_NLTK | Fragile, non standard — c'est précisément ce qu'on cherche à remplacer |

---

## Architecture Patterns

### Pattern de résolution de binaire CLAN (`find_clan_mor`)

Calqué sur `find_ffmpeg` existant (`app/models/operation_fichier.py:70`). Structure recommandée :

```python
# Source: app/models/operation_fichier.py:70 (pattern existant)
def find_clan_mor() -> str:
    """Retourne le chemin vers le binaire mor de CLAN.

    Ordre de résolution :
      1. Bundle PyInstaller (frozen) -> _internal/clan/mor
      2. Vendored -> app/../bin/clan/mor (layout dev)
      3. PATH système (CLAN installé globalement)
      4. Fallback littéral 'mor' (lève CalledProcessError si absent)
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
        return os.path.abspath(os.path.join(base, '_internal', 'clan', 'mor'))

    vendored = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'bin', 'clan', 'mor')
    )
    if os.path.isfile(vendored):
        return vendored

    system = shutil.which('mor')
    if system:
        return system

    return 'mor'
```

Sur Windows, le binaire s'appelle `mor.exe` — `shutil.which('mor')` le trouve si CLANWin est dans PATH.

### Pattern d'appel subprocess `mor`

```python
# [ASSUMED] — à confirmer par les essais CLI du spike
import subprocess, os, pathlib

def run_mor(cha_path: str, grammar_dir: str, mor_bin: str = 'mor') -> str:
    """Appelle mor sur un fichier .cha et retourne le chemin du fichier annoté.

    Args:
        cha_path: Chemin absolu vers le fichier .cha d'entrée
        grammar_dir: Chemin vers le répertoire de la grammaire française (fra/)
        mor_bin: Chemin vers l'exécutable mor (résolu par find_clan_mor)

    Returns:
        Chemin du fichier .cha annoté (même nom, mor écrit directement dedans avec +1)
    """
    env = os.environ.copy()
    env['MORLIB'] = grammar_dir  # variable d'environnement lue par mor [ASSUMED]

    result = subprocess.run(
        [mor_bin, '+l', grammar_dir, '+1', cha_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"mor failed: {result.stderr}")
    return cha_path  # mor +1 écrit dans le fichier d'entrée (overwrite)
```

**Note critique :** La syntaxe exacte des flags (`+l grammar_dir` vs variable d'environnement `MORLIB` vs bouton GUI) est la principale incertitude CLI. Le spike doit explorer les deux approches en Wave 1. La documentation officielle indique que CLAN stocke le chemin MORLIB dans ses préférences GUI — pour une invocation headless, tester `MORLIB=<path> mor *.cha` depuis PowerShell.

### Format du tier `%mor`

Structure d'un fichier `.cha` après passage par `mor` :

```
@UTF8
@Begin
@Languages: fra
@Participants: CHI Child, MOT Mother
*CHI: le chat mange .
%mor: det|le n|chat v|manger-PRES3S .
*CHI: il veut du lait .
%mor: pro|il v|vouloir-PRES3S det:part|de+det|le n|lait .
@End
```

**Règles de notation `%mor`** [CITED: talkbank.org/0info/manuals/CLAN.html ; MEDIUM confidence] :
- Format : `POS|lemme-morphèmes` séparés par espaces
- `~` (tilde) : clitiques ou liaisons morphémiques (ex : `v|aller~pro|y`)
- `+` (plus) : fusion de mots (ex : `det:part|de+det|le` pour "du")
- Les frontières de morphèmes sont comptées pour la MLU
- Ponctuation (`.`, `?`, `!`) : non comptée dans les morphèmes
- Codes `xxx`, `yyy`, `www` : exclus du calcul MLU

### Algorithme de calcul de la MLU morphèmes depuis `%mor`

```python
import re
from pathlib import Path

# [ASSUMED] — basé sur les règles CLAN documentées (Brown, 1973 adapté CLAN)
_MOR_TOKEN = re.compile(r'\S+\|\S+')  # POS|lemme ou POS|lemme-morph
_EXCLUDED = {'xxx', 'yyy', 'www', '0'}

def compute_mlu_morphemes(cha_path: str) -> float:
    """Calcule la MLU en morphèmes depuis un fichier .cha annoté par mor.

    Méthode CLAN : compte les tokens POS|lemme sur les lignes %mor,
    en excluant les énoncés avec xxx/yyy/www et la ponctuation.
    """
    total_morphemes = 0
    total_utterances = 0
    in_mor_tier = False

    for line in Path(cha_path).read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line.startswith('%mor:'):
            mor_content = line[5:].strip()
            # Exclure les énoncés marqués xxx/yyy/www
            if any(tok in mor_content.split() for tok in _EXCLUDED):
                continue
            # Compter les tokens morphémiques (tout token contenant |)
            tokens = _MOR_TOKEN.findall(mor_content)
            if tokens:
                total_morphemes += len(tokens)
                total_utterances += 1

    if total_utterances == 0:
        raise ValueError("Aucun énoncé valide trouvé dans le tier %mor")
    return round(total_morphemes / total_utterances, 3)
```

**Note :** Le comptage exact des morphèmes infléchis (ex : `-PRES3S` = 1 morphème supplémentaire ?) varie selon les conventions. La version CLAN compte chaque token `POS|...` comme 1 unité morphologique minimale — les suffixes après `-` sont inclus dans le même token. Vérifier avec le manuel CLAN §MLU. D-08 autorise un écart raisonnable.

---

## Oracle de Validation (SPIKE-03)

### Corpus recommandé : MTLN (Le Normand, 1990)

| Propriété | Valeur |
|-----------|--------|
| Corpus | CHILDES French MTLN |
| Créateur | Marie-Thérèse Le Normand (Univ. Paris Descartes) + Christophe Parisse |
| URL | talkbank.org/childes/access/French/MTLN.html |
| Téléchargement | `data/childes/French/MTLN?f=zip` |
| Participants | 56 enfants, âge 2;0–4;0, corpus naturaliste 1990 |
| Statut `%mor` | Non confirmé dans la page corpus — à vérifier en téléchargeant. Le corpus est annoté MOR par Parisse selon les publications associées. |
| Accès | Public, téléchargement zip disponible sans inscription |

### Valeurs MLU de référence publiées (oracle D-03/D-04)

Source : Parisse & Le Normand (2002), large étude sur 315 enfants francophones 2–4 ans, données MTLN. [VERIFIED: pmc.ncbi.nlm.nih.gov/articles/PMC8752861/ cite ces valeurs, HIGH confidence pour les chiffres]

| Âge (mois) | MLU-mots | MLU-morphèmes |
|------------|----------|---------------|
| 24 | 1,60 | 1,86 |
| 27 | 2,11 | 2,50 |
| 30 | 2,52 | 3,02 |
| 33 | 3,30 | 3,97 |
| 36 | 3,38 | 4,09 |
| 39 | 3,57 | 4,30 |
| 42 | 3,74 | 4,49 |
| 45 | 3,91 | 4,72 |
| 48 | 4,01 | 4,82 |

**Utilisation pour le spike :** Sélectionner un fichier `.cha` du sous-corpus MTLN correspondant à un enfant d'un groupe d'âge connu. Calculer la MLU avec notre script. Comparer à la plage normative de l'âge. Per D-08, un résultat dans la plage ±0,5 est satisfaisant ; tout résultat plausible et explicable est suffisant.

### Corpus alternatifs (si MTLN ne contient pas de tier `%mor`)

| Corpus | Avantage | Inconvénient |
|--------|----------|--------------|
| Lyon (Demuth & Tremblay) | Longitudinal, bien documenté | MLU par fichier non publiée globalement |
| Leveillé (Suppes & Leveillé, 1973) | Longitudinal, un seul enfant (Philippe, 25–39 mois) | Âge très précoce, MLU basse, pas de valeur publiée par fichier |
| York (Plunkett & De Cat) | Enfants bilingues / L1 | Contextes mixtes, moins idéal pour validation |

**Recommandation :** Si MTLN n'a pas de `%mor` pre-annoté, utiliser un fichier MTLN pour faire tourner `mor` FR dessus, puis comparer la MLU calculée à la plage normative du groupe d'âge correspondant.

---

## Don't Hand-Roll

| Problème | Ne pas construire | Utiliser | Pourquoi |
|----------|-------------------|----------|---------|
| Analyse morphologique française | Heuristique JSON + stemmer (existant) | CLAN `mor` + grammaire Parisse | Fragile, non standard, non citable |
| Parsing CHAT | Parser custom from scratch | Regex ciblé sur `%mor:` + `*CHI:` | CHAT est du texte structuré simple ; un parser complet (pylangacq) ajoute une dépendance pour un bénéfice limité au spike |
| MLU depuis %mor | Algorithme custom complexe | Commande `mlu` de CLAN (ou parsing Python simple) | `mlu` de CLAN produit directement la MLU ; le script Python n'est qu'un oracle de validation |

**Note sur pylangacq :** Il existe une bibliothèque Python `pylangacq` (MIT, PyPI) qui parse les fichiers CHAT. Elle est utile pour Phase 2 mais inutile pour ce spike dont la valeur est précisément de valider l'appel CLAN natif.

---

## Invocation `mor` sur Windows

### Installation CLANWin

1. Télécharger le programme d'installation depuis `dali.talkbank.org/clan/` (lien `clanwin.exe`)
2. Installer via InstallShield → installe dans `C:\TalkBank\CLAN\` par défaut
3. Télécharger la grammaire française : dans CLAN GUI → File → Get MOR Grammar → French → installe dans `C:\TalkBank\CLAN\fra\`
4. Vérifier que `C:\TalkBank\CLAN\` est dans le PATH Windows (à configurer manuellement ou à passer en chemin absolu dans le subprocess)

[CITED: dali.talkbank.org/clan/ ; MEDIUM confidence pour les chemins exacts]

### Commande CLI (à confirmer par le spike)

```powershell
# Approche 1 : variable d'environnement MORLIB + flags
$env:MORLIB = "C:\TalkBank\CLAN\fra"
mor +1 sample.cha

# Approche 2 : flag +l pour spécifier le grammar dir
mor +l "C:\TalkBank\CLAN\fra" +1 sample.cha

# Approche 3 : se placer dans le dossier de la grammaire
cd "C:\TalkBank\CLAN"
mor +1 "D:\ortholyse\tests\fixtures\sample_fra.cha"
```

**Incertitude principale :** La documentation CLAN insiste sur le bouton "mor lib" de l'interface GUI pour configurer MORLIB. Pour un usage headless (subprocess Python), la question est : `mor` lit-il `MORLIB` depuis une variable d'environnement, depuis un fichier de config CLAN (`~/.clanrc` ou équivalent Windows), ou exige-t-il d'être lancé depuis un répertoire spécifique ? Le changelog indique que `mor` existe en mode batch (ligne `2018-10-25: Commands: changed batch command`) — confirmer la syntaxe exacte est le SPIKE-02 lui-même.

### Vérification rapide (to-do Wave 1 du spike)

```powershell
# Test minimal — produit-il un tier %mor dans sample_fra.cha ?
cd "D:\ortholyse\tests\fixtures"
$env:MORLIB = "C:\TalkBank\CLAN\fra"
& "C:\TalkBank\CLAN\mor.exe" +1 sample_fra.cha
Select-String "%mor" sample_fra.cha
```

---

## Common Pitfalls

### Pitfall 1 : MORLIB non trouvé en mode headless

**Ce qui se passe :** `mor` se lance mais produit des tokens non reconnus (`xxx` ou `0` sur tous les mots) parce qu'il ne trouve pas le répertoire de la grammaire.
**Cause :** CLAN stocke le chemin MORLIB dans ses préférences GUI (Windows Registry ou fichier `.clanrc`), pas dans une variable d'environnement standard.
**Comment éviter :** Tester d'abord en passant le chemin explicitement via `+l` flag. Si ce flag n'existe pas, passer via `MORLIB` env var. En dernier recours, pré-configurer CLAN GUI une fois et vérifier si le subprocess hérite des préférences.
**Signes d'alerte :** Fichier de sortie avec `%mor: xxx` sur tous les énoncés, ou `mor` qui s'exécute sans erreur mais ne produit aucun tier `%mor`.

### Pitfall 2 : Encodage Windows (cp1252 vs UTF-8)

**Ce qui se passe :** La sortie de `mor` ou le fichier `.cha` produit des caractères corrompus sur les accents français.
**Cause :** `mor.exe` peut produire du CP-1252 sur Windows ; `subprocess.run()` sans `encoding=` lit en bytes.
**Comment éviter :** Forcer `encoding='utf-8'` dans subprocess et vérifier que le fichier `.cha` commence par `@UTF8`.
**Signes d'alerte :** `UnicodeDecodeError` ou lettres accentuées (`é`, `à`) affichées comme `?` ou `Ã©`.

### Pitfall 3 : `mor +1` overwrite silencieux

**Ce qui se passe :** `mor +1 sample.cha` écrase le fichier d'entrée sans avertissement.
**Cause :** Le flag `+1` produit le fichier de sortie avec le même nom que l'entrée.
**Comment éviter :** Travailler sur une copie du fichier `.cha` de test (jamais l'original MTLN directement).
**Signes d'alerte :** Le fichier original disparaît.

### Pitfall 4 : Corpus MTLN sans `%mor` pré-existant

**Ce qui se passe :** Les fichiers MTLN sont téléchargés mais ne contiennent pas de tier `%mor`.
**Cause :** Tous les corpus CHILDES n'ont pas été annotés MOR. Le statut `%mor` du MTLN n'est pas confirmé dans la documentation.
**Comment éviter :** Télécharger un fichier MTLN, vérifier si `%mor` est présent. Si absent, cela confirme que le spike DOIT faire tourner `mor` lui-même — ce qui est même plus représentatif de l'usage réel.
**Signes d'alerte :** `grep %mor sample.cha` ne retourne rien.

### Pitfall 5 : Windows-CLAN n'est que du code source — pas d'installeur pré-compilé

**Ce qui se passe :** On cherche un `mor.exe` précompilé dans le repo GitHub et on ne le trouve pas.
**Cause :** `github.com/TalkBank/Windows-CLAN` contient le **code source C++**, pas les binaires compilés. L'installeur est séparé.
**Comment éviter :** Télécharger `clanwin.exe` depuis `dali.talkbank.org/clan/`, pas depuis GitHub.
**Signes d'alerte :** Le repo GitHub ne contient que `.cpp` / `.sln` sans dossier `Release/`.

### Pitfall 6 : Licence de la grammaire MOR FR non confirmée avant redistribution

**Ce qui se passe :** On embarque `fra/` dans le bundle de l'app avant d'avoir confirmation légale.
**Cause :** La licence de la grammaire n'est pas documentée publiquement sur talkbank.org.
**Comment éviter :** Confirmation email/GitHub Issue en Wave 0 du spike, avant toute décision de redistribution.

---

## Environment Availability

| Dépendance | Requise par | Disponible | Version | Fallback |
|------------|------------|------------|---------|----------|
| Python 3.12+ | Wrapper subprocess + parsing | ✓ | 3.13.7 (> min requis) | — |
| pytest + pytest-cov | Gate couverture 80 % | ✓ | pytest 9.0.2 | — |
| CLANWin (clanwin.exe) | SPIKE-02 | ✗ (à installer) | V 01-May-2026 | — |
| Grammaire MOR FR (fra.zip) | SPIKE-02, SPIKE-03 | ✗ (à télécharger) | 2009+ Parisse | — |
| Corpus CHILDES MTLN (.cha) | SPIKE-03 | ✗ (à télécharger) | 1990 | Lyon, Leveillé |
| Internet (téléchargement initial) | Installation CLAN + grammaire + corpus | ✓ (supposé) | — | N/A (une fois téléchargé, tout est local) |

**Dépendances bloquantes sans fallback :**
- CLANWin doit être installé (téléchargement depuis `dali.talkbank.org/clan/`)
- Grammaire MOR FR `fra.zip` doit être téléchargée (depuis `talkbank.org/morgrams/` via CLAN GUI ou direct)
- Corpus MTLN doit être téléchargé (depuis `talkbank.org/childes/access/French/MTLN.html`)

**Ces dépendances ne sont nécessaires QUE pour le spike**, pas pour la CI. Les tests du spike peuvent être `pytest.mark.manual` ou conditionnels sur la présence des binaires.

---

## Validation Architecture

### Cadre de test

| Propriété | Valeur |
|-----------|--------|
| Framework | pytest 9.0.2 |
| Config | `pyproject.toml [tool.pytest.ini_options]` |
| Commande rapide | `rtk pytest tests/test_spike_clan.py -x` |
| Suite complète | `rtk pytest --cov` (gate 80 %) |

### Mapping requirements → tests

| Req ID | Comportement | Type | Commande | Fichier |
|--------|-------------|------|----------|---------|
| SPIKE-01 | Lecture du fichier LICENSE Windows-CLAN → extrait "BSD-3-Clause" | unit | `pytest tests/test_spike_clan.py::test_clan_license_is_bsd3 -x` | ❌ Wave 0 |
| SPIKE-02 | `run_mor("sample_fra.cha", grammar_dir)` produit un tier `%mor` | integration | `pytest tests/test_spike_clan.py::test_mor_produces_mor_tier -x` | ❌ Wave 0 |
| SPIKE-03 | `compute_mlu_morphemes("mtln_sample.cha")` retourne une valeur dans [1.5, 5.5] | integration | `pytest tests/test_spike_clan.py::test_mlu_plausible_range -x` | ❌ Wave 0 |
| SPIKE-03 | `compute_mlu_morphemes` sur un fichier de référence mini-manuel | unit | `pytest tests/test_spike_clan.py::test_mlu_known_sample -x` | ❌ Wave 0 |

Les tests SPIKE-02 et SPIKE-03 nécessitent CLANWin + grammaire installés — marquer `@pytest.mark.integration` et les conditionner sur un flag `--run-clan-integration` ou sur la présence de `mor.exe` dans PATH. Les tests unitaires (parsing pur) tournent en CI sans CLAN.

### Wave 0 Gaps

- [ ] `tests/test_spike_clan.py` — couvre SPIKE-01, SPIKE-02, SPIKE-03 (avec fixtures intégrées)
- [ ] `tests/fixtures/sample_fra.cha` — fichier `.cha` minimal en français pour test unitaire du parsing
- [ ] `app/models/clan_wrapper.py` — module amorce (find_clan_mor, run_mor, compute_mlu_morphemes)

---

## State of the Art

| Ancienne approche | Approche actuelle | Quand changé | Impact |
|------------------|-------------------|--------------|--------|
| Grammaire MOR FR contributée par Parisse (TalkBank FTP) | Disponible via CLAN GUI "File > Get MOR Grammar > French" | 2024-09-13 (changelog) | Installation simplifiée |
| Batchalign legacy | Batchalign2 (Python, BSD-3, PyPI) | 2023+ | Alternative Python officielle si No-Go CLAN |
| Analyse UD pour CHILDES : email à macw@cmu.edu | UD tagging via Batchalign2 / Stanza pour 28 langues dont FR | 2024 | Complément UD disponible sans CLAN |

---

## Assumptions Log

| # | Claim | Section | Risque si faux |
|---|-------|---------|----------------|
| A1 | La grammaire MOR française `fra.zip` est librement redistribuable (pas de licence restrictive) | §Licence CLAN | BLOQUANT : si licence non-commercial ou restrictive → No-Go D-07, changement de stratégie moteur |
| A2 | `mor` accepte un flag `+l <grammar_dir>` ou lit la variable d'environnement `MORLIB` en mode headless | §Invocation `mor` | Impact technique : si headless impossible, nécessite une approche alternative (wrapper COM, pré-configuration registry) |
| A3 | Les fichiers MTLN disponibles en téléchargement contiennent des énoncés enfants annotables par `mor` (format CHAT standard) | §Oracle | Mineur (D-08) : si MTLN est incomplet, utiliser un autre corpus French CHILDES |
| A4 | `compute_mlu_morphemes` compte chaque token `POS|...` comme 1 unité (sans décomposer les suffixes après `-`) | §Architecture Patterns | Mineur (D-08) : écart de MLU corrigeable en Phase 2 |
| A5 | CLANWin installe `mor.exe` dans `C:\TalkBank\CLAN\` et ce chemin est ajouté au PATH | §Invocation | Mineur : le chemin exact peut différer ; à résoudre avec `shutil.which()` |

---

## Open Questions

1. **Licence de la grammaire MOR française**
   - Ce qu'on sait : développée par Parisse + MacWhinney, hébergée sur TalkBank, utilisée dans des projets académiques open science
   - Ce qui est flou : aucune licence explicite dans la page de téléchargement
   - Recommandation : email à macw@cmu.edu ou GitHub Issue avant de conclure Go sur SPIKE-01. En attendant, le spike technique peut avancer.

2. **Syntaxe headless de `mor` sur Windows**
   - Ce qu'on sait : `mor` est une commande CLAN invocable (pas seulement via GUI), `MORLIB` est le répertoire de la grammaire
   - Ce qui est flou : le flag CLI exact pour passer `MORLIB` sans GUI (`+l`, `MORLIB=`, config file)
   - Recommandation : Wave 1 du spike = session exploratoire PowerShell, tester les 3 approches documentées ci-dessus

3. **Présence de `%mor` dans les fichiers MTLN**
   - Ce qu'on sait : le corpus a été annoté par Parisse selon les publications associées
   - Ce qui est flou : si les fichiers zip disponibles publiquement contiennent le tier `%mor` ou seulement les transcriptions brutes
   - Recommandation : télécharger un fichier MTLN en Wave 1 et inspecter avant de construire les tests oracle

---

## Sources

### Primaires (HIGH confidence)

- [TalkBank/Windows-CLAN LICENSE](https://github.com/TalkBank/Windows-CLAN/blob/master/LICENSE) — BSD-3-Clause vérifié
- [TalkBank/OSX-CLAN](https://github.com/TalkBank/OSX-CLAN) — BSD-3-Clause identique
- [talkbank.org/0info/mor/index.html](https://talkbank.org/0info/mor/index.html) — liste des langues UD, grammaire FR par Parisse + MacWhinney, lien fra.zip
- [pmc.ncbi.nlm.nih.gov/articles/PMC8752861/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8752861/) — valeurs MLU-m et MLU-w par âge pour enfants français (MTLN corpus)
- [dali.talkbank.org/clan/changes.txt](https://dali.talkbank.org/clan/changes.txt) — changelog CLAN confirmant ajout French dans "Get MOR Grammar" (2024-09-13)
- [talkbank.org/childes/access/French/MTLN.html](https://talkbank.org/childes/access/French/MTLN.html) — corpus MTLN, Le Normand 1990
- [dali.talkbank.org/clan/](https://dali.talkbank.org/clan/) — version actuelle CLAN, description CLANWin

### Secondaires (MEDIUM confidence)

- [talkbank.org/0info/manuals/CLAN.html](https://talkbank.org/0info/manuals/CLAN.html) — manuel CLAN (structure, commandes)
- [Frontiers — Language Sample Analysis With TalkBank](https://www.frontiersin.org/articles/10.3389/fcomm.2022.865498/full) — MOR 95-97% précision EN, French protocol disponible
- [talkbank.org/childes/access/French/](https://talkbank.org/childes/access/French/) — liste des 15 corpus français CHILDES
- [github.com/TalkBank/batchalign2](https://github.com/TalkBank/batchalign2) — alternative Python BSD-3

### Tertiaires (LOW confidence — à valider)

- Documentation CLAN sur syntaxe CLI `mor` (extrapolation à partir de guides GUI 2013-2016)
- Format `%mor` tier (reconstruction depuis publications, non lu dans le manuel officiel)

---

## Metadata

**Confidence breakdown :**
- Licence CLAN binaire : HIGH — BSD-3-Clause vérifié sur GitHub
- Licence grammaire MOR FR : LOW — non documentée publiquement (A1, action requise)
- Standard stack : HIGH — CLANWin + fra.zip bien identifiés
- Syntaxe CLI `mor` headless : MEDIUM — commande connue, flags exacts à confirmer (A2)
- Oracle MTLN + valeurs MLU : HIGH — peer-reviewed PMC
- Format `%mor` : MEDIUM — format documenté indirectement, exemples à valider

**Research date :** 2026-06-02
**Valid until :** 2026-07-02 (stable — CLAN sort des mises à jour mensuelles mais l'architecture est stable)
