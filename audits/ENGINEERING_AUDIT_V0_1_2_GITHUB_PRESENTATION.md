# Engineering Audit: v0.1.2 GitHub Presentation

## Scope

This audit covers repository presentation work for ConvertKit/FileMorph after the v0.1.1 MVP usability fixes. No conversion behavior was changed.

## Changes Made

- Reworked `README.md` into a GitHub-friendly project overview with quick start, supported conversions, screenshots guidance, limitations, roadmap, troubleshooting, and a local-only privacy note.
- Added `docs/screenshots/.gitkeep` so future screenshots have a stable home without fabricating assets.
- Added an MIT `LICENSE` using the current year and repository owner name.
- Added `CHANGELOG.md` with `Unreleased`, `v0.1.1`, and `v0.1.0` sections.
- Added `CONTRIBUTING.md` with local setup, test command, and branch naming guidance.
- Added this audit file under `audits/`.

## Verification

- Ran `python -m pytest -q`.
- Result: `11 passed in 0.09s`.
- Scope is documentation and repository metadata only; existing conversion behavior was not changed.

## Known Limitations

- No screenshots have been added yet; `docs/screenshots/` is intentionally a placeholder.
- OCR remains out of scope.
- PDF-to-PNG still requires Poppler to be installed locally.
- PDF-to-DOCX output quality still depends on source PDF structure and `pdf2docx` behavior.
- Uploaded and generated files still require manual cleanup from `uploads/` and `output/`.
