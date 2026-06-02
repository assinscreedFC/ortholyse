# Codebase Concerns

**Analysis Date:** 2026-06-02

## Tech Debt

**Morpheme Detection (Rule-Based Heuristic):**
- Issue: `Analyse_NLTK.morphem()` in `app/models/Analyse_NLTK.py:159-209` uses fragile rule-based detection:
  - JSON prefix/suffix lists matched by string startswith/endswith
  - SnowballStemmer.stem() + word.replace() heuristic to detect suffixes (line 183): `word_suffixe = word.replace(stem, "")`
  - No validation against gold standard or linguistic corpus
  - False positives on accidental patterns (e.g., short words where replace() removes too much)
  - Infixe detection checks stem length constraints but with ad-hoc thresholds (line 201: `len(stem) - len(suf)) > 1 and len(suf) > 1`)
- Files: `app/models/Analyse_NLTK.py` (60 lines of fragile logic), `app/controllers/Result_controllers.py:65-70` (uses morphem results)
- Impact: Morpheme counts feed MLU-related metrics displayed to speech therapists; systematic over/under-counting skews analysis results
- Fix approach: Replace with spaCy lemmatization (code present at `app/models/Analyse_NLTK.py:222-240` but not integrated); validate against standard French morphology dataset; implement proper decomposition rules per inflectional patterns

**Utterance Segmentation (nltk.sent_tokenize):**
- Issue: `Analyse_NLTK.sent_size()` in `app/models/Analyse_NLTK.py:111-121` relies on `nltk.sent_tokenize(self.__text)` which segments on punctuation only
  - Inadequate for spoken/oral transcripts (pauses, false starts, mid-sentence interruptions not reflected in written transcript)
  - MLCU (Mean Length of Communication Unit) = word_count / sent_count depends entirely on sentence boundaries
  - No handling of run-on sentences common in spontaneous speech
  - No distinction between utterances vs syntactic sentences
- Files: `app/models/Analyse_NLTK.py:117`, `app/models/transcription.py` (Whisper segments used for timing but not utterance units), `app/controllers/Result_controllers.py:72-78` (get_enonce calls sent_size)
- Impact: MLCU and morpheme-per-utterance metrics (`get_morpheme_enonce()` at line 80-85) are linguistically invalid for speech data
- Fix approach: Implement pause-based segmentation using Whisper segment boundaries (already captured at `app/models/transcription.py:314`); add custom utterance tokenizer for French disfluencies; validate against gold-standard segmentation corpus

**Fragile Timestamp Mapping in Transcription:**
- Issue: `app/models/transcription.py:158-233` (ajuster_mapping function) uses heuristic-based timestamp remapping
  - When user edits transcribed text, mapping is recalculated via token count change heuristics (line 198: ±15% threshold)
  - If change exceeds threshold, falls back to uniform redistribution across segment (line 223-231)
  - No validation that remapped timestamps match actual audio content
  - Word-level timestamps from Whisper may not align with user corrections
- Files: `app/models/transcription.py:158-233`
- Impact: Playback of edited text skips/repeats audio; analysis metrics linked to timestamps become unreliable if text corrections are made
- Fix approach: Store correction deltas (position, before/after tokens); calculate offset adjustments rather than wholesale remapping; lock timestamps when user edits transcription; separate "source" vs "corrected" text tracks

## Known Bugs

**Temp File Cleanup in Concurrent Transcriptions:**
- Symptoms: Temp MP3 files from `extract_audio_fmp4()` or `split_audio()` may accumulate if transcription is cancelled or crashes
- Files: `app/models/operation_fichier.py:120-134` (extract_audio_fmp4), `app/models/operation_fichier.py:156-199` (split_audio), `app/models/transcription.py:242-325` (transcription function)
- Trigger: User cancels transcription mid-processing, or exception in `transcription_result = modele.transcribe()` at line 294/298
- Current mitigation: `shutil.rmtree(outDir)` at line 296 cleans split fragments; `os.remove(file_path)` at line 303 cleans extracted MP4 audio. But if exception occurs between temp file creation and cleanup, file persists
- Risk: Disk space leak in long-running application with repeated transcriptions
- Workaround: Manually delete files in system temp folder; restart application
- Fix approach: Use context managers (try/finally) for temp file lifecycle; implement temp file registry on app startup to orphan cleanup

**Print Statements in Production Code:**
- Symptoms: Console spam from `app/models/memo.py` (lines 47, 67, 71, 87, 90, 96, 99, 105, 109, 114, 117, 122, 127, 130, 133, 192)
- Files: `app/models/memo.py:47-192` (Memo class has 15+ print() calls)
- Trigger: Any recording operation produces console output
- Workaround: Suppress stdout or ignore console logs
- Fix approach: Replace all print() with logging.debug/info/error (already imported logger at line 8); log only lifecycle events (start, stop, error)

**Missing Exception Handling in Morpheme Calculation:**
- Symptoms: If morphem() receives invalid/empty text, may produce ZeroDivisionError or index errors
- Files: `app/models/Analyse_NLTK.py:159-209`
- Trigger: Empty transcription or special characters that break tokenization
- Current mitigation: None visible
- Fix approach: Add guards for empty word_dict, validate stem length before replace(), catch regex errors

## Security Considerations

**No Patient Data Persistence / GDPR Compliance:**
- Risk: Patient transcriptions are held only in memory during the app session. No encryption, no patient ID separation, no audit log
- Files: `app/models/memo.py` (raw audio in frames buffer), `app/models/transcription.py` (raw text in `texte_global`), `app/controllers/Result_controllers.py:42` (self.data dict with patient text), `app/models/exportation.py` (exports to user-chosen path with no access control)
- Current mitigation: Data is cleared on app exit; user responsible for managing exported files
- Recommendations: 
  - Implement patient ID + session isolation (no patient name in logs or temp files)
  - Encrypt temp files on disk (use `cryptography` package already in requirements)
  - Add audit trail for who accessed what data, when
  - Never log patient text (already done at `app/models/Analyse_NLTK.py:119-120`, but review all modules)
  - Implement proper file access controls on exported data (password-protect PDFs, set file permissions)

**Audio Validation Incomplete:**
- Risk: `_validate_audio_file()` at `app/models/operation_fichier.py:49-68` checks extension whitelist + MIME type (if python-magic available), but:
  - MIME check is a no-op if libmagic native not installed (line 60-65)
  - No file size validation before loading into memory
  - No sample rate validation for Whisper (expects 16kHz)
  - pydub.AudioSegment.from_file() may fail with truncated/corrupted files
- Files: `app/models/operation_fichier.py:49-68`, `app/models/operation_fichier.py:108-118` (file_size_sec calls AudioSegment.from_file)
- Recommendations:
  - Make libmagic validation mandatory (raise error if not available)
  - Add max file size check (e.g., reject >1GB audio)
  - Validate sample rate and warn if != 16kHz
  - Handle pydub exceptions and provide user-friendly error messages

**Temp File Path Predictability:**
- Risk: `tempfile.mkstemp()` at `app/models/operation_fichier.py:130` creates unique files, but directory is system temp (usually readable by all users on system)
  - Extracted MP4 audio (patient voice data) written to world-readable temp
- Files: `app/models/operation_fichier.py:130` (ortholyse_convert_*.mp3)
- Recommendations:
  - Use `tempfile.mkdtemp(dir=SECURE_TEMP)` with restricted permissions (mode 0o700)
  - Store secure temp dir in app config
  - Ensure cleanup in finally block

## Performance Bottlenecks

**Spacy Model Loaded Per Analyse_NLTK Instance:**
- Problem: `self.nlp = spacy.load("fr_core_news_lg")` at `app/models/Analyse_NLTK.py:47` loads ~900MB model every time Analyse_NLTK() is instantiated
- Files: `app/models/Analyse_NLTK.py:47`
- Cause: No module-level caching (unlike Whisper model caching at `app/models/transcription.py:22-35`)
- Impact: Analysis step (`Result_worker.py:36-39`) instantiates Analyse_NLTK, causing multi-second hang
- Improvement path: Implement module-level cache similar to `_get_whisper_model()`:
  ```python
  _SPACY_MODEL = None
  def _get_spacy_model():
      global _SPACY_MODEL
      if _SPACY_MODEL is None:
          _SPACY_MODEL = spacy.load("fr_core_news_lg")
      return _SPACY_MODEL
  ```

**Morpheme Detection O(n^2) Loop:**
- Problem: `morphem()` at line 196-203 iterates over ALL suffixes dict entries for each word, then checks word.endswith() on all suffixes in each entry
- Files: `app/models/Analyse_NLTK.py:196-203`
- Cause: Nested loops without early exit across all suffix keys
- Impact: Slow for large texts (100+ words × 1000+ suffix patterns = 100k checks)
- Improvement path: Pre-build trie or suffix tree for O(log n) lookup; or use regex compiled suffix patterns

**Whisper Model Loading Blocks UI:**
- Problem: `modele.transcribe()` at `app/models/transcription.py:294/298` runs in thread (`TranscriptionRunnable`), but first time loads 1.5GB model synchronously
- Files: `app/controllers/Transcription_worker.py:35` calls transcription() which calls `_get_whisper_model()` at line 288 (sync load)
- Impact: UI freezes for 10-30s on first transcription depending on disk speed
- Improvement path: Pre-load model on app startup or in background thread; show progress indicator

## Fragile Areas

**Large UI Files (MonoWorks):**
- Files: `app/Views/ImporterAudio.py` (579 lines), `app/Views/Parametres.py` (393 lines), `app/Views/Metrique.py` (381 lines)
- Why fragile: High cohesion of layout, styling, and event handling makes any change risky; no component extraction
- Safe modification: Extract layout methods (top_bar, body, etc.) into dedicated layout builder classes; test event handlers separately
- Test coverage: Minimal UI tests visible; no automated QWidget tests

**Transcription Worker State Machine:**
- Files: `app/controllers/Transcription_worker.py`, `app/models/transcription.py`, `app/models/operation_fichier.py` (split_audio, extract_audio_fmp4)
- Why fragile: Multiple async steps (extract → split → transcribe → cleanup) with shared state (temp files, whisper model); no formal state machine or rollback on error
- Safe modification: Implement explicit state enum; add pre-condition checks before each step; wrap entire transcription in context manager for cleanup
- Test coverage: No integration tests for full pipeline; only unit test at `app/models/test/test_Analyse_NLTK.py:16-21` (single test, no error cases)

**Memo.py Audio Recording State:**
- Files: `app/models/memo.py:19-194`
- Why fragile: Uses threading.Event to coordinate pause/resume/stop; frames buffer grows unbounded; pyaudio/sounddevice can deadlock on cleanup
- Safe modification: Add buffer size limit; use queue.Queue for thread-safe frame passing; test pause/resume cycle
- Test coverage: None

**Mixed French/English Naming (Inconsistent APIs):**
- Files: Throughout codebase
  - Methods mix: `word_treatment()`, `sent_size()` (English) vs `get_morpheme()`, `exporte_pdf()` (French verbs), `get_enonce()` (French noun)
  - Parameter names: `chemin` (Fr), `file_path` (En), `file_pth` (En abbreviated)
  - Class names: `Analyse_NLTK` (French prefix, English suffix), `Memo` (generic)
  - Comments mostly French, variable names mostly English
- Why fragile: Inconsistency causes API discovery confusion; refactoring across files risks missing method calls
- Safe modification: Pick one language (recommend English for code, French for UI strings); create deprecation aliases for old names; use sed/rg to bulk rename
- Impact: Low severity (documentation issue mainly) but impacts maintainability

## Missing Critical Features

**Patient Data Management System:**
- Problem: No way to associate analyses with patient metadata (age, language, diagnosis, session date); no case history/progression tracking
- Blocks: Speech therapists cannot organize multiple analyses per patient; cannot track improvement over time; cannot export patient chart
- Current workaround: Manual file naming (user remembers to include patient ID in filename)
- Fix approach: Implement SQLite patient registry; add patient ID field to analysis exports; implement session history view

**Real-time Feedback During Transcription:**
- Problem: Transcription worker produces no progress updates; UI shows no indication of what step is running (extract? split? transcribe? combine?)
- Blocks: User cannot estimate remaining time; cannot differentiate between "slow" and "hung"
- Current workaround: None
- Fix approach: Add progress signal to TranscriptionRunnable; emit stage names ("Extracting audio...", "Transcribing segment 1/5", etc.)

**Distribution / Setup Automation:**
- Problem: App requires manual venv setup + pip + nltk.download + ffmpeg path adjustment (documented at line 70-91 of operation_fichier.py but manual)
- Blocks: Non-technical end users (speech therapists) cannot install; ffmpeg discovery fails silently if system ffmpeg unavailable
- Current workaround: Developer ships pre-configured bundle or documents all steps
- Fix approach: PyInstaller bundle with vendored ffmpeg + embedded nltk data + pip requirements pre-installed; installer script to validate dependencies on first run

## Test Coverage Gaps

**Morpheme Detection Untested:**
- What's not tested: `Analyse_NLTK.morphem()` has no test cases; spacy_calc_morphem() has no assertions
- Files: `app/models/test/test_Analyse_NLTK.py` has only test_word_size() (tests word_treatment, sent_size, mlcu, unique_words but NOT morphem)
- Risk: False morpheme counts go undetected; refactoring stem/suffix logic has no regression guard
- Priority: HIGH (core analysis metric)
- Recommendation: Add test cases with known words:
  - "unhappy" → prefixe=True, suffixe=False, infixe=False
  - "thoughtfully" → prefixe=False, suffixe=True (or infixe?), validate against Petit Larousse morphology

**Transcription Mapping Untested:**
- What's not tested: `extraire_mapping_depuis_segments()`, `ajuster_mapping()` with real Whisper outputs
- Files: `app/models/test/test_Analyse_NLTK.py` does not import transcription module
- Risk: User edits text → timestamps become corrupted → playback skips; no CI catches this
- Priority: HIGH (impacts UX and analysis results)
- Recommendation: Add integration test with recorded audio sample + edit scenarios

**Temp File Cleanup Untested:**
- What's not tested: `extract_audio_fmp4()`, `split_audio()` with exception scenarios (corrupt input, disk full, concurrent access)
- Files: No test suite for operation_fichier.py
- Risk: Orphaned temp files accumulate; no coverage of cleanup path on error
- Priority: MEDIUM (operational reliability)
- Recommendation: Unit tests with tempfile mocking; test abort scenarios

**No End-to-End Tests:**
- What's not tested: Full pipeline (record audio → transcribe → analyze → export) never runs in CI
- Risk: Integration failures (e.g., Result_worker emits signal but nobody listening) go undetected
- Priority: MEDIUM (catches regressions in worker orchestration)
- Recommendation: Add E2E test with short recorded sample audio

---

*Concerns audit: 2026-06-02*
