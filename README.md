# FileMorph

FileMorph is a local Streamlit MVP for common file conversions. Uploaded files are written to a local `uploads/` folder and generated files are written to `output/`. Nothing is uploaded to an external service.

## Features

- Batch image conversion between JPG, PNG, and WEBP.
- Safe JPG output for transparent images by flattening alpha onto a white background.
- ZIP download packaging when a conversion creates multiple output files.
- Convert multiple images into one PDF.
- Convert PDF pages to PNG images.
- Extract text from text-based PDFs into TXT.
- Convert PDF to DOCX with `pdf2docx` as a first MVP implementation.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

PDF-to-PNG conversion uses `pdf2image`, which also requires Poppler to be installed on your system.

On macOS:

```bash
brew install poppler
```

## Run the App

```bash
streamlit run app/main.py
```

Then open the local Streamlit URL shown in the terminal.

## Run Tests

```bash
python -m pytest -q
```

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
tests/
requirements.txt
README.md
```

## Short Report

What works:

- Image conversion for JPG, JPEG, PNG, and WEBP inputs.
- Batch image uploads and batch image output.
- Images can be combined into a single PDF.
- PDF pages can be rendered to PNG when Poppler is available.
- Text extraction works for PDFs that contain selectable text.
- DOCX export is implemented through `pdf2docx`.

Known limitations:

- Scanned PDFs do not become text unless OCR is added later.
- PDF-to-PNG depends on the system Poppler binary, not just Python packages.
- DOCX conversion quality depends heavily on the PDF layout.
- Uploaded source files are retained in `uploads/` for transparency during the MVP.

Recommended next steps:

- Add cleanup controls for `uploads/` and `output/`.
- Add downloadable output links in the Streamlit UI.
- Add OCR support for scanned PDFs.
- Add integration tests for PDF workflows with small fixture files.
