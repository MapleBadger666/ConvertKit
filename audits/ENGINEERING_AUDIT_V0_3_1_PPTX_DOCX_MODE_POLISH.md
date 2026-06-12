# Engineering Audit: v0.3.1 PPTX DOCX Mode Polish

## Scope

This audit covers v0.3.1 PPTX to DOCX mode polish for ConvertKit/FileMorph. The work adds multiple local-only DOCX export modes while keeping the existing text outline behavior as the default.

## Changed Files

- `app/converters/office_converter.py`: added PPTX to DOCX mode constants, mode normalization, slide image export, slide image DOCX output, and mixed image/text DOCX output.
- `app/main.py`: added the Streamlit `DOCX mode` selector for PPTX to DOCX.
- `tests/test_office_converter.py`: added mode normalization, dispatch, text outline structure, slide image export, and mixed mode tests with mocked dependencies.
- `tests/test_main_helpers.py`: added DOCX mode option tests.
- `README.md`: documented PPTX to DOCX mode tradeoffs and local dependencies.
- `CHANGELOG.md`: added v0.3.1 notes.
- `audits/ENGINEERING_AUDIT_V0_3_1_PPTX_DOCX_MODE_POLISH.md`: added this audit.

## PPTX to DOCX Modes

- Text Outline: keeps the existing editable text outline behavior.
- Slide Images: embeds rendered slide images into DOCX for closer visual preservation.
- Slide Images + Extracted Text: embeds rendered slide images and adds extracted editable text below each slide.

## Dependencies

- Text Outline mode uses `python-pptx` and `python-docx`.
- Slide image modes use local LibreOffice for PPTX-to-PDF rendering and local Poppler for PDF-to-PNG export.
- No cloud APIs were added.

## Verification

- Ran `python -m pytest -q`.
- Result: `59 passed in 0.39s`.
- Manual Streamlit UI check confirmed `PPTX to DOCX` shows a `DOCX mode` selector.
- Manual Streamlit UI check confirmed the selector contains `Text Outline`, `Slide Images`, and `Slide Images + Extracted Text`.
- Manual Streamlit UI check confirmed `Text Outline` is selected by default.
- Manual Streamlit UI check confirmed PPTX upload filtering still shows `PPTX`.
- Manual Streamlit UI check confirmed `PPTX to PDF` still appears in the conversion menu.
- Manual local conversion check confirmed Text Outline mode generated a DOCX with extracted editable slide text.
- Attempted a real PPTX-to-PDF and slide-image DOCX conversion with a temporary synthetic deck, but the local `soffice` wrapper points to `/Applications/LibreOffice.app/Contents/MacOS/soffice`, which is not present in this environment. The implementation now maps that broken-wrapper case to the readable LibreOffice dependency error.
- Slide-image DOCX behavior is covered by mocked tests and remains dependent on a working local LibreOffice and Poppler installation.

## Conversion Behavior

PPTX to PDF remains routed through the existing LibreOffice path. Existing image, PDF, OCR, media, TXT preview, and download behavior should remain unchanged.
