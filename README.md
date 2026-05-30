**Read in [English](./README.md) / [Français](./README.fr.md)**

# Ortholyse

Desktop app for speech-language pathologists. Automates audio transcription and computes syntactic complexity metrics on patient speech samples.

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-41cd52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](./LICENSE)
[![CI](https://img.shields.io/badge/CI-pytest%20%2B%20coverage-success?style=flat-square)](.github/workflows/)
[![Coverage](https://img.shields.io/badge/coverage-80%25%2B-brightgreen?style=flat-square)](.github/workflows/)

> Built for clinicians who lose hours transcribing sessions by hand. Ortholyse turns a recording into a structured analysis you can correct, validate and export in minutes.

## Table of Contents

1. [About](#about)
2. [Features](#features)
3. [Screenshots](#screenshots)
4. [Architecture](#architecture)
5. [Prerequisites](#prerequisites)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [Quickstart](#quickstart)
9. [Usage](#usage)
10. [Development](#development)
11. [Tests and coverage](#tests-and-coverage)
12. [Roadmap](#roadmap)
13. [Contributing](#contributing)
14. [License](#license)
15. [Acknowledgments](#acknowledgments)
16. [Read the Story](#read-the-story)
17. [Live page](#live-page)

## About

Speech-language pathologists routinely transcribe patient sessions to compute metrics like Mean Length of Utterance (MLU), morpheme count, and syntactic complexity. Doing this by hand on a 20 minute session can take a full hour, and the maths is error-prone.

Ortholyse runs the recording through Whisper for transcription, lets you correct the text against synchronised playback, then computes the linguistic metrics with Spacy and NLTK. Everything runs locally on the clinician's machine. No cloud upload, no patient data leaving the desk.

**Built for:**

- Speech-language pathologists (orthophonistes) in private practice or in hospital settings
- French-speaking clinical environments (the NLP pipeline is tuned for French; English support is planned)
- Researchers comparing speech samples across patient cohorts

## Features

- Local audio transcription with OpenAI Whisper, no cloud calls
- Live recording from the microphone inside the app
- Synced audio player and text editor for fast manual correction
- Automatic linguistic metrics: word count, utterance count, MLU, morphological complexity
- PDF report export combining the transcription and the analysis
- French NLP pipeline using Spacy `fr_core_news_lg` and NLTK
- Desktop UI built with PySide6, runs on Windows, macOS and Linux

## Screenshots

Screenshots will be added in a future release. The app exposes three main views (Recording, Import, Analysis) accessible from a left sidebar.

## Architecture

```
+------------------+      +------------------+      +-------------------+
|  Audio capture   | ---> |  Whisper STT     | ---> |  Editable text    |
|  (PySide6 UI)    |      |  (local model)   |      |  (sync playback)  |
+------------------+      +------------------+      +-------------------+
                                                              |
                                                              v
                                                    +-------------------+
                                                    | Spacy + NLTK      |
                                                    | linguistic metrics|
                                                    +-------------------+
                                                              |
                                                              v
                                                    +-------------------+
                                                    | PDF report export |
                                                    +-------------------+
```

The codebase is split into:

- `app/` Qt UI screens and widgets
- `app/feuille/` linguistic analysis modules (Analyse_NLTK, MLU, morpheme counters)
- `app/exportation/` PDF generation
- `app/operation_fichier/` file IO and session storage
- `app/transcription/` Whisper wrappers

## Prerequisites

- Python 3.12 or higher
- FFmpeg installed and on `PATH` (Whisper and pydub require it for audio decoding)
- About 4 GB of free disk for the Whisper and Spacy models
- A working microphone if you plan to record sessions in app

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/assinscreedFC/ortholyse.git
   cd ortholyse
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate     # Windows
   source .venv/bin/activate     # macOS / Linux
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   This step downloads several hundred megabytes of model weights, so plan accordingly.

4. Download the French Spacy models:

   ```bash
   python -m spacy download fr_core_news_lg
   python -m spacy download fr_core_news_sm
   ```

5. Download the required NLTK data:

   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
   ```

   If a runtime error mentions a missing NLTK resource, run the same command for the specific resource named in the trace.

## Configuration

Ortholyse runs entirely offline and stores its data under `data/` inside the project folder. There are no API keys to set. Whisper model size can be tweaked in `app/transcription/` by changing the default model name (`base`, `small`, `medium`, `large`). Smaller models are faster but less accurate.

## Quickstart

From the project root, with the virtual environment active:

```bash
python app/main.py
```

The app window opens on the Recording view. Pick an audio file via Import, or record a fresh session, then run the analysis.

## Usage

The typical session flow:

1. **Import or record** an audio file (WAV, MP3, M4A and most common formats are supported)
2. **Transcribe** with Whisper from the toolbar. Progress is shown in the status bar.
3. **Correct** the text in the editor while listening. Click a word to jump to the matching audio position.
4. **Analyse** to compute MLU, morpheme count, utterance segmentation and other metrics.
5. **Export** a PDF report containing the corrected transcription and the metrics table.

## Development

```bash
# Install dev dependencies (pytest, pytest-cov, ruff)
pip install -r requirements-dev.txt

# Run the linter
ruff check app tests

# Run the test suite
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

UI code (PySide6 widgets) and ML wrappers (Whisper, Spacy) are excluded from the coverage gate, since they require a display server and large models to exercise meaningfully. The business modules under `app/feuille/`, `app/exportation/` and `app/operation_fichier/` are covered at 80 percent or more.

## Tests and coverage

CI runs on every push and pull request to `main` via GitHub Actions:

- Lint with ruff
- pytest with coverage on business modules
- Fails the build if coverage drops below 80 percent on the gated modules

See `.github/workflows/` for the exact pipeline.

## Roadmap

- English language support (Spacy `en_core_web_lg`, English NLTK corpora)
- Batch processing of multiple sessions
- Configurable report templates
- Side-by-side comparison view across patient sessions

## Contributing

Issues and pull requests are welcome. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) (or [CONTRIBUTING.fr.md](./CONTRIBUTING.fr.md) in French) before opening a PR. Work is tracked via GitHub issues; please open one to discuss larger changes before coding.

## License

MIT. See [LICENSE](./LICENSE).

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for offline speech to text
- [Spacy](https://spacy.io/) and the `fr_core_news_lg` French pipeline
- [NLTK](https://www.nltk.org/) for tokenisation and morphology helpers
- [PySide6](https://doc.qt.io/qtforpython/) and the Qt project for the desktop UI toolkit
- Clinicians who tested early builds and reported what hurt

Mean Length of Utterance methodology references: Brown (1973), Rondal (1985). If you use Ortholyse in academic work, please cite the corresponding papers for the underlying metrics.

## Read the Story

The design rationale, the choice of offline-first, and lessons learned are written up here:

https://solidscale.tech/insights/ortholyse-bilan-orthophonique-open-source

## Live page

Project page with screenshots and a non-technical summary:

https://solidscale.tech/labs/ortholyse
