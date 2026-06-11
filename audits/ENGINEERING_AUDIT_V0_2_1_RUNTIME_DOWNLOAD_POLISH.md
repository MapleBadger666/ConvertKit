# Engineering Audit: v0.2.1 Runtime Download Polish

## Scope

This audit covers v0.2.1 runtime dependency and download polish for ConvertKit/FileMorph. Conversion behavior was not changed.

## Changed Files

- `app/main.py`: added MIME type inference, readable single-file download labels, single-output download buttons, and TXT previews.
- `tests/test_main_helpers.py`: added tests for MIME types, download labels, preview length, and empty TXT preview messaging.
- `README.md`: clarified missing Python dependency recovery, Poppler requirements for PDF pages to PNG, and Tesseract requirements for OCR.
- `CHANGELOG.md`: added v0.2.1 notes.
- `audits/ENGINEERING_AUDIT_V0_2_1_RUNTIME_DOWNLOAD_POLISH.md`: added this audit.

## Dependency Check

`requirements.txt` was reviewed and already includes:

- `streamlit`
- `pypdf`
- `pdf2image`

No duplicate dependencies were added.

## Verification

- Ran `python -m pytest -q`.
- Result: `20 passed in 0.47s`.
- Streamlit local test harness confirmed PDF to TXT creates a `download_button` labeled `Download TXT`.
- Streamlit local test harness confirmed PDF to TXT shows a TXT preview with extracted text.
- Streamlit local test harness confirmed PDF pages to PNG completes with two `.png` outputs.
- Streamlit local test harness confirmed multi-output PDF pages to PNG creates a ZIP output path and download element.

## Known Limitations

- Streamlit download buttons read generated files into memory, which is acceptable for this MVP but may need streaming or size limits later.
- TXT previews show only the first 1000 characters.
- Poppler and Tesseract remain system-level dependencies and are not installed by `pip`.

## Next Steps

- Add end-to-end UI tests for file upload and download flows.
- Consider single-file download buttons for all generated outputs in multi-output mode alongside the ZIP download.
- Add cleanup controls for `uploads/` and `output/`.
