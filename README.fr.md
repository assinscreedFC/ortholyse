**Lire en [English](./README.md) / [Français](./README.fr.md)**

# Ortholyse

Application desktop pour orthophonistes. Automatise la transcription audio et calcule des métriques de complexité syntaxique sur des échantillons de parole patient.

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-41cd52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![Licence: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](./LICENSE)
[![CI](https://img.shields.io/badge/CI-pytest%20%2B%20coverage-success?style=flat-square)](.github/workflows/)
[![Couverture](https://img.shields.io/badge/coverage-80%25%2B-brightgreen?style=flat-square)](.github/workflows/)

> Conçu pour les clinicien-ne-s qui perdent des heures à transcrire des séances à la main. Ortholyse transforme un enregistrement en analyse structurée que vous pouvez corriger, valider et exporter en quelques minutes.

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

Ortholyse fait passer l'enregistrement par Whisper pour la transcription, vous laisse corriger le texte avec une lecture synchronisée, puis calcule les métriques linguistiques avec Spacy et NLTK. Tout tourne en local sur la machine du praticien. Aucun upload cloud, aucune donnée patient ne quitte le bureau.

**Pour qui :**

- Orthophonistes en cabinet libéral ou en milieu hospitalier
- Environnements cliniques francophones (le pipeline NLP est calibré pour le français ; support anglais prévu)
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

Les captures seront ajoutées dans une prochaine version. L'application présente trois vues principales (Enregistrement, Import, Analyse), accessibles depuis une barre latérale gauche.

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

Le code est découpé en :

- `app/` écrans et widgets Qt
- `app/feuille/` modules d'analyse linguistique (Analyse_NLTK, LME, compteurs de morphèmes)
- `app/exportation/` génération PDF
- `app/operation_fichier/` IO fichiers et stockage de séances
- `app/transcription/` wrappers Whisper

## Prérequis

- Python 3.12 ou plus récent
- FFmpeg installé et présent dans le `PATH` (requis par Whisper et pydub pour décoder l'audio)
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

   Cette étape télécharge plusieurs centaines de Mo de poids de modèles, prévoir le temps nécessaire.

4. Télécharger les modèles Spacy français :

   ```bash
   python -m spacy download fr_core_news_lg
   python -m spacy download fr_core_news_sm
   ```

5. Télécharger les données NLTK requises :

   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
   ```

   Si une erreur runtime mentionne une ressource NLTK manquante, relancer la même commande avec le nom exact donné dans la trace.

## Configuration

Ortholyse tourne entièrement hors ligne et stocke ses données sous `data/` dans le dossier projet. Aucune clé API à renseigner. La taille du modèle Whisper peut être ajustée dans `app/transcription/` en changeant le nom de modèle par défaut (`base`, `small`, `medium`, `large`). Les modèles plus petits sont plus rapides mais moins précis.

## Démarrage rapide

Depuis la racine du projet, avec l'environnement virtuel actif :

```bash
python app/main.py
```

La fenêtre s'ouvre sur la vue Enregistrement. Choisir un fichier audio via Import, ou enregistrer une nouvelle séance, puis lancer l'analyse.

## Utilisation

Flux d'une séance type :

1. **Importer ou enregistrer** un fichier audio (WAV, MP3, M4A et la plupart des formats courants sont supportés)
2. **Transcrire** avec Whisper via la barre d'outils. La progression s'affiche dans la barre de statut.
3. **Corriger** le texte dans l'éditeur en écoutant. Cliquer un mot pour sauter à la position audio correspondante.
4. **Analyser** pour calculer LME, nombre de morphèmes, segmentation en énoncés et autres métriques.
5. **Exporter** un rapport PDF contenant la transcription corrigée et le tableau de métriques.

## Développement

```bash
# Installer les dépendances dev (pytest, pytest-cov, ruff)
pip install -r requirements-dev.txt

# Lancer le linter
ruff check app tests

# Lancer la suite de tests
pytest

# Lancer avec couverture
pytest --cov=app --cov-report=term-missing
```

Le code UI (widgets PySide6) et les wrappers ML (Whisper, Spacy) sont exclus du gate de couverture, parce qu'ils nécessitent un serveur d'affichage et de gros modèles pour être exercés correctement. Les modules métier sous `app/feuille/`, `app/exportation/` et `app/operation_fichier/` sont couverts à 80 % ou plus.

## Tests et couverture

La CI tourne à chaque push et pull request sur `main` via GitHub Actions :

- Lint avec ruff
- pytest avec couverture sur les modules métier
- Échec du build si la couverture descend sous 80 % sur les modules gatés

Voir `.github/workflows/` pour le pipeline exact.

## Feuille de route

- Support de l'anglais (Spacy `en_core_web_lg`, corpus NLTK anglais)
- Traitement batch de plusieurs séances
- Templates de rapport configurables
- Vue de comparaison côte à côte entre séances patient

## Contribuer

Issues et pull requests bienvenues. Merci de lire [CONTRIBUTING.fr.md](./CONTRIBUTING.fr.md) (ou [CONTRIBUTING.md](./CONTRIBUTING.md) en anglais) avant d'ouvrir une PR. Le travail est suivi via les issues GitHub ; ouvrir une issue pour discuter des changements importants avant de coder.

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
