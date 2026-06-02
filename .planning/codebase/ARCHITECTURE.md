# Architecture

**Analysis Date:** 2026-06-02

## Pattern Overview

**Overall:** Model-View-Controller (MVC) with Qt6 PySide6 desktop application

**Key Characteristics:**
- Desktop GUI framework using PySide6.QtWidgets (QMainWindow, QStackedWidget for page navigation)
- Singleton NavigationController manages global state and page transitions
- Worker threads (QRunnable) for long-running operations (transcription, linguistic analysis)
- Signal-slot architecture for asynchronous communication between components
- Lazy-loaded spaCy/NLTK assets to avoid module-level I/O

## Layers

**Views (UI Layer):**
- Purpose: Display content and capture user interaction via PySide6 widgets
- Location: `app/Views/` (page-based views), `app/Widgets/` (reusable UI components)
- Contains: QWidget-based views (Transcription.py, Metrique.py, CorrectionTranscription.py), custom widgets (Feuille.py for text editing, AudioPlayer.py for playback)
- Depends on: Controllers (NavigationController), signal-slot connections to models
- Used by: QMainWindow (mainWindow.py) which stacks views in QStackedWidget

**Controllers (Application Logic Layer):**
- Purpose: Orchestrate navigation, state management, and coordination between views and models
- Location: `app/controllers/`
- Contains: NavigationController (singleton), worker threads (Transcription_worker.py, Result_worker.py), domain-specific controllers (Player_controllers.py, Record_controllers.py, Settings_controller.py)
- Depends on: Models (Analyse_NLTK, transcription), Views
- Used by: Views to trigger navigation and state changes; workers to emit signals

**Models (Business Logic Layer):**
- Purpose: Implement core algorithms and data transformations
- Location: `app/models/`
- Contains: 
  - `transcription.py` - Whisper model orchestration + word-level timestamp extraction/mapping
  - `Analyse_NLTK.py` - Linguistic analysis (morphemes, lemmas, sentence counts, unique words via nltk/spacy)
  - `exportation.py` - PDF/DOCX/JSON/CSV/TXT export
  - `operation_fichier.py` - File operations (audio extraction, splitting, formatting)
  - `audio_worker.py` - Audio recording backend
  - `memo.py` - In-memory data management
- Depends on: External libraries (whisper, nltk, spacy, num2words, pydocx), file system
- Used by: Controllers and workers

**Assets & Configuration:**
- Location: `app/assets/` (fonts, SVGs, images) + `app/config.py` (APP_ROOT path resolution, logging setup)
- Contains: Poppins/Inter/Montserrat fonts, JSON assets (suffixe.json, prefixe.json for morphological analysis)

## Data Flow

**1. Transcription Pipeline:**
```
Audio File
  ↓ [ImporterAudio view]
  ↓ [Menu_controllers.change_page("ModeDeChargement")]
  ↓ [Prenregistrement or Enregistrement view]
  ↓ [Record_controllers + audio_worker.py]
  ↓ [Transcription_worker.TranscriptionRunnable.run()]
     ├─ transcription.transcription(file_path) - Whisper model loads from cache (_WHISPER_MODEL)
     ├─ Audio format check + extraction (MP4→WAV)
     ├─ File size check + split if >25MB or >10min
     ├─ word_timestamps=True passed to whisper.transcribe()
     └─ extraire_mapping_depuis_segments() - Maps each word to (start_time, end_time, text_indices)
  ↓ [Controller stores: text_transcription, mapping_data]
  ↓ [change_page("Transcription")] - View receives both as constructor args
  ↓ [Transcription view + Feuille widget + AudioPlayer]
```

**2. Audio Synchronization Flow:**
```
AudioPlayer.player.positionChanged
  ↓ [AudioPlayer.update_position() emits position_en_secondes(float)]
  ↓ [Transcription.on_position_changed(current_time_s)]
  ↓ [Feuille.mettre_a_jour_surlignage(current_time, mapping_data)]
     ├─ Find segment where start_t <= current_time < end_t
     ├─ Extract (start_idx, end_idx) from mapping tuple
     └─ Highlight text[start_idx:end_idx] in QPlainTextEdit with yellow QBrush
```

**3. Correction & Editing Flow:**
```
Transcription.feuille.text_edit (read-only)
  ↓ [User clicks "Corriger"]
  ↓ [change_page("CTanscription")] - CorrectionTranscription view
  ↓ [Feuille widget with setReadOnly(False)]
  ↓ [User edits text]
  ↓ [text_edit.textChanged → controller.change_text()]
  ↓ [ajuster_mapping(old_text, new_text, old_mapping)] - Recalculates indices
  ↓ [Highlight updates on position changes]
  ↓ [User clicks "Valider"] 
  ↓ [set_text_transcription(modified_text)]
  ↓ [change_page("Transcription")] - Back to read-only view
```

**4. Linguistic Analysis Flow:**
```
Transcription.feuille text_edit (read-only)
  ↓ [User clicks "Analyser"]
  ↓ [Metrique view.showEvent()]
  ↓ [LoaderWidget displayed]
  ↓ [Result_worker.ControllerLoaderWorker.run() in thread pool]
     ├─ text = get_enonce_pertinant() if marked else full text
     ├─ ResultController.__init__() instantiates Analyse_NLTK(text)
     └─ Analyse_NLTK triggers spacy.load("fr_core_news_lg") + asset lazy-load
  ↓ [ResultController.get_* methods called in Metrique.container()]
     ├─ get_word() → word_treatment() → nltk tokenize
     ├─ get_dif_word() → unique word set
     ├─ get_morpheme() → morphem() counts prefix/suffix/infix via Snowball + JSON assets
     ├─ get_enonce() → sent_size() → nltk sentence tokenize
     ├─ get_lemme() → calc_lemme() → spacy lemmatizer
     └─ Each returns [count, percentage_score]
  ↓ [Percentage = (count * 50) / (ratio * multiplicateur)]
  ↓ [Metrique displays cards with counts + score bars]
```

**5. Export Flow:**
```
Metrique view
  ↓ [User clicks export button]
  ↓ [File dialog → select path]
  ↓ [ResultController.export_pdf/json/csv/txt/docx(path)]
  ↓ [Relevant exportation.py function (exporte_pdf, exporte_json, etc.)]
  ↓ [PDF/Excel/JSON file written]
```

**State Management:**
- NavigationController (singleton) maintains:
  - `text_transcription` - Current transcription text
  - `mapping_data` - Word→audio timestamp mapping
  - `file_transcription_path` - Audio file path
  - `position` (audio_player reference) - Playback state
  - `enonce_pertinant` - Marked relevant utterances from text_edit
- Views read state via `controller.get_*()` methods
- Models modify state via controller.set_*() slots

## Key Abstractions

**1. Mapping Data Structure:**
- Purpose: Synchronize audio playback with text highlighting
- Files: `app/models/transcription.py`, `app/Widgets/Feuille.py`
- Pattern: List of tuples `[(start_time_s, end_time_s, start_char_idx, end_char_idx), ...]`
  - `start_time_s / end_time_s` - Absolute audio timestamps from whisper word_timestamps
  - `start_char_idx / end_char_idx` - Character offsets in the combined transcription text
- Functions:
  - `extraire_mapping_depuis_segments()` - Combines Whisper segments + word timestamps into unified mapping
  - `ajuster_mapping()` - Recalculates indices when user edits text (handles token count changes)
  - `custom_tokenize()` - Splits text on spaces but recombines apostrophe-split tokens (m'appeler stays as 1 token)

**2. Analyse_NLTK Class:**
- Purpose: Single interface to compute linguistic metrics
- Files: `app/models/Analyse_NLTK.py`
- Pattern: Instance per analysis (new instance in ControllerLoaderWorker.run())
- Key Methods:
  - `word_treatment()` - NLTK word tokenize after number expansion (num2words)
  - `sent_size()` - Count sentences via NLTK sent_tokenize
  - `morphem()` - Boolean dict per word {prefixe, infixe, suffixe} via Snowball stem + JSON suffix/prefix lists
  - `mlcu()` - Mean Length of Communication Unit = words / sentences
  - `calc_lemme()` - Unique lemmas via spacy + comparison with NLTK tokens
  - Lazy-loads: `spacy.load("fr_core_news_lg")`, assets/{suffixe.json, prefixe.json}

**3. ResultController Wrapper:**
- Purpose: Adapt Analyse_NLTK output to UI metric display (count + percentage score)
- Files: `app/controllers/Result_controllers.py`
- Pattern: Wraps Analyse_NLTK instance, reads settings.json for ratio baselines, calculates percentage = (count * 50) / (baseline * multiplicateur)
- Multiplicateur: Audio duration normalization factor relative to settings baseline

**4. Feuille (Sheet) Widget:**
- Purpose: Reusable form-like widget for text display + editing + buttons
- Files: `app/Widgets/Feuille.py`
- Pattern: Custom QPlainTextEdit with real-time highlight sync via `mettre_a_jour_surlignage()` callback
- Features:
  - Read-only vs editable modes
  - Background highlighting (QBrush with QColor) for current playback word
  - Enonce pertinant marking: wrap selected text with `+text+` to flag relevant utterances (stored in `enonce_history` per instance)
  - Context menu for operations

**5. AudioPlayer Widget:**
- Purpose: Unified audio playback control across all transcription views
- Files: `app/Widgets/AudioPlayer.py`
- Pattern: Cached singleton instance stored in NavigationController (reused across Transcription ↔ CorrectionTranscription)
- Signals: `position_en_secondes` emits current position in seconds on every tick
- Features: Play/pause toggle, 10s rewind/forward, seekbar with HoverSlider

## Entry Points

**Application Entry:**
- Location: `app/main.py`
- Triggers: `python -m app.main` or exe launcher
- Responsibilities: 
  - Create QApplication
  - Instantiate MyWindow (QMainWindow)
  - Show window
  - Execute event loop

**Window Entry:**
- Location: `app/Views/mainWindow.py` class MyWindow
- Triggers: `app.main.py` instantiation
- Responsibilities:
  - Initialize QStackedWidget for page navigation
  - Load Home view as first page
  - Create NavigationController singleton and set main_window reference
  - Build toolbar with navigation actions (Accueil, Enregistrer, Import, Parametres, Info)
  - Define page action shortcuts (Alt+A, etc.)

**Page Navigation:**
- Via: NavigationController.change_page(page_name)
- Loads modules dynamically: importlib.import_module() + getattr() for class instantiation
- Special handling for Transcription/CorrectionTranscription: recreate widget each time (remove old, add new) to reset state
- Other pages: lazy-load once and reuse

## Error Handling

**Strategy:** Try-except blocks at worker boundaries; logging (never print) for all error paths

**Patterns:**
- `Transcription_worker.TranscriptionRunnable.run()`: Calls transcription() which may raise on file I/O or Whisper errors → logged, signal emitted
- `Result_worker.ControllerLoaderWorker.run()`: Wrapped in try-except, emits error signal with traceback
- `transcription.transcription()`: File checks before processing (file_size_Mo, file_size_sec); falls back to CPU if CUDA unavailable
- Model layer: Exception propagates to caller (worker); caller logs and handles gracefully

## Cross-Cutting Concerns

**Logging:** 
- Location: `app/config.py` - basicConfig setup on import
- Pattern: `import logging; logger = logging.getLogger(__name__)` in every module
- Usage: Log at DEBUG level for word counts/segment counts; INFO for major operations (model loaded, transcription finished); ERROR for exceptions
- RGPD: Never log patient text (sensitive); log only counts and operation messages

**Validation:**
- Audio file format: `reel_file_format()` checks extension
- Audio size: `file_size_Mo()`, `file_size_sec()` enforce thresholds
- Whisper model: Cached to avoid reloading 800MB-1.5GB per transcription
- Text edits: ajuster_mapping() validates indices before applying highlight

**Authentication & Authorization:** 
- Not applicable - single-user desktop app

**Configuration:**
- Location: `app/assets/JSON/settings.json` - user-editable Whisper model choice, ratio baselines for metrics
- Loading: Settings read once per analysis session in Result_worker

---

*Architecture analysis: 2026-06-02*
