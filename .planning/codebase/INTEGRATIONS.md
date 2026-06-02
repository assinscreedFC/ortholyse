# External Integrations

**Analysis Date:** 2026-06-02

## APIs & External Services

**OpenAI Whisper:**
- Service: Local speech-to-text transcription (OpenAI model, downloaded once)
- SDK/Client: `openai-whisper` 20240930 Python package
- No API key required; runs entirely locally on user's machine
- Location: `app/models/transcription.py:235-325`
- Usage:
  - Downloads model variants on first use ("base", "small", "medium", "turbo")
  - Cached at module level to avoid reloading 800MB-1.5GB per transcription
  - Detects GPU (CUDA) availability; falls back to CPU
  - Returns transcription with word-level timestamps for audio-text synchronization

**spaCy Language Models:**
- Service: French linguistic parsing (downloaded from GitHub releases)
- Models:
  - `fr_core_news_lg` 3.8.0 (~500MB, primary) - Full pipeline with word vectors
  - `fr_core_news_sm` 3.8.0 (~50MB, fallback) - Smaller footprint
- SDK/Client: `spacy` 3.8.4 Python package
- Download: Manual via GitHub releases URLs pinned in `requirements.txt:20-21`
- No network calls after download; models cached locally
- Location: `app/models/Analyse_NLTK.py:47`
- Usage:
  - Tokenization, POS tagging, dependency parsing, morphological analysis
  - Lazy-loaded on first instantiation to avoid startup delay
  - Used for syntactic metric computation (complexity, dependency relations, etc.)

## Data Storage

**Databases:**
- None - Ortholyse is a standalone desktop app
- Patient data stored locally in user's filesystem only
- No centralized database; no network I/O

**File Storage:**
- Local filesystem only
- Supported audio input formats: MP3, WAV, M4A, MP4, OGG, FLAC
- Export formats: JSON, TXT, CSV (column and row layouts), PDF, DOCX
- Location: `app/models/operation_fichier.py` (file validation, format detection)
- Audio metadata: TextGrid format support for phonetic annotations

**Temporary File Management:**
- Audio splitting: Creates unique tempdir via `tempfile.mkdtemp(prefix="ortholyse_split_")`
- Audio conversion: Creates unique tempfile via `tempfile.mkstemp(prefix="ortholyse_convert_")`
- Cleanup: Automatic via `shutil.rmtree()` after transcription completes
- Location: `app/models/operation_fichier.py:156-190`, `app/models/transcription.py:296`
- No lingering temp files due to explicit cleanup

**Caching:**
- Whisper model: Module-level cache to avoid reloading (performance optimization)
- spaCy model: Cached on disk after first download, loaded once per session
- NLTK assets (suffix.json, prefix.json): Lazy-loaded once, held in memory

## Authentication & Identity

**Auth Provider:**
- None - Ortholyse is a single-user desktop application
- No user accounts, login, or identity management
- Patient data is file-based; no access control beyond OS-level permissions

## Monitoring & Observability

**Error Tracking:**
- None - No error reporting service
- All errors logged locally via Python `logging` module

**Logs:**
- Python `logging` module configured at `app/config.py:10-13`
- Format: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`
- Log level: `logging.INFO` (debug messages logged but not shown by default)
- Output: Console/stdout only (no file logging configured)
- No sensitive data logged (RGPD compliance in place; see recent commit "fix(rgpd): replace print() with logging")
- Error handling: Contextual logging with `exc_info=True` for debugging

## CI/CD & Deployment

**Hosting:**
- None - Desktop application (Windows/macOS/Linux)
- Distribution: PyInstaller bundles (`sys._MEIPASS` detection at `app/main.py:11-18`)
- Platform-specific FFmpeg bundled as `_internal/ffmpeg` in frozen bundles

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`)
- Runs pytest with coverage gate (80%+ required)
- Heavy dependencies (Whisper, torch, PyAudio, PySide6) stubbed in CI via `tests/conftest.py`
- Coverage config: `pyproject.toml [tool.coverage.run]` (lines 70-87)
- Excludes: Widgets, Views, Controllers, transcription pipelines, audio I/O, test stubs

## Environment Configuration

**Required env vars:**
- None currently used
- Settings stored in `app/assets/JSON/settings.json` (user editable, included in app bundle)
- Example: Whisper model selection at `app/models/transcription.py:237-240`

**Secrets location:**
- No secrets used or managed
- Offline-first design: no API keys, credentials, or auth tokens
- GDPR-compliant: patient audio never leaves the user's machine

**Configuration Files:**
- `app/assets/JSON/settings.json` - User preferences (Whisper model, output paths, etc.)
- `app/assets/JSON/suffixe.json` - French language morphological suffixes
- `app/assets/JSON/prefixe.json` - French language morphological prefixes
- Lazy-loaded via `app/models/Analyse_NLTK.py:31-40`

## Webhooks & Callbacks

**Incoming:**
- None - No network endpoints, no server component

**Outgoing:**
- None - No external API calls, no webhooks

## System Dependencies

**FFmpeg:**
- Required for audio format conversion and extraction from video containers
- Not installed via pip; must be present on system
- Runtime detection at `app/models/operation_fichier.py:70-91`:
  1. PyInstaller bundle location: `sys._MEIPASS/_internal/ffmpeg`
  2. Vendored binary (optional, legacy): `app/../bin/ffmpeg`
  3. System PATH via `shutil.which('ffmpeg')`
  4. Fallback: literal "ffmpeg" string (rely on PATH)
- Used by: `pydub` for MP4 extraction, audio format conversion, silence detection

**libmagic (Optional):**
- Used for MIME type validation of audio files
- Optional: gracefully disabled if python-magic or libmagic native lib unavailable
- Whitelist validation at `app/models/operation_fichier.py:36-46`
- If unavailable: extension-based whitelist is used instead (`app/models/operation_fichier.py:25-33`)

**Audio Hardware (Runtime, not compile-time):**
- PyAudio: Requires audio device for recording (real hardware)
- sounddevice: Requires audio device for playback (real hardware)
- No compile-time requirement; gracefully handled if no device available
- Location: `app/controllers/Record_controllers.py`, `app/Widgets/AudioBar.py`

## ML/NLP Pipelines

**Transcription Pipeline:**
- Input: Audio file (MP3, WAV, M4A, MP4, OGG, FLAC)
- Process:
  1. Validate file format and MIME type at `app/models/operation_fichier.py:49-68`
  2. Extract audio from MP4 if needed at `app/models/transcription.py:268-272`
  3. Split large files (>25MB or >10 min) at `app/models/transcription.py:275-277`
  4. Load Whisper model (cached) at `app/models/transcription.py:288`
  5. Transcribe with word-level timestamps at `app/models/transcription.py:294-299`
- Output: JSON segments with text and word-level timing (for synchronization)
- Location: `app/models/transcription.py:242-325`

**Linguistic Analysis Pipeline:**
- Input: Corrected transcript (user-edited text after Whisper)
- Process:
  1. Load spaCy French model (`fr_core_news_lg`) at `app/models/Analyse_NLTK.py:47`
  2. Tokenize with NLTK and custom apostrophe handling at `app/models/Analyse_NLTK.py:65-73`
  3. Convert numerals to words at `app/models/Analyse_NLTK.py:75-99`
  4. Apply stemming (Snowball) and morphological analysis
  5. Compute metrics: word count, morpheme count, MLU, syntactic complexity, etc.
- Output: Dictionary of linguistic metrics
- Location: `app/models/Analyse_NLTK.py` (class `Analyse_NLTK`)

**Audio Segmentation:**
- Automatic silence detection for smart audio splitting
- Uses pydub's silence detection: min silence 900ms, threshold -40dB
- Location: `app/models/operation_fichier.py:156-190`
- Purpose: Large files (>25MB or >10 min) split at silence boundaries to preserve coherence

## Timestamps & Audio-Text Synchronization

**Mapping:**
- Whisper provides word-level timestamps (start/end in seconds)
- Custom tokenization handles French apostrophes (e.g., "m'appeler" as single token)
- Mapping adjusted when user edits transcript at `app/models/transcription.py:158-233`
- Used by playback widget to highlight current word during listening
- Location: `app/models/transcription.py:70-155` (mapping extraction)

**Fallback:**
- If word-level timestamps unavailable, uniform time distribution across segment
- Location: `app/models/transcription.py:140-153`

## Offline-First Design

**Network Policy:**
- Zero network calls after installation
- All models downloaded once on first use (not on every run)
- spaCy models: GitHub release URLs pinned at `requirements.txt:20-21`
- Whisper models: Downloaded automatically on first transcription request
- Patient audio never leaves the user's machine
- No telemetry, no analytics, no tracking

**GDPR Compliance:**
- All processing local to user's filesystem
- No cloud storage, no data transmission
- logging module used instead of print() for audit trails
- Sensitive data (patient audio) handled safely with tempfile cleanup

---

*Integration audit: 2026-06-02*
