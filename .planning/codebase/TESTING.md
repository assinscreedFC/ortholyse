# Testing Patterns

**Analysis Date:** 2026-06-02

## Test Framework

**Runner:**
- pytest 8.0+
- Config: `pyproject.toml`
- Test discovery: `testpaths = ["tests"]`
- Python 3.12 (from CI matrix)

**Assertion Library:**
- Standard `assert` statements (pytest introspection)
- `pytest.raises()` for exception testing
- `pytest.approx()` for floating-point comparisons

**Coverage Tool:**
- pytest-cov 5.0+
- Configuration enforces 80% minimum (`--cov-fail-under=80`)
- Reports: terminal-missing + XML (for CI artifact upload)

**Mocking:**
- pytest-mock 3.12+ (provides `monkeypatch` fixture)
- `unittest.mock.MagicMock` for heavy dependencies
- `patch.object()` for specific method mocking

**Run Commands:**
```bash
pytest                           # Run all tests with coverage gate (80% minimum)
pytest -v                        # Verbose output
pytest tests/test_analyse_nltk.py  # Run specific test file
pytest -k test_name              # Run tests matching pattern
pytest --cov=app --cov-report=term-missing  # View coverage
```

## Test File Organization

**Location:**
- Primary: `tests/` directory (pytest-configured testpath)
- Legacy: `app/models/test/test_Analyse_NLTK.py` (excluded from coverage via `norecursedirs`)

**File Naming:**
- Prefix: `test_`
- Pattern: `test_{module_name}.py`
- Examples:
  - `tests/test_analyse_nltk.py` — Tests for `app/models/Analyse_NLTK.py`
  - `tests/test_controllers.py` — Tests for `app/models/transcription.py` (pure functions only)
  - `tests/test_feuille.py` — Tests for `app/models/operation_fichier.py`
  - `tests/test_pdf_export.py` — Tests for `app/models/exportation.py`

**Directory Structure:**
```
tests/
├── __init__.py          # Makes tests/ a package
├── conftest.py          # Shared fixtures + heavy dependency mocks
├── test_analyse_nltk.py # Linguistic analysis tests
├── test_controllers.py  # Transcription pipeline tests
├── test_feuille.py      # File operation & audio handling tests
├── test_pdf_export.py   # Export (JSON/TXT/CSV/PDF/DOCX) tests
└── __pycache__/         # Pytest cache
```

## Test Structure (Class-Based Organization)

**Pattern:** Class-based test organization (pytest supports this idiomatically)

```python
class TestSentenceSegmentation:
    def test_single_sentence(self):
        an = Analyse_NLTK("Une seule phrase.")
        assert an.sent_size() == 1

    def test_three_sentences(self):
        an = Analyse_NLTK("Premiere phrase. Deuxieme phrase. Troisieme phrase.")
        assert an.sent_size() == 3

class TestWordTreatment:
    def test_simple_sentence_tokens(self):
        an = Analyse_NLTK("Bonjour le monde.")
        tokens = an.word_treatment()
        assert "Bonjour" in tokens
```

**Benefits:**
- Logical grouping by functionality
- Shared setup via class-level fixtures (not observed here, but supported)
- Clear intent from class name

**Arrange-Act-Assert (AAA) Pattern:** Not explicitly labeled but followed implicitly:
```python
def test_file_size_mo(self, tmp_path):
    # Arrange
    f = tmp_path / "small.bin"
    f.write_bytes(b"x" * 1024)
    
    # Act
    size_mo = operation_fichier.file_size_Mo(str(f))
    
    # Assert
    assert size_mo == pytest.approx(1 / 1024, rel=1e-3)
```

## Fixtures and Test Data

**Location:** `tests/conftest.py` (shared across all tests)

**Key Fixtures:**

1. **sample_text:**
   ```python
   @pytest.fixture
   def sample_text() -> str:
       """A short French paragraph for linguistic analysis tests."""
       return (
           "Lors d'une belle matinee, le soleil brillait. "
           "Marie marchait dans la foret. "
           "Elle decouvrit une cabane mysterieuse."
       )
   ```

2. **tmp_export_dir:**
   ```python
   @pytest.fixture
   def tmp_export_dir(tmp_path) -> Path:
       """A clean temporary directory for export tests."""
       return tmp_path
   ```

3. **sample_export_data:**
   ```python
   @pytest.fixture
   def sample_export_data() -> dict:
       """Representative payload used by exporte_json/txt/csv/pdf."""
       return {
           "Nombre de mots": 286,
           "Nombre d'enonces": 7,
           "MLCU": 40.86,
           "Mots uniques": 203,
           "texte": "Texte de transcription d'exemple.",
       }
   ```

4. **mock_spacy:**
   ```python
   @pytest.fixture
   def mock_spacy(monkeypatch):
       """Replace spacy.load with a lightweight mock returning a fake nlp pipeline."""
       fake_token = MagicMock(text="mot", lemma_="mot", pos_="NOUN")
       fake_doc = MagicMock()
       fake_doc.__iter__ = lambda self: iter([fake_token])
       fake_nlp = MagicMock(return_value=fake_doc)
       fake_spacy = MagicMock(load=MagicMock(return_value=fake_nlp))
       monkeypatch.setitem(sys.modules, "spacy", fake_spacy)
       return fake_spacy
   ```

## Heavy Dependency Mocking Strategy

**Rationale (D-07):**
- PySide6 widgets require X11/display server (Linux), or native graphics (Windows/macOS)
- Whisper + torch + CUDA require GPU or local model files (expensive ~500MB+)
- spaCy `fr_core_news_lg` is ~500MB, not available in CI by default
- PyAudio + sounddevice require real audio hardware

**Mocking Approach:**

1. **Module-level stubs (conftest.py):**
   ```python
   def _stub_if_missing(name: str) -> None:
       """Insert a MagicMock for name when the real module is unavailable."""
       if name in sys.modules:
           return
       try:
           if _importlib_util.find_spec(name) is None:
               _install_module_mock(name)
       except (ImportError, ValueError):
           _install_module_mock(name)
   
   for mod_name in ("whisper", "torch", "pyaudio", "sounddevice", "pydub", "pydub.silence"):
       _stub_if_missing(mod_name)
   ```

2. **spaCy fake pipeline:**
   ```python
   _fake_spacy = MagicMock()
   _fake_token = MagicMock()
   _fake_token.text = "mot"
   _fake_token.lemma_ = "mot"
   _fake_token.prefix_ = ""
   _fake_token.suffix_ = ""
   _fake_token.pos_ = "NOUN"
   _fake_token.morph = ""
   _fake_nlp = MagicMock(return_value=[_fake_token])
   _fake_nlp.pipe_names = []
   _fake_spacy.load = MagicMock(return_value=_fake_nlp)
   sys.modules["spacy"] = _fake_spacy
   ```

3. **Patching at test level:**
   ```python
   def test_uses_audiosegment(self, tmp_path):
       f = tmp_path / "audio.mp3"
       f.write_bytes(b"fake audio")
       fake_audio = MagicMock()
       fake_audio.__len__ = lambda self: 5000
       with patch.object(
           operation_fichier.AudioSegment, "from_file", return_value=fake_audio
       ):
           assert operation_fichier.file_size_ms(str(f)) == 5000
   ```

## Coverage Configuration & Omissions

**Coverage Gate:** `--cov-fail-under=80` in pytest config

**Configured Omissions (from pyproject.toml):**
```
[tool.coverage.run]
omit = [
    # PySide6 widgets and views require a display server (D-07)
    "app/Widgets/*",
    "app/Views/*",
    # Qt controllers couple tightly to widgets/signals
    "app/controllers/*",
    "app/main.py",
    # pyaudio/sounddevice wrappers need real audio hardware
    "app/models/memo.py",
    "app/models/audio_worker.py",
    # whisper transcription pipeline needs the model + GPU
    "app/models/transcription.py",
    # legacy in-tree test directory (pre-Phase-9 test stub)
    "app/models/test/*",
    "app/models/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

**Why Excluded:**
1. **Views, Widgets, Controllers (UI layer):** Require display server or tight Qt coupling; use integration/e2e testing instead
2. **memo.py, audio_worker.py:** Require real PyAudio hardware device
3. **transcription.py:** Requires Whisper model (~500MB) + GPU; contains end-to-end pipeline not suitable for unit testing
4. **app/main.py:** Entry point; no testable logic beyond Qt initialization
5. **app/models/test/:** Legacy pre-refactoring test directory; superceded by `tests/`

**Covered Modules (business logic eligible for 80% gate):**
- `app/models/Analyse_NLTK.py` ✓ (covered via `test_analyse_nltk.py`)
- `app/models/operation_fichier.py` ✓ (covered via `test_feuille.py`)
- `app/models/exportation.py` ✓ (covered via `test_pdf_export.py`)
- `app/config.py` ✓ (implicitly covered; minimal code)

**Targeted modules NOT covered (excluded, appropriate reasons):**
- `app/models/transcription.py` — End-to-end Whisper transcription; tested via `test_controllers.py` (unit functions only: `custom_tokenize`, `extraire_mapping_depuis_segments`, `ajuster_mapping`)
- `app/models/memo.py` — Audio hardware wrapper
- `app/models/audio_worker.py` — Async audio processing

## Test Types

**Unit Tests:**
- Focus: Individual functions, class methods
- Examples:
  - `TestSentenceSegmentation.test_single_sentence()` — Tests `Analyse_NLTK.sent_size()`
  - `TestFileSizeMo.test_small_file()` — Tests `file_size_Mo()` utility
  - `TestCustomTokenize.test_simple_split()` — Tests `custom_tokenize()` word splitting
- Setup: Direct function calls with simple inputs; no external dependencies

**Integration Tests:**
- Focus: Interactions between modules, file I/O
- Examples:
  - `TestExporteJson.test_writes_valid_json()` — Exports data and reads back via `json.loads()`
  - `TestFileSizeMo.test_one_mo_file()` — Creates real temp file, measures size
- Setup: Use real temp filesystem (`tmp_path` fixture); mock only external calls

**E2E Tests:**
- Not implemented (excluded from scope; would require display server for UI testing)
- Could use Playwright or similar for GUI flows, but currently not in scope

## Mocking Patterns

**What to Mock:**
- Heavy ML libraries: `torch`, `whisper`, `spacy` (module-level in conftest)
- Audio libraries: `pyaudio`, `sounddevice`, `pydub` (when needed)
- File I/O operations that are slow or require specific hardware: `AudioSegment.from_file()` (patched in test)

**What NOT to Mock:**
- Real tempfile operations (use `tmp_path` fixture)
- Pure Python functions (`custom_tokenize`, `sent_size`)
- JSON/CSV I/O (test real reads/writes to `tmp_path`)
- Math/string operations

**Example: Mixed Real + Mock**
```python
def test_file_size_ms(self, tmp_path):
    # Real temp file creation
    f = tmp_path / "audio.mp3"
    f.write_bytes(b"fake audio")
    
    # Mock the expensive AudioSegment.from_file call
    fake_audio = MagicMock()
    fake_audio.__len__ = lambda self: 5000
    
    with patch.object(
        operation_fichier.AudioSegment, "from_file", return_value=fake_audio
    ):
        assert operation_fichier.file_size_ms(str(f)) == 5000
```

## Async Testing

Not applicable (codebase is not async; uses threading for audio recording).

## Error Testing

**Pattern:** Use `pytest.raises()` context manager

```python
def test_missing_file_raises(self):
    with pytest.raises(OSError):
        operation_fichier.file_size_Mo("/nonexistent/path/file.bin")
```

## Conditional Tests (Skip, Mark)

**Skip decorator (for unavailable resources):**
```python
@pytest.mark.skipif(
    not (FONTS_DIR / "Poppins-Bold.ttf").exists(),
    reason="Poppins fonts not bundled in this checkout",
)
class TestExportePdf:
    def test_writes_pdf_file(self, tmp_path, sample_export_data):
        ...
```

**Skip annotation (for known bugs):**
```python
@pytest.mark.skip(
    reason="spacy_calc_morphem has an upstream bug "
    "(calls .items() on morphem() which returns int). Tracked separately."
)
def test_spacy_calc_morphem_returns_list(self):
    ...
```

## CI Configuration

**File:** `.github/workflows/ci.yml`

**Steps:**
1. Checkout code
2. Set up Python 3.12 with pip caching
3. Install test dependencies from `requirements-test.txt`
4. Download NLTK data: `python -m nltk.downloader -q punkt punkt_tab`
5. Run pytest (automatically applies coverage gate from pyproject.toml)
6. Upload coverage XML as artifact (for reporting)

**Coverage Reporting:**
- XML uploaded for 14 days
- Terminal output shown in job logs
- Gate enforced: 80% minimum

## Common Test Patterns

**Floating-Point Assertions:**
```python
assert size_mo == pytest.approx(1 / 1024, rel=1e-3)
```

**Parametrized Tests:**
Not observed in current test suite (could be added for testing multiple format types).

**Fixtures with Cleanup:**
```python
@pytest.fixture
def tmp_export_dir(tmp_path) -> Path:
    """A clean temporary directory for export tests."""
    return tmp_path  # pytest auto-cleans tmp_path after test
```

**Monkeypatch (sys.modules):**
```python
def mock_spacy(monkeypatch):
    """Replace spacy.load with a lightweight mock."""
    monkeypatch.setitem(sys.modules, "spacy", fake_spacy)
```

## Coverage Results

**Current Target:** ~81% on gated modules (based on omit list)

**Modules NOT in 80% gate:**
- `app/Views/*` (5+ files, ~100+ lines each) — Excluded by design
- `app/Widgets/*` (20+ files, ~50 lines avg) — Excluded by design
- `app/controllers/*` (7 files, ~50 lines avg) — Excluded by design
- `app/models/transcription.py` (~330 lines) — Excluded; only pure helper functions tested
- `app/models/memo.py` (~193 lines) — Excluded; audio hardware required
- `app/models/audio_worker.py` (~83 lines) — Excluded; async audio processing
- `app/main.py` (entry point) — Excluded; Qt initialization only

**Eligible Modules (in 80% gate):**
- `app/models/Analyse_NLTK.py` (~252 lines) — Tested in `test_analyse_nltk.py`
- `app/models/operation_fichier.py` (~198 lines) — Tested in `test_feuille.py`
- `app/models/exportation.py` (~245 lines) — Tested in `test_pdf_export.py`
- `app/config.py` (~14 lines) — Minimal, coverage implicit

---

*Testing analysis: 2026-06-02*
