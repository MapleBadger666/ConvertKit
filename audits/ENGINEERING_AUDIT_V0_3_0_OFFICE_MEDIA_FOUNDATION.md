# Engineering Audit: v0.3.0 Office and Media Foundation

## Scope

This audit covers v0.3.0 Office and media conversion foundation work for ConvertKit/FileMorph. The work adds local PPTX and video conversion paths without adding cloud APIs or changing existing image, PDF, OCR, TXT preview, or download behavior.

## Changed Files

- `app/converters/office_converter.py`: added PPTX to PDF through LibreOffice and PPTX to DOCX text extraction helpers.
- `app/converters/media_converter.py`: added video to audio conversion through ffmpeg with WAV and MP3 output support.
- `app/main.py`: added Streamlit conversion options, upload filters, video audio format selector, and conversion dispatch.
- `app/services/file_service.py`: added PPTX and video extension helpers.
- `requirements.txt`: added `python-pptx` and `python-docx`.
- `tests/test_file_service.py`: added PPTX and video extension tests.
- `tests/test_main_helpers.py`: added upload filter and MIME type tests for Office and media output.
- `tests/test_office_converter.py`: added LibreOffice dependency error, PPTX helper, and mocked PPTX-to-PDF tests.
- `tests/test_media_converter.py`: added ffmpeg dependency error, audio format, output path, and mocked video-to-audio tests.
- `README.md`: documented Office and media conversions, system dependencies, and limitations.
- `CHANGELOG.md`: added v0.3.0 notes.
- `audits/ENGINEERING_AUDIT_V0_3_0_OFFICE_MEDIA_FOUNDATION.md`: added this audit.

## New Conversion Options

- `PPTX to PDF`
- `PPTX to DOCX`
- `Video to Audio`

## System Dependencies

- PPTX to PDF requires local LibreOffice through `soffice`.
- Video to Audio requires local `ffmpeg`.
- These are documented as system dependencies and were not added to `requirements.txt`.

## Verification

- Ran `python -m pytest -q`.
- Result: `49 passed in 0.42s`.
- Manual Streamlit UI check confirmed `PPTX to PDF` appears.
- Manual Streamlit UI check confirmed `PPTX to DOCX` appears.
- Manual Streamlit UI check confirmed `Video to Audio` appears.
- Manual Streamlit UI check confirmed PPTX upload filters show `PPTX`.
- Manual Streamlit UI check confirmed video upload filters show `MP4, MOV, MKV, AVI`.
- Manual Streamlit UI check confirmed the video audio format selector appears with `WAV` selected by default.
- Manual Streamlit UI check confirmed existing image, PDF, and OCR options still render.

## Conversion Behavior

Existing image, PDF, OCR, TXT preview, and download behavior should remain unchanged. No speech-to-text or cloud API integration was added.
