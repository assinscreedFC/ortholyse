**Read in [English](./CONTRIBUTING.md) / [Français](./CONTRIBUTING.fr.md)**

# Contributing to Ortholyse

Thanks for taking the time to look at how to help. This project is maintained as time allows; contributions go a long way.

## Ground rules

- Open an issue before opening a non-trivial pull request. We will discuss the design before any code is written.
- One concern per PR. Smaller diffs land faster.
- Conventional commit messages: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- All code stays in English (identifiers, comments, commit messages). User-facing strings remain in French; English UI is on the roadmap.
- No secrets, no patient data, no audio samples committed to the repository.

## Reporting bugs

Use the **Bug report** issue template. Include:

- A clear description of what happened versus what you expected.
- Steps to reproduce, with concrete inputs.
- Your OS, Python version, and the relevant commit SHA or tag.
- Logs and any traceback, copy pasted as text rather than as a screenshot.

## Requesting features

Use the **Feature request** issue template. Describe the clinical or research need behind the request, not just the technical solution. That helps us pick the right shape for the fix.

## Local setup

```bash
git clone https://github.com/assinscreedFC/ortholyse.git
cd ortholyse
python -m venv .venv
source .venv/bin/activate     # macOS / Linux
.\.venv\Scripts\activate      # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m spacy download fr_core_news_lg
python -m spacy download fr_core_news_sm
```

Run the app:

```bash
python app/main.py
```

## Tests

Run the suite before pushing:

```bash
pytest
pytest --cov=app --cov-report=term-missing
```

CI fails the build if coverage on the gated modules (`app/feuille/`, `app/exportation/`, `app/operation_fichier/`) drops below 80 percent. UI widgets and Whisper / Spacy wrappers are excluded from the gate.

If you add a business module, add tests in the matching folder under `tests/`.

## Style

- Run `ruff check app tests` before committing.
- Stick to type hints on public functions.
- Keep functions focused; if a function gets past 50 lines, consider splitting it.

## Pull request flow

1. Fork the repository.
2. Create a branch from `main`: `git checkout -b feat/short-description`.
3. Commit small, focused changes.
4. Run `ruff` and `pytest` locally.
5. Push and open a PR using the template.
6. Reference the related issue with `Closes #N`.

A reviewer will respond as time allows. Please be patient; this is a maintained side project, not a full time effort.

## Code of conduct

Be respectful. Assume good intent. No harassment, no personal attacks. If something feels off, open an issue and we will sort it out.

## License

By submitting a contribution you agree that it will be released under the [MIT License](./LICENSE).
