# Engineering Audit: v0.2.3 OCR Quality Polish

## Scope

This audit covers v0.2.3 OCR quality polish for ConvertKit/FileMorph. The work improves local OCR preprocessing and user guidance without changing non-OCR conversion behavior.

## Changed Files

- `app/converters/ocr_converter.py`: added OCR modes, Pillow-only preprocessing, OCR mode normalization, and 300 DPI PDF OCR rendering.
- `app/main.py`: added OCR mode selection, OCR mode defaults, and low-quality OCR result warning helpers.
- `tests/test_ocr_converter.py`: added tests for preprocessing, mode preparation, and mode validation.
- `tests/test_main_helpers.py`: added tests for OCR mode defaults and low-quality warning helpers.
- `README.md`: added OCR quality tips and screenshot/code limitations.
- `CHANGELOG.md`: added v0.2.3 notes.
- `audits/ENGINEERING_AUDIT_V0_2_3_OCR_QUALITY_POLISH.md`: added this audit.

## Verification

- Ran `python -m pytest -q`.
- Result: `36 passed in 0.37s`.
- Streamlit local test harness confirmed `Image to TXT (OCR)` still renders.
- Streamlit local test harness confirmed `Scanned PDF to TXT (OCR)` still renders.
- Streamlit local test harness confirmed OCR mode selector is visible.
- Streamlit local test harness confirmed image OCR defaults to `Enhanced OCR for screenshots`.
- Streamlit local test harness confirmed scanned PDF OCR defaults to `Enhanced OCR for scanned documents`.
- Streamlit local test harness confirmed existing `PDF to TXT` and `PDF to DOCX` options still render.

## Known Limitations

- OCR-to-DOCX remains out of scope.
- OCR quality still depends on source clarity, contrast, resolution, orientation, and installed Tesseract language data.
- Screenshots with code, dense UI, dark backgrounds, or mixed fonts may still be imperfect.
- The enhanced modes use Pillow preprocessing only; heavier OCR engines are intentionally not included.

## Next Steps

- Add optional image rotation and deskew controls.
- Add OCR integration tests gated on local Tesseract availability.
- Consider additional OCR engines only if local-only requirements and dependency weight are acceptable.
