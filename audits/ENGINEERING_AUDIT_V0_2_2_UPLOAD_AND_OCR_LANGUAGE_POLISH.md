# Engineering Audit: v0.2.2 Upload and OCR Language Polish

## Scope

This audit covers v0.2.2 upload filtering and OCR language detection polish for ConvertKit/FileMorph. Existing conversion behavior was preserved.

## Changed Files

- `app/main.py`: added conversion-specific upload type filtering, OCR language option filtering, and Chinese language-pack warning.
- `app/converters/ocr_converter.py`: added Tesseract language parsing, installed language detection, required language splitting, and pre-conversion OCR language validation.
- `tests/test_main_helpers.py`: added upload type helper tests and OCR UI option filtering tests.
- `tests/test_ocr_converter.py`: added OCR language parsing and validation tests.
- `README.md`: documented `tesseract --list-langs` and troubleshooting for missing `chi_sim` / `chi_tra`.
- `CHANGELOG.md`: added v0.2.2 notes.
- `audits/ENGINEERING_AUDIT_V0_2_2_UPLOAD_AND_OCR_LANGUAGE_POLISH.md`: added this audit.

## Verification

- Ran `python -m pytest -q`.
- Result: `28 passed in 0.37s`.
- Streamlit local test harness confirmed `Images to JPG` only allows `.jpg`, `.jpeg`, `.png`, and `.webp`.
- Streamlit local test harness confirmed `PDF to TXT` only allows `.pdf`.
- Streamlit local test harness confirmed `Image to TXT (OCR)` only allows image extensions.
- Streamlit local test harness confirmed `Scanned PDF to TXT (OCR)` only allows `.pdf`.
- Streamlit local test harness confirmed the Chinese OCR language-pack warning appears when Chinese languages are missing.
- Streamlit local test harness confirmed existing conversion options still render.

## Known Limitations

- Tesseract language detection depends on the local `tesseract --list-langs` command.
- If Tesseract is not installed, OCR conversion still fails with the existing readable Tesseract install message.
- The UI hides OCR language combinations that are not fully installed rather than offering disabled options.
- OCR-to-DOCX remains out of scope.

## Next Steps

- Add end-to-end OCR tests that run only when Tesseract and language packs are installed.
- Add UI help text showing the exact installed OCR language codes.
- Add cleanup controls for local upload and output folders.
