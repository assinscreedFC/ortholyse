# Codebase Structure

**Analysis Date:** 2026-06-02

## Directory Layout

```
ortholyse/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # Entry point: QApplication + MyWindow launch
│   ├── config.py                 # APP_ROOT path resolution + logging.basicConfig
│   │
│   ├── Views/                    # Page-based UI views (QWidget subclasses)
│   │   ├── mainWindow.py         # QMainWindow with QStackedWidget + toolbar
│   │   ├── Home.py               # Landing page with mode selection
│   │   ├── Transcription.py      # Read-only transcription view + sync highlight
│   │   ├── CorrectionTranscription.py  # Editable transcription view
│   │   ├── Metrique.py           # Linguistic analysis results display
│   │   ├── Prenregistrement.py   # Pre-recording setup view
│   │   ├── Enregistrement.py     # Recording in-progress view
│   │   ├── StopEnregistrement.py # Recording complete view
│   │   ├── ImporterAudio.py      # File picker for existing audio
│   │   ├── ModeDeChargement.py   # Choose: record new or import existing
│   │   ├── Parametres.py         # Settings (Whisper model selection)
│   │   ├── Informations.py       # About/help view
│   │   └── base/
│   │       └── base_enregistrement.py  # Base class for record views
│   │
│   ├── Widgets/                  # Reusable UI components (QWidget subclasses)
│   │   ├── Feuille.py           # Custom text editor with highlight sync + enonce marking
│   │   ├── AudioPlayer.py        # Audio playback control + position signal
│   │   ├── HoverSlider.py        # Custom slider with hover tooltip
│   │   ├── AudioBar.py           # Waveform/audio level display
│   │   ├── Loader.py             # Loading spinner animation
│   │   └── [other UI widgets]
│   │
│   ├── controllers/              # Application logic + orchestration
│   │   ├── Menu_controllers.py   # NavigationController singleton (global state)
│   │   ├── Transcription_worker.py   # QRunnable for async transcription
│   │   ├── Result_worker.py      # QRunnable for async analysis + ResultController creation
│   │   ├── Result_controllers.py # ResultController: wraps Analyse_NLTK + metrics
│   │   ├── Player_controllers.py # Audio playback state management
│   │   ├── Record_controllers.py # Recording orchestration
│   │   └── Settings_controller.py # Settings persistence
│   │
│   ├── models/                   # Core business logic + algorithms
│   │   ├── Analyse_NLTK.py      # Linguistic analysis engine (morphemes, lemmas, etc.)
│   │   ├── transcription.py      # Whisper orchestration + word→time mapping
│   │   ├── exportation.py        # PDF/DOCX/JSON/CSV/TXT export functions
│   │   ├── operation_fichier.py  # File I/O (extract audio, split, format check)
│   │   ├── audio_worker.py       # Audio recording backend (WAV recording)
│   │   ├── memo.py              # In-memory data structures
│   │   └── test/
│   │       └── test_Analyse_NLTK.py  # Unit tests for linguistic analysis
│   │
│   └── assets/                   # Static files + configuration
│       ├── JSON/
│       │   ├── settings.json     # User settings (Whisper model, metric baselines)
│       │   ├── suffixe.json      # Morphological suffix list (French)
│       │   └── prefixe.json      # Morphological prefix list (French)
│       ├── Fonts/
│       │   ├── Poppins/          # Main UI font (SemiBold, Bold)
│       │   ├── Inter,Montserrat,Roboto/  # Secondary fonts
│       │   │   ├── Inter/
│       │   │   ├── Montserrat/
│       │   │   └── Roboto/
│       │   └── Inknut_Antiqua/
│       ├── SVG/                  # Vector icons
│       │   └── [*.svg icon files]
│       ├── image/                # Static images
│       ├── GIF/                  # Animated GIFs
│       └── Logo/                 # Application logo (logo2.svg)
│
├── tests/                        # Integration/E2E tests
├── ortholyse.egg-info/           # Package metadata
└── [config files: setup.py, pyproject.toml, etc.]
```

## Directory Purposes

**`app/`**
- Purpose: Root package containing all application code
- Contains: Views, Widgets, controllers, models, assets, configuration
- Key files: `main.py` (entry), `config.py` (initialization)

**`app/Views/`**
- Purpose: Page-level UI components displayed via QStackedWidget
- Contains: QWidget subclasses implementing distinct application screens
- Key files: `mainWindow.py` (orchestrator), `Transcription.py` (main flow), `Metrique.py` (results)
- Pattern: Each view is a full-screen widget; views are added to QStackedWidget and switched via NavigationController

**`app/Widgets/`**
- Purpose: Reusable UI building blocks
- Contains: Custom QWidget subclasses (Feuille for editing, AudioPlayer for playback, etc.)
- Key files: `Feuille.py` (complex form), `AudioPlayer.py` (playback control)
- Pattern: Instantiated and embedded in Views; emit signals for user interaction

**`app/controllers/`**
- Purpose: Application logic, state management, worker orchestration
- Contains: NavigationController (singleton, global state), worker threads, domain-specific controllers
- Key files: `Menu_controllers.py` (central hub), `Transcription_worker.py` (async transcription), `Result_worker.py` + `Result_controllers.py` (async analysis)
- Pattern: Controllers coordinate Views ↔ Models; workers run long operations off main thread

**`app/models/`**
- Purpose: Core algorithms and data transformations
- Contains: Whisper integration, linguistic analysis, file I/O, export functions
- Key files: `transcription.py` (word mapping), `Analyse_NLTK.py` (metrics engine), `exportation.py` (output formats)
- Pattern: Stateless or single-use instances; called from workers or controllers

**`app/assets/JSON/`**
- Purpose: Data files for algorithm configuration
- Contains: 
  - `settings.json` - Whisper model choice, metric ratio baselines (user-editable)
  - `suffixe.json` - French suffix list for morphological analysis
  - `prefixe.json` - French prefix list for morphological analysis
- Lazy-loaded in `Analyse_NLTK._load_assets()` to avoid module-level I/O

**`app/assets/Fonts/`**
- Purpose: Custom fonts for UI rendering
- Contains: Poppins (primary), Inter/Montserrat/Roboto (secondary)
- Usage: Loaded via QFontDatabase in controller.set_font() method

**`app/assets/SVG/` and `app/assets/Logo/`**
- Purpose: Vector icons and application branding
- Contains: Button icons, window icon, decorative SVGs
- Pattern: Referenced as relative paths from app root (e.g., `./assets/SVG/play_arrow.svg`)

**`tests/`**
- Purpose: Project-level test suite
- Contains: Integration tests, E2E tests
- Pattern: Run with pytest

## Key File Locations

**Entry Points:**
- `app/main.py` - Application launcher (QApplication + MyWindow)
- `app/Views/mainWindow.py` - Main window (QMainWindow, QStackedWidget, toolbar)
- `app/controllers/Menu_controllers.py` class NavigationController - Global state manager (singleton)

**Configuration:**
- `app/config.py` - APP_ROOT resolution, logging setup
- `app/assets/JSON/settings.json` - Whisper model, metric baselines

**Core Logic:**
- `app/models/transcription.py` - Whisper transcription + word→time mapping
- `app/models/Analyse_NLTK.py` - Linguistic metrics (morphemes, lemmas, sentences, unique words)
- `app/controllers/Result_controllers.py` - ResultController: UI-friendly metrics wrapper

**Synchronization:**
- `app/models/transcription.py` functions:
  - `extraire_mapping_depuis_segments()` - Create word→timestamp mapping
  - `ajuster_mapping()` - Update mapping on text edit
  - `custom_tokenize()` - Split text (handles apostrophes)
- `app/Widgets/Feuille.py` method:
  - `mettre_a_jour_surlignage(current_time, mapping_data)` - Highlight sync callback

**UI Components:**
- `app/Widgets/Feuille.py` - Text editor with highlight
- `app/Widgets/AudioPlayer.py` - Playback control
- `app/Views/Transcription.py` - Main transcription view
- `app/Views/CorrectionTranscription.py` - Editable transcription view
- `app/Views/Metrique.py` - Analysis results display

**Export:**
- `app/models/exportation.py` - PDF/DOCX/JSON/CSV/TXT export functions

**Workers:**
- `app/controllers/Transcription_worker.py` - QRunnable for async transcription
- `app/controllers/Result_worker.py` - QRunnable for async analysis

## Naming Conventions

**Files:**
- `CamelCase.py` - Views, controllers, widgets (e.g., `Transcription.py`, `Menu_controllers.py`)
- `snake_case.py` - Models and utilities (e.g., `transcription.py`, `operation_fichier.py`)
- `*_worker.py` - Worker threads (e.g., `Transcription_worker.py`, `Result_worker.py`)

**Directories:**
- `Views/` - UI page-level components
- `Widgets/` - Reusable UI components
- `controllers/` - Application logic + state management
- `models/` - Business logic + algorithms
- `assets/` - Static files (fonts, icons, JSON configs)

**Classes:**
- PascalCase (e.g., `NavigationController`, `Analyse_NLTK`, `Feuille`)
- Widgets inherit from QWidget, QMainWindow, QPlainTextEdit, etc.
- Workers inherit from QRunnable

**Methods:**
- `camelCase` (PySide6 convention for Qt methods/slots)
- Signal callbacks: `on_*` prefix (e.g., `on_position_changed`, `on_text_changed`)
- Internal helpers: `_method_name` (single underscore)

**Constants:**
- `UPPER_SNAKE_CASE` in `config.py` (e.g., `APP_ROOT`)
- Model choices: `modele_dispo = ["base", "small", "medium", "turbo"]` in `transcription.py`

## Where to Add New Code

**New Feature (e.g., new page/analysis):**
- UI layer: Create `app/Views/NewFeature.py` inheriting QWidget
  - Constructor takes input parameters (text, mapping_data, etc.)
  - Implement `ui()` method to build layout
  - Connect signals to controller methods
- Controller logic: Add state + orchestration in `app/controllers/Menu_controllers.py`
  - Register page in `change_page()` pages dict
  - Add getter/setter for feature state
- Model logic: Add functions to `app/models/` or create new module
  - Implement algorithm or data transformation
  - Avoid Qt imports in models (models are framework-agnostic)

**New Component/Widget:**
- Create `app/Widgets/MyComponent.py` inheriting QWidget (or appropriate Qt base class)
- Define signals for user interaction (e.g., `Signal(str)` for text changes)
- Implement layout in `__init__` or separate method (like `body()` in Feuille)
- Include context menu / keyboard shortcuts if appropriate
- Instantiate in Views as needed

**Utilities/Helpers:**
- Shared across modules: Add to existing model file (e.g., `operation_fichier.py`)
- File I/O: Add to `app/models/operation_fichier.py`
- Linguistic helpers: Add methods to `Analyse_NLTK` class or separate module
- Export formats: Add to `app/models/exportation.py`

**New Worker Thread:**
- Create `app/controllers/NewOperation_worker.py`
- Define `WorkerSignals(QObject)` with relevant signals
- Implement `WorkerRunnable(QRunnable)` with `run()` method
- Call from controller: `worker = NewOperationWornable(...); thread_pool.start(worker)`
- Connect signals in calling view to handle results

**New Asset:**
- Static file (font, icon, image): Add to `app/assets/[Fonts|SVG|image|etc]/`
- JSON config: Add to `app/assets/JSON/` with descriptive name
- Update `config.py` or relevant loader if path needs APP_ROOT resolution

**Tests:**
- Unit tests: `app/models/test/test_module.py` (co-located with model)
- Integration tests: `tests/test_feature.py`
- Use pytest framework + fixtures for setup/teardown

## Special Directories

**`app/assets/`**
- Purpose: Static resources + configuration data
- Generated: No (all checked into git)
- Committed: Yes (fonts, icons, JSON configs are source assets)
- Pattern: Accessed via APP_ROOT / "assets" / [subdir] for cross-platform path resolution

**`app/models/test/`**
- Purpose: Unit tests for model layer
- Generated: No (test code checked in)
- Committed: Yes
- Pattern: Pytest with fixtures; tests are co-located with models for easy maintenance

**`ortholyse.egg-info/`**
- Purpose: Package metadata (auto-generated by setuptools)
- Generated: Yes (on `pip install -e .`)
- Committed: No (ignored by .gitignore)

**`__pycache__/`**
- Purpose: Python compiled bytecode cache
- Generated: Yes (auto)
- Committed: No (ignored by .gitignore)

---

*Structure analysis: 2026-06-02*
