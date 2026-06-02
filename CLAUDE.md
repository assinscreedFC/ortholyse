<!-- GSD:project-start source:PROJECT.md -->
## Project

**Ortholyse**

Application desktop (Python / PySide6, 100 % locale) pour orthophonistes francophones. Le cœur du produit est **l'analyse d'échantillon de langage (LSA)** : à partir d'une transcription de séance, l'outil calcule les indicateurs linguistiques d'un bilan (MLU, morphèmes, diversité lexicale, complexité syntaxique, temps/modes verbaux). La transcription audio (Whisper local) est une commodité d'entrée, pas la valeur centrale.

Positionnement : **« le LSA convivial que CLAN ne sait pas rendre utilisable »**. CLAN/CHILDES fait déjà l'analyse de référence mais reste imbuvable pour un clinicien en cabinet ; Orthonie/myCR couvrent la dictée de compte-rendu (marché distinct, déjà pris). Le trou réel : l'analyse de la production du patient avec une UX accessible, en français.

**Core Value:** Un orthophoniste obtient des **indicateurs de bilan fiables (alignés sur les standards CLAN/MOR)** à partir d'une transcription, **sans rien installer ni configurer de technique**. Si tout le reste échoue, c'est ça qui doit marcher.

### Constraints

- **Tech stack** : Python 3.12+, PySide6 (Qt), refonte incrémentale — pas de changement de techno
- **Offline / RGPD** : tout reste sur le poste, zéro cloud, aucune donnée patient en télémétrie ni en logs
- **Dépendances embarquées** : CLAN + grammaire MOR FR + FFmpeg doivent être packagés de façon invisible pour l'utilisateur final
- **Licence** : projet MIT ; vérifier la licence CLAN/TalkBank avant de redistribuer les binaires (bloquant Phase 0)
- **Cible non technique** : orthophonistes libéraux sans support IT ni ligne de commande
- **Qualité** : maintenir le gate de couverture 80 % sur les modules métier
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.12+ - Desktop application, all business logic, audio processing, NLP pipelines
## Runtime
- CPython 3.12 (minimum) via `pyproject.toml` requires-python field
- Windows 11 (primary platform; Windows-specific code for taskbar icon at `app/main.py:39`)
- Linux/macOS supported (audio/FFmpeg path resolution is cross-platform)
- pip (via setuptools build system)
- Lockfile: `requirements.txt` (pinned versions for reproducibility)
- Optional test dependencies in `requirements-test.txt`
## Frameworks
- **PySide6** 6.8.2.1 - Desktop GUI framework (Qt6 bindings), primary UI layer
- **openai-whisper** 20240930 - Local speech-to-text transcription
- **spacy** 3.8.4 - Tokenization, POS tagging, dependency parsing, morphological analysis
- **NLTK** 3.9.4 - Sentence tokenization, stemming (Snowball stemmer for French)
- **num2words** 0.5.14 - Convert numerals to words (e.g., "1.5" → "un virgule cinq") for linguistic metrics
- **pytest** 8.3.4 - Test runner and assertion library
- **pytest-cov** 5.0 - Coverage reporting (80%+ minimum enforced at `pyproject.toml:66`)
- **pytest-mock** 3.12 - Mocking utilities for heavy dependencies
- Config: `pyproject.toml [tool.pytest.ini_options]` (lines 64-68)
- Test path: `tests/` directory
- Heavy modules (Whisper, torch, PyAudio, PySide6) stubbed at `tests/conftest.py:59-88` to avoid CI dependency bloat
- **setuptools** ≥64 - Python packaging and distribution
- **wheel** - Binary distribution format
## Audio Processing & Media
- **pydub** 0.25.1 - Audio file conversion, splitting, silence detection
- **PyAudio** 0.2.14 - Real-time microphone audio capture
- **sounddevice** 0.5.1 - Alternative audio I/O library for device detection and playback
- **TextGrid** 1.6.1 - Praat TextGrid format support for phonetic annotations
- **System dependency** FFmpeg (not in Python dependencies)
## Document Export
- **fpdf2** 2.8.2 - Low-level PDF generation with table support
- **python-docx** 1.1.2 - Microsoft Word .docx file creation
- **pdfplumber** 0.11.5 - Extract text and tables from PDF files
- **pypdfium2** 4.30.1 - PDF rendering engine alternative
- **pdfminer.six** 20231228 - PDF text extraction (fallback)
- Used when importing pre-recorded patient sessions
- **python-magic** 0.4.27 - MIME type detection via libmagic (optional, no-op if unavailable)
## Data Processing
- **pandas** 2.2.3 - DataFrame operations, metric aggregation, table export
- **numpy** 1.26.4 (< 2.0) - Numerical arrays, audio processing (via pydub/torch)
- **biopython** 1.85 - Listed in dependencies but no active usage in codebase
- **Unidecode** 1.3.8 - Unicode to ASCII transliteration
- **lxml** ≥6.1.0 - XML parsing (for TextGrid format support)
- **defusedxml** 0.7.1 - Safe XML parsing (XXE protection)
## Network & Serialization
- **Pydantic** 2.10.6 - Data validation and serialization (used in test fixtures, likely for future API)
- **requests** 2.32.3 - HTTP requests library (not actively used; likely legacy or future integration)
- **typer** 0.15.1 - CLI argument parsing (not used in current app, likely for future CLI)
- **rich** 13.9.4 - Terminal formatting and progress bars (no active usage in codebase)
## System & Logging
- **certifi** 2025.1.31 - SSL certificate bundle
- **click** 8.1.8 - Command-line interface (dependency of typer; not directly used)
- Built-in `logging` module (configured at `app/config.py:10-13`)
- All modules import `app.config` to trigger `logging.basicConfig()` as a side effect
- Format: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`
## Platform Support
- Windows 11 Home (10.0.26200) - primary development platform
- Python 3.12+ required
- FFmpeg system dependency (via vendor, system PATH, or bundle)
- libmagic native library optional (for MIME validation; graceful no-op if missing)
- Windows 7+ (based on PySide6 support)
- macOS (Intel/M-series, via PySide6)
- Linux (via PySide6; less tested)
- FFmpeg bundled as `_internal/ffmpeg` in PyInstaller bundles
- No network connectivity required (offline-first design)
## Dependency Constraints
- `numpy < 2.0` - Locks to 1.26.x for compatibility with torch/torchaudio
- `cryptography >= 46.0.5` - Security requirement
- `pillow >= 12.2.0` - Image security fixes
- `urllib3 >= 2.7.0` - HTTP security fixes
- `lxml >= 6.1.0` - XML security patches
- Test dependencies installed separately via `requirements-test.txt` (CI-only)
- Spacy models (`fr_core_news_lg`, `fr_core_news_sm`) downloaded from GitHub releases on first run
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Mixed French/English convention observed
- Model modules use French names: `Analyse_NLTK.py`, `operation_fichier.py`, `exportation.py`, `memo.py`, `audio_worker.py`, `transcription.py`
- View/Widget files use PascalCase (Qt convention): `Enregistrement.py`, `Home.py`, `ImporterAudio.py`, `Metrique.py`, `Parametres.py`, `CorrectionTranscription.py`
- Controller files use mixed case with underscores: `Menu_controllers.py`, `Player_controllers.py`, `Record_controllers.py`, `Transcription_worker.py`, `Result_worker.py`
- Test files use lowercase with underscores: `test_analyse_nltk.py`, `test_controllers.py`, `test_feuille.py`, `test_pdf_export.py`
- PascalCase for all classes: `Analyse_NLTK`, `AudioSegment` (imported), `Document` (imported)
- Snake_case for pure functions: `custom_tokenize()`, `extraire_mapping_depuis_segments()`, `ajuster_mapping()`, `exporte_json()`, `file_size_Mo()`, `find_ffmpeg()`
- Private functions prefixed with single underscore: `_get_whisper_model()`, `_load_assets()`, `_validate_audio_file()`, `_stub_if_missing()`
- Double underscore for name-mangling in classes: `__init__()`, `__sub_punc()`, `__num2words()`, `__token_spacy()`
- Snake_case for variables and parameters: `ancien_text`, `nouveau_text`, `combined_segments`, `file_path`, `tmp_path`
- Module-level constants (cache): `_WHISPER_MODEL`, `_WHISPER_MODEL_KEY`, `_ASSETS_CACHE`, `FORMAT_FROM_EXT`, `AUDIO_MIME_WHITELIST`
- Loop counters: `i`, `current_index`
- `UPPER_SNAKE_CASE` for constants: `APP_ROOT`, `FORMAT_FROM_EXT`, `AUDIO_MIME_WHITELIST`, `AUDIO_WHITELIST_EXTS`, `modele_dispo` (list of available models)
## Documentation & Comments
- Docstrings written in French (primary)
- File headers with author, email, version (legacy convention, present in most modules)
- Comments in French, matching the codebase language
- English comments appear only in test files and some configuration
- Triple-quoted strings (not type-annotated formal docstrings, mostly informal descriptions)
- Format: Description + Arguments + Return value sections in French
- Example from `app/models/transcription.py`:
- **CRITICAL**: Patient text/transcripts (`texte` field in export data) MUST NEVER be logged
- Only use `logging` module for data that is not patient-identifying
- Pattern: Comments explicitly note "Texte de transcription d'exemple" in test fixtures, never real patient data
- Logging setup in `app/config.py` uses `INFO` level by default
- `print()` statements are discouraged in production modules; use `logging` instead
## Code Style
- No auto-formatter configuration detected (no `.black.toml`, `.ruff.toml`, or `.flake8` config)
- No explicit linting enforced via CI (CI only runs tests with coverage)
- Default Python line length appears lenient (observed lines up to ~120 characters)
- Imports organized: stdlib → third-party → local (standard PEP 8)
- Path aliasing used: `from app.models import operation_fichier` (app is in sys.path via `pythonpath = ["."]` in pytest config)
- Module-level side effects allowed: `import app.config` deliberately triggers `logging.basicConfig()` as documented
- Type stubs for heavy dependencies: `# type: ignore` used for optional/complex packages
- **INCONSISTENT**: Type hints present on some public functions, absent on others
- Present on: `def __init__(self, text: str = "")`, `def sent_size(self) -> int:`, `def _get_whisper_model(model_name: str, device: str)`
- Absent on: `def __sub_punc(self, text=None)`, `def word_treatment(self)`, `def custom_tokenize(text)`, `def extraire_mapping_depuis_segments(combined_segments)`
- Pattern: Recent refactoring added `from __future__ import annotations` to test files but NOT to source modules
- Recommendation: Older modules lack full type hints; newer code in `conftest.py` uses full annotations
## Logging Patterns
- Centralized in `app/config.py` which configures `logging.basicConfig()` as a module-level side effect
- Format: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`
- Level: `logging.INFO`
- Discouraged in production modules but still present in some legacy code (`app/models/memo.py`)
- Commented-out print statements in `app/models/exportation.py` suggest gradual migration to logging
- Tests use standard `assert` statements, not prints
## Error Handling
- Try-except blocks with specific exception types preferred
- Example from `app/models/operation_fichier.py`:
- Raise explicit errors with context: `raise ValueError(f"unsupported audio extension: {ext!r}")`
- Graceful degradation: When optional features unavailable (e.g., python-magic), code logs warning and continues
- Use `pytest.raises()` context manager: `with pytest.raises(OSError):`
- Test both success and error cases (observed in `test_feuille.py`, `test_pdf_export.py`)
## Function Design
- Private helper functions use parameters without type hints (older code)
- Public module functions increasingly use type hints
- Mutable defaults avoided (use `None` pattern)
- Functions return single values or tuples for multi-value returns
- Example: `extraire_mapping_depuis_segments()` returns `(text: str, mapping: list[tuple])`
- No implicit None returns; functions either return data or raise exception
## Module Organization
- `app/models/` — Pure business logic, data processing, export helpers
- `app/controllers/` — Qt signal/slot bridges (excluded from test coverage)
- `app/Views/` — PySide6 widget definitions (excluded from test coverage)
- `app/Widgets/` — Reusable Qt components (excluded from test coverage)
- `app/config.py` — Centralized config, APP_ROOT resolution, logging setup
- `app/main.py` — Entry point (excluded from test coverage)
- `Analyse_NLTK.py` — Single class with linguistic analysis methods
- `operation_fichier.py` — Utility functions for file operations, audio format detection, ffmpeg discovery
- `exportation.py` — Export helper functions (JSON, TXT, CSV, PDF, DOCX)
- `transcription.py` — Whisper transcription pipeline + mapping functions
- `Analyse_NLTK._load_assets()` — Lazy-loads JSON prefix/suffix tables to avoid module-level I/O crashes
- `transcription._get_whisper_model()` — Module-level cache for Whisper models (expensive to load)
- Pattern: Check cache before loading; initialize once per process
## Comments Style
- Non-obvious algorithm choices (e.g., morpheme detection regex)
- Workarounds and known limitations
- References to external tracking (e.g., "Tracked separately" for known bugs)
- Self-explanatory code rarely commented
- No inline comments for obvious operations
## Security Considerations
- No hardcoded API keys detected
- Environment variables not used in current codebase (no `.env` read observed)
- Tests use fixtures with sample data, never real credentials
- Audio file validation: Extension + MIME whitelist in `operation_fichier._validate_audio_file()`
- MIME sniffing used when `python-magic` available (SEC-F2)
- Tempfile cleanup implemented for converted audio (SEC-F4)
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Desktop GUI framework using PySide6.QtWidgets (QMainWindow, QStackedWidget for page navigation)
- Singleton NavigationController manages global state and page transitions
- Worker threads (QRunnable) for long-running operations (transcription, linguistic analysis)
- Signal-slot architecture for asynchronous communication between components
- Lazy-loaded spaCy/NLTK assets to avoid module-level I/O
## Layers
- Purpose: Display content and capture user interaction via PySide6 widgets
- Location: `app/Views/` (page-based views), `app/Widgets/` (reusable UI components)
- Contains: QWidget-based views (Transcription.py, Metrique.py, CorrectionTranscription.py), custom widgets (Feuille.py for text editing, AudioPlayer.py for playback)
- Depends on: Controllers (NavigationController), signal-slot connections to models
- Used by: QMainWindow (mainWindow.py) which stacks views in QStackedWidget
- Purpose: Orchestrate navigation, state management, and coordination between views and models
- Location: `app/controllers/`
- Contains: NavigationController (singleton), worker threads (Transcription_worker.py, Result_worker.py), domain-specific controllers (Player_controllers.py, Record_controllers.py, Settings_controller.py)
- Depends on: Models (Analyse_NLTK, transcription), Views
- Used by: Views to trigger navigation and state changes; workers to emit signals
- Purpose: Implement core algorithms and data transformations
- Location: `app/models/`
- Contains: 
- Depends on: External libraries (whisper, nltk, spacy, num2words, pydocx), file system
- Used by: Controllers and workers
- Location: `app/assets/` (fonts, SVGs, images) + `app/config.py` (APP_ROOT path resolution, logging setup)
- Contains: Poppins/Inter/Montserrat fonts, JSON assets (suffixe.json, prefixe.json for morphological analysis)
## Data Flow
```
```
```
```
```
```
```
```
```
```
- NavigationController (singleton) maintains:
- Views read state via `controller.get_*()` methods
- Models modify state via controller.set_*() slots
## Key Abstractions
- Purpose: Synchronize audio playback with text highlighting
- Files: `app/models/transcription.py`, `app/Widgets/Feuille.py`
- Pattern: List of tuples `[(start_time_s, end_time_s, start_char_idx, end_char_idx), ...]`
- Functions:
- Purpose: Single interface to compute linguistic metrics
- Files: `app/models/Analyse_NLTK.py`
- Pattern: Instance per analysis (new instance in ControllerLoaderWorker.run())
- Key Methods:
- Purpose: Adapt Analyse_NLTK output to UI metric display (count + percentage score)
- Files: `app/controllers/Result_controllers.py`
- Pattern: Wraps Analyse_NLTK instance, reads settings.json for ratio baselines, calculates percentage = (count * 50) / (baseline * multiplicateur)
- Multiplicateur: Audio duration normalization factor relative to settings baseline
- Purpose: Reusable form-like widget for text display + editing + buttons
- Files: `app/Widgets/Feuille.py`
- Pattern: Custom QPlainTextEdit with real-time highlight sync via `mettre_a_jour_surlignage()` callback
- Features:
- Purpose: Unified audio playback control across all transcription views
- Files: `app/Widgets/AudioPlayer.py`
- Pattern: Cached singleton instance stored in NavigationController (reused across Transcription ↔ CorrectionTranscription)
- Signals: `position_en_secondes` emits current position in seconds on every tick
- Features: Play/pause toggle, 10s rewind/forward, seekbar with HoverSlider
## Entry Points
- Location: `app/main.py`
- Triggers: `python -m app.main` or exe launcher
- Responsibilities: 
- Location: `app/Views/mainWindow.py` class MyWindow
- Triggers: `app.main.py` instantiation
- Responsibilities:
- Via: NavigationController.change_page(page_name)
- Loads modules dynamically: importlib.import_module() + getattr() for class instantiation
- Special handling for Transcription/CorrectionTranscription: recreate widget each time (remove old, add new) to reset state
- Other pages: lazy-load once and reuse
## Error Handling
- `Transcription_worker.TranscriptionRunnable.run()`: Calls transcription() which may raise on file I/O or Whisper errors → logged, signal emitted
- `Result_worker.ControllerLoaderWorker.run()`: Wrapped in try-except, emits error signal with traceback
- `transcription.transcription()`: File checks before processing (file_size_Mo, file_size_sec); falls back to CPU if CUDA unavailable
- Model layer: Exception propagates to caller (worker); caller logs and handles gracefully
## Cross-Cutting Concerns
- Location: `app/config.py` - basicConfig setup on import
- Pattern: `import logging; logger = logging.getLogger(__name__)` in every module
- Usage: Log at DEBUG level for word counts/segment counts; INFO for major operations (model loaded, transcription finished); ERROR for exceptions
- RGPD: Never log patient text (sensitive); log only counts and operation messages
- Audio file format: `reel_file_format()` checks extension
- Audio size: `file_size_Mo()`, `file_size_sec()` enforce thresholds
- Whisper model: Cached to avoid reloading 800MB-1.5GB per transcription
- Text edits: ajuster_mapping() validates indices before applying highlight
- Not applicable - single-user desktop app
- Location: `app/assets/JSON/settings.json` - user-editable Whisper model choice, ratio baselines for metrics
- Loading: Settings read once per analysis session in Result_worker
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
