**Read in [English](./README.md) / [Français](./README.fr.md)**

# Ortholyse

Desktop app for speech-language pathologists. It transcribes session audio with Whisper and computes syntactic metrics on the corrected transcript, locally.

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-41cd52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](./LICENSE)
[![CI](https://img.shields.io/badge/CI-pytest%20%2B%20coverage-success?style=flat-square)](.github/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-80%25%2B-brightgreen?style=flat-square)](.github/workflows/ci.yml)

> Built for clinicians who lose hours transcribing sessions by hand. Ortholyse turns a recording into a structured analysis you can correct, validate and export.

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

- Speech-language pathologists in private practice or in hospital settings
- French-speaking clinical environments (the NLP pipeline is tuned for French, English support is planned)
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

Screenshots will be added in a future release. The app exposes a sidebar with the main views (Home, Recording, Import, Transcription correction, Analysis, Settings).

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

The codebase follows a Views / Controllers / Models split:

- `app/Views/` Qt screens (Home, Recording, Import, Transcription, Metrique, Settings)
- `app/Widgets/` reusable Qt widgets (AudioPlayer, AudioBar, Feuille)
- `app/controllers/` controller layer wiring views to models
- `app/models/` business logic and IO:
  - `Analyse_NLTK.py` linguistic analysis (MLU, morphemes, Spacy + NLTK pipeline)
  - `exportation.py` PDF and JSON export
  - `operation_fichier.py` audio file IO and silence detection
  - `transcription.py` Whisper wrappers
  - `audio_worker.py`, `memo.py` recording and live capture
- `app/assets/` fonts, icons, JSON resources (suffixes, prefixes, settings)

## Prerequisites

- Python 3.12 or higher
- FFmpeg available to the app (the code expects a binary under `bin/ffmpeg` relative to `app/`; on a dev machine the simplest path is to install FFmpeg system-wide and adjust `find_ffmpeg()` in `app/models/operation_fichier.py` if needed)
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

   This installs PySide6, Whisper, torch, Spacy and the French Spacy models (`fr_core_news_lg`, `fr_core_news_sm`) which are pinned as wheel URLs in `requirements.txt`. Plan for several hundred megabytes of downloads.

4. Download the NLTK data used at runtime:

   ```bash
   python -c "import nltk; nltk.download('punkt_tab')"
   ```

   If a runtime error mentions another NLTK resource, run the same command with the resource named in the trace.

## Configuration

Ortholyse runs entirely offline. There are no API keys.

The Whisper model used by the app is read from `app/assets/JSON/settings.json` (`modelWhisper` key, indexing into `["base", "small", "medium", "turbo"]`). Smaller models are faster, larger ones are more accurate. The Settings view lets you switch from inside the app.

Linguistic resources (prefix and suffix lists) live alongside settings in `app/assets/JSON/`.

## Quickstart

From the project root, with the virtual environment active:

```bash
python app/main.py
```

The app window opens on Home. Pick an audio file via Import, or record a fresh session, then run the analysis.

## Usage

The typical session flow:

1. **Import or record** an audio file (WAV, MP3, M4A and most common formats are supported)
2. **Transcribe** with Whisper from the toolbar. Progress is shown in the status bar.
3. **Correct** the text in the editor while listening. Click a word to jump to the matching audio position.
4. **Analyse** to compute MLU, morpheme count, utterance segmentation and other metrics.
5. **Export** a PDF report containing the corrected transcription and the metrics table.

## Development

Tests run on a minimal dependency set (UI, Whisper and Spacy are mocked in `tests/conftest.py`):

```bash
# Install test dependencies (pytest, pytest-cov, pytest-mock, nltk, num2words, fpdf2, python-docx)
pip install -r requirements-test.txt

# Download the NLTK data the tests rely on
python -m nltk.downloader -q punkt punkt_tab

# Run the test suite (coverage is enforced via pyproject.toml)
pytest
```

`pyproject.toml` carries the pytest and coverage config, including a `--cov-fail-under=80` gate and the omit list for UI, controllers, and ML wrappers that need a display server, audio hardware or the actual Whisper model to run.

The same flow runs on every push and PR through `.github/workflows/ci.yml`.

## Tests and coverage

CI runs on every push and pull request to `main`:

- `pytest` with coverage on the business modules (`app/models/Analyse_NLTK.py`, `exportation.py`, `operation_fichier.py`)
- Build fails if coverage drops below 80 percent on the gated modules
- Current coverage on those modules is 81 percent (see `coverage.xml`)

UI widgets, Qt views, controllers, and the Whisper / audio wrappers are excluded from the gate because they need a display server, audio hardware or the real ML model to exercise meaningfully.

## Roadmap

- English language support (Spacy `en_core_web_lg`, English NLTK corpora; the English Spacy wheel is already pinned in `requirements.txt`)
- Configurable Whisper model and FFmpeg path from the Settings view, without editing source
- Batch processing of multiple sessions
- Configurable report templates
- Side-by-side comparison view across patient sessions

## Contributing

Issues and pull requests are welcome. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) (or [CONTRIBUTING.fr.md](./CONTRIBUTING.fr.md) in French) before opening a PR. Work is tracked via GitHub issues, open one to discuss larger changes before coding.

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
