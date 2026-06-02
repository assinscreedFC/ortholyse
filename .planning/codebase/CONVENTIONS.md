# Coding Conventions

**Analysis Date:** 2026-06-02

## Naming Patterns

**Files:**
- Mixed French/English convention observed
- Model modules use French names: `Analyse_NLTK.py`, `operation_fichier.py`, `exportation.py`, `memo.py`, `audio_worker.py`, `transcription.py`
- View/Widget files use PascalCase (Qt convention): `Enregistrement.py`, `Home.py`, `ImporterAudio.py`, `Metrique.py`, `Parametres.py`, `CorrectionTranscription.py`
- Controller files use mixed case with underscores: `Menu_controllers.py`, `Player_controllers.py`, `Record_controllers.py`, `Transcription_worker.py`, `Result_worker.py`
- Test files use lowercase with underscores: `test_analyse_nltk.py`, `test_controllers.py`, `test_feuille.py`, `test_pdf_export.py`

**Classes:**
- PascalCase for all classes: `Analyse_NLTK`, `AudioSegment` (imported), `Document` (imported)

**Functions:**
- Snake_case for pure functions: `custom_tokenize()`, `extraire_mapping_depuis_segments()`, `ajuster_mapping()`, `exporte_json()`, `file_size_Mo()`, `find_ffmpeg()`
- Private functions prefixed with single underscore: `_get_whisper_model()`, `_load_assets()`, `_validate_audio_file()`, `_stub_if_missing()`
- Double underscore for name-mangling in classes: `__init__()`, `__sub_punc()`, `__num2words()`, `__token_spacy()`

**Variables:**
- Snake_case for variables and parameters: `ancien_text`, `nouveau_text`, `combined_segments`, `file_path`, `tmp_path`
- Module-level constants (cache): `_WHISPER_MODEL`, `_WHISPER_MODEL_KEY`, `_ASSETS_CACHE`, `FORMAT_FROM_EXT`, `AUDIO_MIME_WHITELIST`
- Loop counters: `i`, `current_index`

**Constants:**
- `UPPER_SNAKE_CASE` for constants: `APP_ROOT`, `FORMAT_FROM_EXT`, `AUDIO_MIME_WHITELIST`, `AUDIO_WHITELIST_EXTS`, `modele_dispo` (list of available models)

## Documentation & Comments

**Language:**
- Docstrings written in French (primary)
- File headers with author, email, version (legacy convention, present in most modules)
- Comments in French, matching the codebase language
- English comments appear only in test files and some configuration

**Docstring Style:**
- Triple-quoted strings (not type-annotated formal docstrings, mostly informal descriptions)
- Format: Description + Arguments + Return value sections in French
- Example from `app/models/transcription.py`:
  ```python
  def extraire_mapping_depuis_segments(combined_segments):
      """
      Combine les segments en un seul texte global et crée un mapping mot par mot.
      ...
      Arguments :
          combined_segments (list): ...
      Retourne :
          tuple: (texte_global, mapping_data)
      """
  ```

**Patient Data Privacy (RGPD):**
- **CRITICAL**: Patient text/transcripts (`texte` field in export data) MUST NEVER be logged
- Only use `logging` module for data that is not patient-identifying
- Pattern: Comments explicitly note "Texte de transcription d'exemple" in test fixtures, never real patient data
- Logging setup in `app/config.py` uses `INFO` level by default
- `print()` statements are discouraged in production modules; use `logging` instead

## Code Style

**Formatting:**
- No auto-formatter configuration detected (no `.black.toml`, `.ruff.toml`, or `.flake8` config)
- No explicit linting enforced via CI (CI only runs tests with coverage)
- Default Python line length appears lenient (observed lines up to ~120 characters)
- Imports organized: stdlib → third-party → local (standard PEP 8)

**Imports:**
- Path aliasing used: `from app.models import operation_fichier` (app is in sys.path via `pythonpath = ["."]` in pytest config)
- Module-level side effects allowed: `import app.config` deliberately triggers `logging.basicConfig()` as documented
- Type stubs for heavy dependencies: `# type: ignore` used for optional/complex packages

**Type Hints Status:**
- **INCONSISTENT**: Type hints present on some public functions, absent on others
- Present on: `def __init__(self, text: str = "")`, `def sent_size(self) -> int:`, `def _get_whisper_model(model_name: str, device: str)`
- Absent on: `def __sub_punc(self, text=None)`, `def word_treatment(self)`, `def custom_tokenize(text)`, `def extraire_mapping_depuis_segments(combined_segments)`
- Pattern: Recent refactoring added `from __future__ import annotations` to test files but NOT to source modules
- Recommendation: Older modules lack full type hints; newer code in `conftest.py` uses full annotations

## Logging Patterns

**Framework:** `logging` module (standard library)

**Setup:**
- Centralized in `app/config.py` which configures `logging.basicConfig()` as a module-level side effect
- Format: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`
- Level: `logging.INFO`

**Usage Pattern:**
```python
import logging
import app.config  # Side effect: configures logging

logger = logging.getLogger(__name__)
logger.info("Message", arg1, arg2)
logger.warning("Warning: %s", var)
```

**Files with logging configured:** `Analyse_NLTK.py`, `audio_worker.py`, `operation_fichier.py`, `transcription.py`, `memo.py`

**Print Statements:**
- Discouraged in production modules but still present in some legacy code (`app/models/memo.py`)
- Commented-out print statements in `app/models/exportation.py` suggest gradual migration to logging
- Tests use standard `assert` statements, not prints

## Error Handling

**Patterns:**
- Try-except blocks with specific exception types preferred
- Example from `app/models/operation_fichier.py`:
  ```python
  try:
      import magic
      _HAS_MAGIC = True
  except Exception:  # ImportError or libmagic native missing
      magic = None
      _HAS_MAGIC = False
  ```
- Raise explicit errors with context: `raise ValueError(f"unsupported audio extension: {ext!r}")`
- Graceful degradation: When optional features unavailable (e.g., python-magic), code logs warning and continues

**Exception Handling in Tests:**
- Use `pytest.raises()` context manager: `with pytest.raises(OSError):`
- Test both success and error cases (observed in `test_feuille.py`, `test_pdf_export.py`)

## Function Design

**Size:** Functions observed range 5–50 lines; larger pipelines broken into sub-functions

**Parameters:**
- Private helper functions use parameters without type hints (older code)
- Public module functions increasingly use type hints
- Mutable defaults avoided (use `None` pattern)

**Return Values:**
- Functions return single values or tuples for multi-value returns
- Example: `extraire_mapping_depuis_segments()` returns `(text: str, mapping: list[tuple])`
- No implicit None returns; functions either return data or raise exception

## Module Organization

**Structure:**
- `app/models/` — Pure business logic, data processing, export helpers
- `app/controllers/` — Qt signal/slot bridges (excluded from test coverage)
- `app/Views/` — PySide6 widget definitions (excluded from test coverage)
- `app/Widgets/` — Reusable Qt components (excluded from test coverage)
- `app/config.py` — Centralized config, APP_ROOT resolution, logging setup
- `app/main.py` — Entry point (excluded from test coverage)

**Cohesion:**
- `Analyse_NLTK.py` — Single class with linguistic analysis methods
- `operation_fichier.py` — Utility functions for file operations, audio format detection, ffmpeg discovery
- `exportation.py` — Export helper functions (JSON, TXT, CSV, PDF, DOCX)
- `transcription.py` — Whisper transcription pipeline + mapping functions

**Lazy Loading & Caching:**
- `Analyse_NLTK._load_assets()` — Lazy-loads JSON prefix/suffix tables to avoid module-level I/O crashes
- `transcription._get_whisper_model()` — Module-level cache for Whisper models (expensive to load)
- Pattern: Check cache before loading; initialize once per process

## Comments Style

**When to Comment:**
- Non-obvious algorithm choices (e.g., morpheme detection regex)
- Workarounds and known limitations
- References to external tracking (e.g., "Tracked separately" for known bugs)

**Example from test:**
```python
@pytest.mark.skip(
    reason="spacy_calc_morphem has an upstream bug "
    "(calls .items() on morphem() which returns int). Tracked separately."
)
```

**Avoid:**
- Self-explanatory code rarely commented
- No inline comments for obvious operations

## Security Considerations

**Secret Management:**
- No hardcoded API keys detected
- Environment variables not used in current codebase (no `.env` read observed)
- Tests use fixtures with sample data, never real credentials

**Input Validation:**
- Audio file validation: Extension + MIME whitelist in `operation_fichier._validate_audio_file()`
- MIME sniffing used when `python-magic` available (SEC-F2)
- Tempfile cleanup implemented for converted audio (SEC-F4)

---

*Convention analysis: 2026-06-02*
