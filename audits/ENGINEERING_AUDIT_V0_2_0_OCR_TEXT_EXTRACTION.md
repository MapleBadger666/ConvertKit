# Engineering Audit: v0.2.0 OCR Text Extraction

## Scope

This audit covers the v0.2.0 local OCR text extraction work for ConvertKit/FileMorph. The implementation adds OCR for image files and scanned PDFs while preserving existing conversion behavior.

## Changed Files

- `app/converters/ocr_converter.py`: added OCR dependency checks, image OCR, scanned PDF OCR, and OCR output path generation.
- `app/main.py`: added OCR conversion options, OCR language selection, Tesseract language-pack note, and OCR dispatch paths.
- `requirements.txt`: added `pytesseract`.
- `tests/test_ocr_converter.py`: added tests for Tesseract dependency behavior, OCR output filename generation, and unsupported OCR image extensions.
- `README.md`: documented OCR features, setup, supported languages, and limitations.
- `CHANGELOG.md`: added v0.2.0 OCR notes.
- `audits/ENGINEERING_AUDIT_V0_2_0_OCR_TEXT_EXTRACTION.md`: added this audit.

## Verification

- Ran `python -m pytest -q`.
- Result: `15 passed in 0.07s`.
- Tests avoid requiring an actual Tesseract installation by monkeypatching the dependency check.
- Manual Streamlit smoke check on `http://localhost:8503` confirmed the existing conversion selector, upload control, and Convert button render.
- Manual Streamlit smoke check confirmed `Image to TXT (OCR)` appears and shows the OCR language selector plus the `brew install tesseract-lang` note.
- Manual Streamlit smoke check confirmed `Scanned PDF to TXT (OCR)` appears and shows the OCR language selector plus the `brew install tesseract-lang` note.
- Direct dispatcher check with a temporary image confirmed missing Tesseract returns: `OCR requires Tesseract. On macOS, install it with: brew install tesseract`.

## Known Limitations

- OCR-to-DOCX is not implemented.
- OCR output is plain text and does not preserve complex tables, columns, fonts, or visual layout.
- OCR quality depends on source image clarity, resolution, orientation, contrast, and installed Tesseract language data.
- Handwriting may be inaccurate.
- Scanned PDF OCR depends on both Tesseract and Poppler being installed locally.
- Chinese OCR may require `tesseract-lang` or equivalent language data packages.

## Next Steps

- Add OCR integration tests that run only when Tesseract is available.
- Add optional preprocessing controls such as grayscale, contrast, or rotation.
- Add OCR-to-DOCX as a separate future workflow.
- Add UI cleanup/download improvements for OCR output files.
