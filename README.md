# FileMorph

FileMorph is a local-only Streamlit file conversion toolkit for documents, images, OCR, media, and transcription. It is built for practical desktop workflows where files stay on your machine and generated outputs are saved to `output/`.

## Preview

![FileMorph v0.4 main UI](docs/screenshots/v0.4.0-main-ui.png)

![FileMorph transcription UI](docs/screenshots/v0.4.0-transcription-ui.png)

## Local-Only Privacy Note

FileMorph runs locally. Uploaded files are written to the local `uploads/` directory, converted files are written to `output/`, and no cloud APIs or external upload services are used by the app.

## Features

| Group | Features |
| --- | --- |
| Images | Batch JPG, JPEG, PNG, WEBP, HEIC, and HEIF conversion; combine images into one PDF or create one PDF per image. |
| PDF | Convert PDF pages to PNG, extract selectable PDF text to TXT, convert PDF to DOCX. |
| OCR | Extract text from images and scanned PDFs with local Tesseract OCR. |
| Office | Convert PPTX to PDF; convert PPTX to DOCX as editable outline, slide images, or mixed output. |
| Media | Extract WAV or MP3 audio from video files. |
| Transcription | Transcribe local audio and video files to timestamped TXT with faster-whisper. |

## Batch Workflow

FileMorph supports multi-file uploads for local, synchronous batch conversion. Images to one PDF combines many images into one PDF; Images to separate PDFs creates one PDF per image. Each run shows simple progress, a success/failure summary, an output file table, individual downloads, and a ZIP download when multiple files are generated. Recent conversion history is stored only in the current Streamlit session and can be cleared from the app.

## Quick Start

1. Clone and enter the project:

```bash
git clone <repository-url>
cd ConvertKit
```

2. Create an environment and install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

3. Install the local system tools needed for the workflows you want. On macOS, the full toolchain is:

```bash
brew install poppler tesseract tesseract-lang ffmpeg
brew install --cask libreoffice
```

4. Run the app:

```bash
streamlit run app/main.py
```

Then open the local Streamlit URL shown in the terminal.

Run tests:

```bash
python -m pytest -q
```

## System Dependencies

| Dependency | Required for | macOS install command |
| --- | --- | --- |
| Poppler | PDF to PNG, scanned PDF OCR, PPTX slide-image DOCX | `brew install poppler` |
| Tesseract | Image OCR, scanned PDF OCR | `brew install tesseract` |
| Tesseract language data | Chinese OCR language options | `brew install tesseract-lang` |
| LibreOffice | PPTX to PDF, PPTX slide-image DOCX | `brew install --cask libreoffice` |
| ffmpeg | Video to Audio, Video to TXT, audio preprocessing | `brew install ffmpeg` |
| faster-whisper | Audio to TXT, Video to TXT | `python -m pip install -r requirements.txt` |

## Current Limitations

- OCR and transcription quality depends on source clarity, noise, volume, language selection, and installed language data.
- PPTX to DOCX layout preservation is best in Slide Images mode; editable Text Outline mode does not reproduce the original slide layout.
- The first real transcription may download the selected Whisper model locally.
- HEIC/HEIF input requires the Python dependency `pillow-heif`.
- Long videos and large PDFs may take time to process.
- Uploaded source files remain in `uploads/` and generated files remain in `output/` until manually removed.

## License

MIT License. See `LICENSE`.
