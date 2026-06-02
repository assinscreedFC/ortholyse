# Technology Stack

**Analysis Date:** 2026-06-02

## Languages

**Primary:**
- Python 3.12+ - Desktop application, all business logic, audio processing, NLP pipelines

## Runtime

**Environment:**
- CPython 3.12 (minimum) via `pyproject.toml` requires-python field
- Windows 11 (primary platform; Windows-specific code for taskbar icon at `app/main.py:39`)
- Linux/macOS supported (audio/FFmpeg path resolution is cross-platform)

**Package Manager:**
- pip (via setuptools build system)
- Lockfile: `requirements.txt` (pinned versions for reproducibility)
- Optional test dependencies in `requirements-test.txt`

## Frameworks

**Core:**
- **PySide6** 6.8.2.1 - Desktop GUI framework (Qt6 bindings), primary UI layer
  - `PySide6_Essentials` 6.8.2.1 - Core widgets
  - `PySide6_Addons` 6.8.2.1 - Advanced components (image handling, document rendering)
  - Location: `app/Views/*`, `app/Widgets/*`, `app/controllers/*`

**Speech & Transcription:**
- **openai-whisper** 20240930 - Local speech-to-text transcription
  - Uses `torch` 2.6 and `torchaudio` 2.6 as compute backend
  - Model variants: ["base", "small", "medium", "turbo"] (user-selectable at `app/models/transcription.py:20`)
  - Supports GPU (CUDA) and CPU inference with runtime device detection (`app/models/transcription.py:280`)
  - Models cached at module level to avoid 800MB-1.5GB reload per transcription
  - Audio input formats: MP3, WAV, M4A, MP4, OGG, FLAC (whitelisted at `app/models/operation_fichier.py:26-33`)

**NLP & Linguistic Analysis:**
- **spacy** 3.8.4 - Tokenization, POS tagging, dependency parsing, morphological analysis
  - Language model: `fr_core_news_lg` 3.8.0 (~500MB, French language, downloaded from GitHub releases)
  - Loaded lazily on first instantiation at `app/models/Analyse_NLTK.py:47`
  - Fallback to `fr_core_news_sm` 3.8.0 (~50MB, smaller model) also available in `requirements.txt`
  - Location: `app/models/Analyse_NLTK.py`

- **NLTK** 3.9.4 - Sentence tokenization, stemming (Snowball stemmer for French)
  - Lazy-loaded asset management for suffix/prefix JSON files at `app/models/Analyse_NLTK.py:31-40`
  - Location: `app/models/Analyse_NLTK.py`

**Number Processing:**
- **num2words** 0.5.14 - Convert numerals to words (e.g., "1.5" → "un virgule cinq") for linguistic metrics
  - Location: `app/models/Analyse_NLTK.py:75-99`

**Testing:**
- **pytest** 8.3.4 - Test runner and assertion library
- **pytest-cov** 5.0 - Coverage reporting (80%+ minimum enforced at `pyproject.toml:66`)
- **pytest-mock** 3.12 - Mocking utilities for heavy dependencies
- Config: `pyproject.toml [tool.pytest.ini_options]` (lines 64-68)
- Test path: `tests/` directory
- Heavy modules (Whisper, torch, PyAudio, PySide6) stubbed at `tests/conftest.py:59-88` to avoid CI dependency bloat

**Build/Dev:**
- **setuptools** ≥64 - Python packaging and distribution
  - Config: `pyproject.toml [build-system]` (setuptools.build_meta backend)
- **wheel** - Binary distribution format

## Audio Processing & Media

**Audio Handling:**
- **pydub** 0.25.1 - Audio file conversion, splitting, silence detection
  - Supports: MP3, WAV, M4A, MP4, OGG, FLAC (via FFmpeg backend)
  - Silence detection for smart audio segmentation at `app/models/operation_fichier.py:156-190`
  - Location: `app/models/operation_fichier.py`, `app/models/audio_worker.py`

- **PyAudio** 0.2.14 - Real-time microphone audio capture
  - Location: `app/controllers/Record_controllers.py` (live recording feature)
  - Omitted from test coverage (requires audio device hardware)

- **sounddevice** 0.5.1 - Alternative audio I/O library for device detection and playback
  - Location: `app/Widgets/AudioBar.py` (playback controls)
  - Omitted from test coverage

**Audio Metadata:**
- **TextGrid** 1.6.1 - Praat TextGrid format support for phonetic annotations
  - Used for time-aligned transcription segments
  - Location: `app/models/transcription.py`

**FFmpeg Integration:**
- **System dependency** FFmpeg (not in Python dependencies)
  - Detected at runtime via `app/models/operation_fichier.py:70-91`
  - Fallback chain:
    1. PyInstaller bundle (`sys._MEIPASS/_internal/ffmpeg`)
    2. Vendored binary (`app/../bin/ffmpeg`, optional, legacy)
    3. System FFmpeg discovered via PATH
    4. Literal "ffmpeg" string (rely on PATH at call time)
  - Used by pydub for format conversion (MP4 extraction, etc.)

## Document Export

**PDF Generation:**
- **fpdf2** 2.8.2 - Low-level PDF generation with table support
  - Location: `app/models/exportation.py:67-100`
  - Custom font loading (Poppins TTF at `app/assets/Fonts/Poppins/`)

**Word Documents:**
- **python-docx** 1.1.2 - Microsoft Word .docx file creation
  - Styled tables, formatting, text alignment
  - Location: `app/models/exportation.py`

**PDF Analysis:**
- **pdfplumber** 0.11.5 - Extract text and tables from PDF files
- **pypdfium2** 4.30.1 - PDF rendering engine alternative
- **pdfminer.six** 20231228 - PDF text extraction (fallback)
- Used when importing pre-recorded patient sessions

**File Type Detection:**
- **python-magic** 0.4.27 - MIME type detection via libmagic (optional, no-op if unavailable)
  - Audio MIME whitelist validation at `app/models/operation_fichier.py:36-46`
  - Graceful degradation if libmagic native library not installed

## Data Processing

**Data Manipulation:**
- **pandas** 2.2.3 - DataFrame operations, metric aggregation, table export
- **numpy** 1.26.4 (< 2.0) - Numerical arrays, audio processing (via pydub/torch)

**Biological Data (Legacy):**
- **biopython** 1.85 - Listed in dependencies but no active usage in codebase

**String Processing:**
- **Unidecode** 1.3.8 - Unicode to ASCII transliteration
  - Useful for French diacritical marks handling

**XML Processing:**
- **lxml** ≥6.1.0 - XML parsing (for TextGrid format support)
- **defusedxml** 0.7.1 - Safe XML parsing (XXE protection)

## Network & Serialization

**Data Format Handling:**
- **Pydantic** 2.10.6 - Data validation and serialization (used in test fixtures, likely for future API)
- **requests** 2.32.3 - HTTP requests library (not actively used; likely legacy or future integration)

**CLI & Utilities:**
- **typer** 0.15.1 - CLI argument parsing (not used in current app, likely for future CLI)
- **rich** 13.9.4 - Terminal formatting and progress bars (no active usage in codebase)

## System & Logging

**Core Libraries:**
- **certifi** 2025.1.31 - SSL certificate bundle
- **click** 8.1.8 - Command-line interface (dependency of typer; not directly used)

**Logging:**
- Built-in `logging` module (configured at `app/config.py:10-13`)
- All modules import `app.config` to trigger `logging.basicConfig()` as a side effect
- Format: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`

## Platform Support

**Development:**
- Windows 11 Home (10.0.26200) - primary development platform
- Python 3.12+ required
- FFmpeg system dependency (via vendor, system PATH, or bundle)
- libmagic native library optional (for MIME validation; graceful no-op if missing)

**Production (Distributed via PyInstaller):**
- Windows 7+ (based on PySide6 support)
- macOS (Intel/M-series, via PySide6)
- Linux (via PySide6; less tested)
- FFmpeg bundled as `_internal/ffmpeg` in PyInstaller bundles
- No network connectivity required (offline-first design)

## Dependency Constraints

**Critical Version Pins:**
- `numpy < 2.0` - Locks to 1.26.x for compatibility with torch/torchaudio
- `cryptography >= 46.0.5` - Security requirement
- `pillow >= 12.2.0` - Image security fixes
- `urllib3 >= 2.7.0` - HTTP security fixes
- `lxml >= 6.1.0` - XML security patches

**Optional:**
- Test dependencies installed separately via `requirements-test.txt` (CI-only)
- Spacy models (`fr_core_news_lg`, `fr_core_news_sm`) downloaded from GitHub releases on first run

---

*Stack analysis: 2026-06-02*
