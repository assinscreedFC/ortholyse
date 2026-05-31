**Lire en [English](./README.md) / [Français](./README.fr.md)**

# Ortholyse

Application desktop pour orthophonistes. Elle transcrit l'audio des séances avec Whisper et calcule des métriques syntaxiques sur le texte corrigé, en local.

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-41cd52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![Licence: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](./LICENSE)
[![CI](https://img.shields.io/badge/CI-pytest%20%2B%20coverage-success?style=flat-square)](.github/workflows/ci.yml)
[![Couverture](https://img.shields.io/badge/coverage-80%25%2B-brightgreen?style=flat-square)](.github/workflows/ci.yml)

> Conçu pour les clinicien-ne-s qui perdent des heures à transcrire des séances à la main. Ortholyse transforme un enregistrement en analyse structurée que vous pouvez corriger, valider et exporter.

## Table des matières

1. [À propos](#à-propos)
2. [Fonctionnalités](#fonctionnalités)
3. [Captures](#captures)
4. [Architecture](#architecture)
5. [Prérequis](#prérequis)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [Démarrage rapide](#démarrage-rapide)
9. [Utilisation](#utilisation)
10. [Développement](#développement)
11. [Tests et couverture](#tests-et-couverture)
12. [Feuille de route](#feuille-de-route)
13. [Contribuer](#contribuer)
14. [Licence](#licence)
15. [Remerciements](#remerciements)
16. [Lire l'article](#lire-larticle)
17. [Page projet](#page-projet)

## À propos

Les orthophonistes transcrivent régulièrement des séances patient pour calculer des métriques comme la longueur moyenne d'énoncé (LME), le nombre de morphèmes ou la complexité syntaxique. Le faire à la main sur une séance de 20 minutes peut prendre une heure complète, et les calculs sont sources d'erreurs.

Ortholyse fait passer l'enregistrement par Whisper pour la transcription, vous laisse corriger le texte avec une lecture synchronisée, puis calcule les métriques linguistiques avec Spacy et NLTK. Tout tourne en local sur la machine du praticien. Aucun envoi cloud, aucune donnée patient ne quitte le bureau.

**Pour qui :**

- Orthophonistes en cabinet libéral ou en milieu hospitalier
- Environnements cliniques francophones (le pipeline NLP est calibré pour le français, support anglais prévu)
- Chercheur-euse-s comparant des échantillons de parole entre cohortes de patients

## Fonctionnalités

- Transcription audio locale via OpenAI Whisper, sans appel cloud
- Enregistrement direct depuis le micro dans l'app
- Lecteur audio et éditeur de texte synchronisés pour une correction rapide
- Métriques linguistiques automatiques : nombre de mots, nombre d'énoncés, LME, complexité morphologique
- Export PDF combinant transcription et analyse
- Pipeline NLP français basé sur Spacy `fr_core_news_lg` et NLTK
- Interface desktop PySide6, tourne sous Windows, macOS et Linux

## Captures

Les captures seront ajoutées dans une prochaine version. L'application présente une barre latérale avec les vues principales (Accueil, Enregistrement, Import, Correction de transcription, Analyse, Paramètres).

## Architecture

```
+------------------+      +------------------+      +-------------------+
|  Capture audio   | ---> |  Whisper STT     | ---> |  Texte éditable   |
|  (UI PySide6)    |      |  (modèle local)  |      |  (lecture sync)   |
+------------------+      +------------------+      +-------------------+
                                                              |
                                                              v
                                                    +-------------------+
                                                    | Spacy + NLTK      |
                                                    | métriques ling.   |
                                                    +-------------------+
                                                              |
                                                              v
                                                    +-------------------+
                                                    | Export PDF        |
                                                    +-------------------+
```

Le code suit une séparation Vues / Contrôleurs / Modèles :

- `app/Views/` écrans Qt (Accueil, Enregistrement, Import, Transcription, Metrique, Paramètres)
- `app/Widgets/` widgets Qt réutilisables (AudioPlayer, AudioBar, Feuille)
- `app/controllers/` couche contrôleurs qui relie vues et modèles
- `app/models/` logique métier et IO :
  - `Analyse_NLTK.py` analyse linguistique (LME, morphèmes, pipeline Spacy + NLTK)
  - `exportation.py` export PDF et JSON
  - `operation_fichier.py` IO fichiers audio et détection de silence
  - `transcription.py` wrappers Whisper
  - `audio_worker.py`, `memo.py` enregistrement et capture live
- `app/assets/` polices, icônes, ressources JSON (suffixes, préfixes, settings)

## Prérequis

- Python 3.12 ou plus récent
- FFmpeg accessible à l'app (le code attend un binaire sous `bin/ffmpeg` relatif à `app/` ; sur un poste de dev, le plus simple est d'installer FFmpeg au niveau système et d'ajuster `find_ffmpeg()` dans `app/models/operation_fichier.py` si besoin)
- Environ 4 Go d'espace disque libre pour les modèles Whisper et Spacy
- Un micro fonctionnel si vous souhaitez enregistrer des séances dans l'app

## Installation

1. Cloner le dépôt :

   ```bash
   git clone https://github.com/assinscreedFC/ortholyse.git
   cd ortholyse
   ```

2. Créer un environnement virtuel :

   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate     # Windows
   source .venv/bin/activate     # macOS / Linux
   ```

3. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

   Cette étape installe PySide6, Whisper, torch, Spacy et les modèles Spacy français (`fr_core_news_lg`, `fr_core_news_sm`) qui sont épinglés comme URLs de wheels dans `requirements.txt`. Prévoir plusieurs centaines de Mo de téléchargements.

4. Télécharger les données NLTK utilisées au runtime :

   ```bash
   python -c "import nltk; nltk.download('punkt_tab')"
   ```

   Si une erreur runtime mentionne une autre ressource NLTK, relancer la même commande avec le nom donné dans la trace.

## Configuration

Ortholyse tourne entièrement hors ligne. Aucune clé API à renseigner.

Le modèle Whisper utilisé par l'app est lu depuis `app/assets/JSON/settings.json` (clé `modelWhisper`, indexe dans `["base", "small", "medium", "turbo"]`). Les modèles plus petits sont plus rapides, les plus gros plus précis. La vue Paramètres permet de basculer depuis l'app.

Les ressources linguistiques (listes de préfixes et suffixes) vivent à côté des settings dans `app/assets/JSON/`.

## Démarrage rapide

Depuis la racine du projet, avec l'environnement virtuel actif :

```bash
python app/main.py
```

La fenêtre s'ouvre sur l'Accueil. Choisir un fichier audio via Import, ou enregistrer une nouvelle séance, puis lancer l'analyse.

## Utilisation

Flux d'une séance type :

1. **Importer ou enregistrer** un fichier audio (WAV, MP3, M4A et la plupart des formats courants sont supportés)
2. **Transcrire** avec Whisper via la barre d'outils. La progression s'affiche dans la barre de statut.
3. **Corriger** le texte dans l'éditeur en écoutant. Cliquer un mot pour sauter à la position audio correspondante.
4. **Analyser** pour calculer LME, nombre de morphèmes, segmentation en énoncés et autres métriques.
5. **Exporter** un rapport PDF contenant la transcription corrigée et le tableau de métriques.

## Développement

Les tests tournent sur un jeu minimal de dépendances (UI, Whisper et Spacy sont mockés dans `tests/conftest.py`) :

```bash
# Installer les dépendances de test (pytest, pytest-cov, pytest-mock, nltk, num2words, fpdf2, python-docx)
pip install -r requirements-test.txt

# Télécharger les données NLTK utilisées par les tests
python -m nltk.downloader -q punkt punkt_tab

# Lancer la suite (la couverture est appliquée via pyproject.toml)
pytest
```

`pyproject.toml` porte la config pytest et coverage, dont le gate `--cov-fail-under=80` et la liste `omit` pour l'UI, les contrôleurs et les wrappers ML qui ont besoin d'un serveur d'affichage, de matériel audio ou du vrai modèle Whisper pour tourner.

Le même flux tourne à chaque push et PR via `.github/workflows/ci.yml`.

## Tests et couverture

La CI tourne à chaque push et pull request sur `main` :

- `pytest` avec couverture sur les modules métier (`app/models/Analyse_NLTK.py`, `exportation.py`, `operation_fichier.py`)
- Échec du build si la couverture descend sous 80 % sur les modules gatés
- Couverture actuelle sur ces modules : 81 % (voir `coverage.xml`)

Les widgets UI, les vues Qt, les contrôleurs et les wrappers Whisper / audio sont exclus du gate parce qu'ils nécessitent un serveur d'affichage, du matériel audio ou le vrai modèle ML pour être exercés correctement.

## Feuille de route

- Support de l'anglais (Spacy `en_core_web_lg`, corpus NLTK anglais ; le wheel Spacy anglais est déjà épinglé dans `requirements.txt`)
- Modèle Whisper et chemin FFmpeg configurables depuis la vue Paramètres, sans toucher au code
- Traitement batch de plusieurs séances
- Templates de rapport configurables
- Vue de comparaison côte à côte entre séances patient

## Contribuer

Issues et pull requests bienvenues. Merci de lire [CONTRIBUTING.fr.md](./CONTRIBUTING.fr.md) (ou [CONTRIBUTING.md](./CONTRIBUTING.md) en anglais) avant d'ouvrir une PR. Le travail est suivi via les issues GitHub, ouvrir une issue pour discuter des changements importants avant de coder.

## Licence

MIT. Voir [LICENSE](./LICENSE).

## Remerciements

- [OpenAI Whisper](https://github.com/openai/whisper) pour la reconnaissance vocale hors ligne
- [Spacy](https://spacy.io/) et le pipeline français `fr_core_news_lg`
- [NLTK](https://www.nltk.org/) pour les helpers de tokenisation et morphologie
- [PySide6](https://doc.qt.io/qtforpython/) et le projet Qt pour la boîte à outils UI desktop
- Les clinicien-ne-s qui ont testé les premières versions et signalé ce qui faisait mal

Références méthodologiques sur la LME : Brown (1973), Rondal (1985). Si vous utilisez Ortholyse dans un travail académique, merci de citer les articles correspondants pour les métriques sous-jacentes.

## Lire l'article

Le raisonnement de design, le choix de l'offline-first et les leçons retenues sont détaillés ici :

https://solidscale.tech/insights/ortholyse-bilan-orthophonique-open-source

## Page projet

Page projet avec captures et résumé non technique :

https://solidscale.tech/labs/ortholyse
