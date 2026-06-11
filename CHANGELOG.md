# Changelog

All notable changes to ConvertKit/FileMorph will be documented in this file.

## Unreleased

- No changes yet.

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
