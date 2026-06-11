# FileMorph

FileMorph is a local Streamlit app for quick file conversion workflows. It currently focuses on common image conversions and practical PDF transformations, with generated files saved to `output/` on your machine.

## Local-Only Privacy Note

FileMorph runs locally. Uploaded files are written to the local `uploads/` directory, converted files are written to `output/`, and no cloud APIs or external upload services are used by the app.

## Features

- Batch image conversion between JPG, PNG, and WEBP.
- Safe JPG output for transparent images by flattening alpha onto a white background.
- ZIP download packaging when a conversion creates multiple output files.
- Convert multiple images into one PDF.
- Convert PDF pages to PNG images.
- Extract text from text-based PDFs into TXT.
- Convert PDF to DOCX with `pdf2docx` as a first MVP implementation.
- Clear UI feedback for uploaded files, conversion status, successful outputs, and failed files.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app/main.py
```

Then open the local Streamlit URL shown in the terminal.

Run tests with:

```bash
python -m pytest -q
```

## Supported Conversions

| Source | Target | Batch support | Notes |
| --- | --- | --- | --- |
| JPG, JPEG, PNG, WEBP | JPG | Yes | Alpha channels are flattened onto white for JPG output. |
| JPG, JPEG, PNG, WEBP | PNG | Yes | Preserves a broadly compatible image output. |
| JPG, JPEG, PNG, WEBP | WEBP | Yes | Uses Pillow for local conversion. |
| JPG, JPEG, PNG, WEBP | Single PDF | Yes | Combines uploaded images into one PDF. |
| PDF | PNG pages | One or more PDFs | Requires Poppler to be installed locally. |
| PDF | TXT | One or more PDFs | Works best with text-based PDFs that contain selectable text. |
| PDF | DOCX | One or more PDFs | Uses `pdf2docx`; complex layouts may need manual cleanup. |

## Screenshots

Screenshots should be added later under `docs/screenshots/`. Do not commit real user files or sensitive document previews. A placeholder `.gitkeep` file keeps the folder available in git.

Suggested future screenshots:

- Main upload and conversion screen.
- Batch image conversion with ZIP download.
- PDF conversion error state when Poppler is missing.

## Limitations

- OCR is not included. Scanned PDFs will not become editable text unless OCR is added in a future release.
- PDF-to-PNG requires Poppler command-line tools in addition to Python packages.
- PDF-to-DOCX quality depends on the source PDF layout and may not perfectly preserve columns, tables, fonts, or spacing.
- Uploaded source files remain in `uploads/` and generated files remain in `output/` until manually removed.
- The app is designed for local MVP usage, not multi-user hosted deployments.

## Roadmap

- Add cleanup controls for `uploads/` and `output/`.
- Add richer download controls for single output files.
- Add integration tests for PDF workflows with small fixture files.
- Add optional OCR support for scanned PDFs.
- Add screenshot assets once the UI is stable enough for project presentation.

## Troubleshooting

### How to run the app

Install the requirements, then start Streamlit from the project root:

```bash
python -m pip install -r requirements.txt
streamlit run app/main.py
```

### PDF-to-PNG requires Poppler

PDF-to-PNG conversion uses `pdf2image`, which needs the Poppler command-line tools. On macOS, install Poppler with:

```bash
brew install poppler
```

If Poppler is missing, FileMorph shows this message:

```text
PDF-to-PNG requires Poppler. On macOS, install it with: brew install poppler
```

### Scanned PDFs and text extraction

TXT export works for text-based PDFs that contain selectable text. Scanned PDFs are usually images inside a PDF, so they do not become editable text without OCR. OCR is intentionally not included in this MVP.

### PDF-to-DOCX layout quality

PDF-to-DOCX conversion is handled by `pdf2docx` for the first MVP. Complex layouts, tables, columns, unusual fonts, and scanned pages may not convert perfectly because PDFs do not store document structure the same way DOCX files do.

## Project Structure

```text
app/
  main.py
  converters/
    image_converter.py
    pdf_converter.py
  services/
    file_service.py
audits/
docs/
  screenshots/
tests/
requirements.txt
README.md
```

## License

MIT License. See `LICENSE`.
