# FileMorph Stage 4.1 Dependency Size Audit

Generated: 2026-06-20

## Summary

The packaged app size is dominated by Python runtime dependencies rather than
FileMorph source. Stage 4 reduced the runtime source copy to 152K, while the
bundled environment remained 610M. Stage 4.1 splits the runtime into a default
lite profile and an optional full profile.

- `requirements.txt` remains the full online/development dependency set.
- `requirements-runtime-core.txt` contains the default lite runtime.
- `requirements-runtime-heavy.txt` contains optional PDF-to-DOCX, OCR, and
  transcription dependencies.
- `requirements-desktop.txt` still installs the full desktop development
  environment.

## Dependency Findings

| Package | Direct or indirect | Source | Code import/use | Core? | Optional? | Removal risk |
| --- | --- | --- | --- | --- | --- | --- |
| `pyarrow` | Indirect | `streamlit` requires `pyarrow>=7.0` | Streamlit internals; FileMorph does not import it directly | Yes | No | Removing it can break Streamlit tables/data transport at startup or render time. |
| `opencv-python-headless` / `cv2` | Indirect | `pdf2docx` requires `opencv-python-headless>=4.5` | Used by `pdf2docx` when `app/converters/pdf_converter.py` imports `pdf2docx.Converter` inside `pdf_to_docx()` | No | Yes | PDF to DOCX is disabled in lite; other PDF workflows continue. |
| `PyMuPDF` / `pymupdf` / `fitz` | Indirect | `pdf2docx` requires `PyMuPDF>=1.26.7` | Used by `pdf2docx` inside `pdf_to_docx()` | No | Yes | PDF to DOCX is disabled in lite. PDF to TXT and PDF to PNG remain available through `pypdf` and `pdf2image`. |
| `onnxruntime` | Indirect | `faster-whisper` requires `onnxruntime<2` | Loaded by `faster-whisper` after `load_whisper_model()` lazy-imports `WhisperModel` | No | Yes | Audio/video transcription is disabled in lite. |
| `av` | Indirect | `faster-whisper` requires `av>=11` | Used by `faster-whisper`, not directly imported by FileMorph | No | Yes | Audio/video transcription is disabled in lite. Video-to-audio still uses the external `ffmpeg` binary and does not require `av`. |
| `tokenizers` | Indirect | `faster-whisper` requires `tokenizers` | Used by `faster-whisper`, not directly imported by FileMorph | No | Yes | Audio/video transcription is disabled in lite. |
| `hf_xet` | Indirect | `huggingface-hub` pulls `hf-xet` on macOS architectures | Used by Hugging Face model download path, not directly imported by FileMorph | No | Yes | Transcription model download acceleration is unavailable in lite because transcription itself is optional. |
| `huggingface-hub` | Indirect | `faster-whisper` requires `huggingface-hub` | Used by `faster-whisper` model loading | No | Yes | Audio/video transcription is disabled in lite. |
| `ctranslate2` | Indirect | `faster-whisper` requires `ctranslate2` | Used by `faster-whisper` model inference | No | Yes | Audio/video transcription is disabled in lite. |
| `faster-whisper` | Direct full dependency | `requirements-runtime-heavy.txt` through `requirements.txt` | Lazy import in `app/converters/transcription_converter.py::load_whisper_model()` | No | Yes | Audio/video transcription is disabled in lite with a clear optional-dependency message. |
| `pytesseract` | Direct full dependency | `requirements-runtime-heavy.txt` through `requirements.txt` | Lazy import in `app/converters/ocr_converter.py::_image_to_text()` | No | Yes | OCR is disabled in lite with a clear optional-dependency message. |
| `pdf2docx` | Direct full dependency | `requirements-runtime-heavy.txt` through `requirements.txt` | Lazy import in `app/converters/pdf_converter.py::pdf_to_docx()` | No | Yes | PDF to DOCX is disabled in lite with a clear optional-dependency message. |
| `transformers` | Not installed by default | Only `faster-whisper[conversion]` extra would require it | No FileMorph imports | No | Yes | No current runtime impact. Keep out of lite. |
| `openai-whisper` / `whisper` | Not installed | None | No FileMorph imports | No | Yes | No current runtime impact. Keep out of lite. |
| `easyocr` | Not installed | None | No FileMorph imports | No | Yes | No current runtime impact. Keep out of lite. |
| `paddleocr` | Not installed | None | No FileMorph imports | No | Yes | No current runtime impact. Keep out of lite. |

## Lite Runtime Kept

The lite runtime keeps the app shell and common conversion workflows:

- Streamlit and WebView runtime.
- Pillow and `pillow-heif` for image conversion.
- `pypdf` for PDF text extraction.
- `pdf2image` for PDF page image export, with Poppler still required as a system
  tool.
- `python-pptx` and `python-docx` for PPTX text-outline DOCX output.
- External system tools such as Poppler, LibreOffice, Tesseract, and ffmpeg are
  still detected at runtime when a workflow needs them.

## Lite Runtime Optionalized

The lite macOS release prunes the following heavy Python packages from the
bundled environment:

- `pdf2docx`, `opencv-python-headless` / `cv2`, `PyMuPDF` / `pymupdf` / `fitz`,
  and `fire`.
- `pytesseract`.
- `faster-whisper`, `ctranslate2`, `onnxruntime`, `av`, `tokenizers`,
  `huggingface-hub`, `hf_xet`, and `tqdm`.

When users call a missing heavy feature in lite, the converter raises a readable
message asking them to install or use the full version instead of crashing at
app import time.

## Build Profiles

- `--profile lite`: default macOS release profile. Starts from the existing
  project `.venv`, copies it into the app, removes caches, then prunes optional
  heavy packages.
- `--profile full`: keeps the full dependency set after cache cleanup.

The build script does not delete any dependency from the source `.venv`; it only
changes the copied bundled runtime under `dist/FileMorph.app`.
