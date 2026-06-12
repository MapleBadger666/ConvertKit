# Engineering Audit: v0.4.2 README Trim

## Scope

This audit covers v0.4.2 README trim and screenshot cleanup for ConvertKit/FileMorph. The work keeps the GitHub landing page focused on the v0.4 UI preview, concise feature summary, setup, dependencies, privacy, and limitations.

## Changed Files

- `README.md`: removed older screenshot references and trimmed long detailed sections.
- `CHANGELOG.md`: added v0.4.2 notes.
- `audits/ENGINEERING_AUDIT_V0_4_2_README_TRIM.md`: added this audit.

## Screenshot References

Kept:

- `docs/screenshots/v0.4.0-main-ui.png`
- `docs/screenshots/v0.4.0-transcription-ui.png`

Removed from README:

- `docs/screenshots/main-ui.png`
- `docs/screenshots/successful-conversion.png`

The old screenshot files were not deleted.

## Verification

- Confirmed old README screenshot references are no longer present.
- Ran `python -m pytest -q`.
- Result: `84 passed in 0.47s`.

## Behavior

No app behavior, conversion logic, dependencies, or screenshot image contents were changed.
