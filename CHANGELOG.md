# Changelog

All notable changes to ConvertKit/FileMorph will be documented in this file.

## Unreleased

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
