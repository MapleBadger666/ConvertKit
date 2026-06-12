# Changelog

All notable changes to ConvertKit/FileMorph will be documented in this file.

## Unreleased

- No changes yet.

## v0.4.1

- Added updated v0.4 UI screenshots to README.

## v0.4.0

- Added product polish for the Streamlit landing area.
- Grouped conversion options by category for clearer navigation.
- Added in-app dependency guidance with lightweight command status checks.
- Added concise conversion-specific help text.
- Polished the README for release readiness with grouped features, dependency guidance, quick start, and limitations.
- Standardized user-facing help around local system dependencies.

## v0.3.3

- Added local audio normalization before faster-whisper transcription.
- Added transcription TXT headers with file, conversion, model, language, and quality notes.
- Added transcription guidance and post-conversion advice for model and language choices.
- Improved readable errors for audio preprocessing failures.
- Documented transcription quality tips for English, Chinese, noisy audio, and short clips.

## v0.3.2

- Added local Audio to TXT transcription with faster-whisper.
- Added local Video to TXT transcription by extracting WAV audio with ffmpeg before transcription.
- Added transcription model and language selectors in Streamlit.
- Added timestamped transcription TXT output with preview and download support.
- Documented local transcription setup, model tradeoffs, and limitations.

## v0.3.1

- Added PPTX to DOCX export modes for text outline, slide images, and slide images with extracted text.
- Kept the existing PPTX to DOCX text outline behavior as the default.
- Added local slide image export for visual DOCX output through LibreOffice and Poppler.
- Documented PPTX to DOCX mode tradeoffs.

## v0.3.0

- Added PPTX to PDF conversion through local LibreOffice.
- Added PPTX to DOCX slide text extraction.
- Added video-to-audio extraction with WAV and MP3 output through local ffmpeg.
- Added upload filtering, tests, and documentation for Office and media conversions.
- No cloud APIs were added.

## v0.2.4

- Added README screenshots.
- Improved project demo presentation.
- No conversion behavior changes.

## v0.2.3

- Added Pillow-only OCR preprocessing for enhanced screenshot and scanned document modes.
- Added OCR mode selection in Streamlit.
- Rendered PDF OCR pages at 300 DPI.
- Added low-quality OCR result warnings.
- Documented OCR quality tips.
- Added tests for OCR preprocessing, mode helpers, and low-quality warning helpers.

## v0.2.2

- Added conversion-specific upload file type filtering in Streamlit.
- Added OCR language detection from `tesseract --list-langs`.
- Filtered OCR language selector options to installed local Tesseract languages.
- Added readable warnings for missing Chinese OCR language packs.
- Added OCR language validation before conversion.
- Added tests for upload type filtering and OCR language parsing/validation.

## v0.2.1

- Added single-file download buttons with readable labels and MIME types.
- Added TXT preview for generated `.txt` files.
- Clarified runtime dependency troubleshooting for Python packages, Poppler, and Tesseract.
- Added tests for download helper behavior and TXT preview behavior.

## v0.2.0

- Added local OCR text extraction for image files.
- Added local OCR text extraction for scanned PDFs.
- Added OCR language selection in Streamlit for English, Simplified Chinese, Traditional Chinese, and English + Simplified Chinese.
- Added Tesseract dependency checks with readable user-facing errors.
- Documented OCR setup and limitations.
- Added OCR tests that do not require a local Tesseract installation.

## v0.1.2

- Prepared the repository for GitHub presentation with clearer project documentation, license, contribution notes, screenshot placeholders, and an engineering audit.

## v0.1.1

- Added deterministic output filename de-duplication.
- Added ZIP packaging and download support for multi-output conversions.
- Improved Streamlit feedback for uploaded files, conversion status, successful outputs, and readable per-file failures.
- Added a clear Poppler dependency message for PDF-to-PNG conversion.
- Expanded tests for filename de-duplication and ZIP packaging.

## v0.1.0

- Built the initial local Streamlit MVP.
- Added image conversion for JPG, JPEG, PNG, and WEBP.
- Added image-to-PDF, PDF-to-PNG, PDF-to-TXT, and PDF-to-DOCX workflows.
- Added local file service helpers and initial pytest coverage.
