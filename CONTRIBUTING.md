# Contributing

Thanks for helping improve ConvertKit/FileMorph. This project is intentionally local-first and simple, so contributions should keep the app readable and avoid cloud-only dependencies.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app/main.py
```

For PDF-to-PNG conversion on macOS, install Poppler:

```bash
brew install poppler
```

## Testing

Run the test suite before opening a pull request:

```bash
python -m pytest -q
```

## Branch Naming

Use short, descriptive branch names. Preferred pattern:

```text
codex/<area>-<short-description>
```

Examples:

- `codex/docs-github-polish`
- `codex/pdf-error-handling`
- `codex/image-tests`

## Contribution Guidelines

- Keep conversion behavior local-only.
- Do not add OCR unless it is part of an explicit roadmap task.
- Do not add new runtime dependencies without a clear reason.
- Add or update tests when changing conversion logic.
- Keep UI changes focused and easy to understand.
