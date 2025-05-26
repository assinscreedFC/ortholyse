# Ortholyse

## Description
Ortholyse est une application desktop permettant aux orthophonistes d'analyser automatiquement la complexité syntaxique des énoncés transcrits à partir d'enregistrements audio. L'objectif est d'automatiser le processus de transcription et d'analyse linguistique afin de faire gagner du temps aux professionnels de santé.

## Fonctionnalités principales
- **Transcription automatique (Speech-to-Text)** : Conversion fiable des enregistrements audio en texte.
- **Correction manuelle** : Révision et édition des transcriptions.
- **Enregistrement et écoute en temps réel** : Possibilité d'enregistrer directement un audio depuis l'application et de l'écouter pour correction immédiate.
- **Analyse linguistique avancée** : Calcul de métriques essentielles comme le nombre total de mots, d'énoncés et de morphèmes.
- **Exportation des résultats** : Sauvegarde et export des analyses sous divers formats (TXT, PDF, CSV).

## Technologies utilisées
- **Python 3**
- **Whisper** (OpenAI) pour la transcription automatique
- **NLTK** pour le traitement et l'analyse linguistique

## Installation
1. Assurez-vous d'avoir **Python 3.12** installé sur votre système.
2. Clonez le dépôt :
   ```sh
   git clone https://github.com/assinscreedFC/OrthoLyse.git
   cd ortholyse
   ```
3. Installez les dépendances :
   ```sh
   pip install -r requirements.txt
   ```

## Utilisation
- **Lancer l'application** :
   ```sh
   python app/main.py
   ```
- **Importer ou enregistrer un fichier audio** pour le transcrire et l'analyser.
- **Écouter et modifier les transcriptions** en temps réel.
- **Exporter les résultats** dans le format souhaité.

## Prochaines évolutions
- Gestion des patients et suivi des séances.
- Affichage de graphiques pour visualiser l’évolution des patients.
- Fonctionnalités avancées d’analyse linguistique et d’annotations.
