**Read in [English](./CONTRIBUTING.md) / [Français](./CONTRIBUTING.fr.md)**

# Contributing to Ortholyse

Thanks for taking the time to look at how to help. This project is maintained as time allows, contributions go a long way.

## Ground rules

- Open an issue before opening a non-trivial pull request. We will discuss the design before any code is written.
- One concern per PR. Smaller diffs land faster.
- Conventional commit messages: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- All code stays in English (identifiers, comments, commit messages). User-facing strings remain in French, English UI is on the roadmap.
- No secrets, no patient data, no audio samples committed to the repository.

## Reporting bugs

Use the **Bug report** issue template. Include:

- A clear description of what happened versus what you expected.
- Steps to reproduce, with concrete inputs.
- Your OS, Python version, and the relevant commit SHA or tag.
- Logs and any traceback, copy pasted as text rather than as a screenshot.

## Requesting features

Use the **Feature request** issue template. Describe the clinical or research need behind the request, not just the technical solution. That helps pick the right shape for the fix.

## Local setup

```bash
git clone https://github.com/assinscreedFC/ortholyse.git
cd ortholyse
python -m venv .venv
source .venv/bin/activate     # macOS / Linux
.\.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

`requirements.txt` already pulls the French Spacy models (`fr_core_news_lg`, `fr_core_news_sm`) as pinned wheels, so no extra `spacy download` step is needed.

NLTK data, on first run:

```bash
python -c "import nltk; nltk.download('punkt_tab')"
```

Run the app:

```bash
python app/main.py
```

## Tests

Tests rely on a slim dependency set (UI, Whisper and Spacy are mocked in `tests/conftest.py`):

```bash
pip install -r requirements-test.txt
python -m nltk.downloader -q punkt punkt_tab
pytest
```

`pyproject.toml` enforces coverage via `--cov-fail-under=80`. The gated modules are the business modules under `app/models/` (`Analyse_NLTK.py`, `exportation.py`, `operation_fichier.py`). UI widgets, Qt views, controllers, and Whisper / audio wrappers are excluded from the gate because they need a display server, audio hardware or the real ML model to run.

If you add a business module, add tests under `tests/`.

## Style

- Type hints on public functions are encouraged.
- Keep functions focused, if a function gets past 50 lines, consider splitting it.
- Match the surrounding style of the file you are editing (this is a French academic codebase, mixed FR / EN naming is expected).

## Pull request flow

1. Fork the repository.
2. Create a branch from `main`: `git checkout -b feat/short-description`.
3. Commit small, focused changes.
4. Run `pytest` locally.
5. Push and open a PR using the template.
6. Reference the related issue with `Closes #N`.

A reviewer will respond as time allows. Please be patient, this is a maintained side project, not a full time effort.

## Code of conduct

Be respectful. Assume good intent. No harassment, no personal attacks. If something feels off, open an issue and we will sort it out.

## License

By submitting a contribution you agree that it will be released under the [MIT License](./LICENSE).
