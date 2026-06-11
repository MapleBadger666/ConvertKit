from __future__ import annotations

from pathlib import Path
from shutil import which

from PIL import Image

from app.converters.pdf_converter import POPPLER_ERROR_MESSAGE, ensure_poppler_available
from app.services.file_service import (
    OUTPUT_DIR,
    ensure_directory,
    is_supported_image,
    is_supported_pdf,
    unique_output_path,
)


TESSERACT_ERROR_MESSAGE = (
    "OCR requires Tesseract. On macOS, install it with: brew install tesseract"
)


def ensure_tesseract_available() -> None:
    if not which("tesseract"):
        raise RuntimeError(TESSERACT_ERROR_MESSAGE)


def ocr_output_path(
    input_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
) -> Path:
    return unique_output_path(input_path, "txt", output_dir)


def _image_to_text(image: Image.Image, language: str) -> str:
    try:
        import pytesseract
        from pytesseract import TesseractNotFoundError
    except ImportError as exc:
        raise RuntimeError("pytesseract is required for OCR conversion.") from exc

    try:
        return pytesseract.image_to_string(image, lang=language)
    except TesseractNotFoundError as exc:
        raise RuntimeError(TESSERACT_ERROR_MESSAGE) from exc


def image_to_text(input_path: Path, language: str = "eng") -> str:
    source = Path(input_path)
    if not is_supported_image(source):
        raise ValueError(f"Unsupported image format for OCR: {source.name}")

    ensure_tesseract_available()
    with Image.open(source) as image:
        return _image_to_text(image, language)


def pdf_to_text_with_ocr(
    input_path: Path,
    output_dir: Path,
    language: str = "eng",
) -> Path:
    source = Path(input_path)
    if not is_supported_pdf(source):
        raise ValueError(f"Unsupported PDF file for OCR: {source.name}")

    ensure_tesseract_available()
    try:
        ensure_poppler_available()
    except RuntimeError as exc:
        if str(exc) == POPPLER_ERROR_MESSAGE:
            raise
        raise

    try:
        from pdf2image import convert_from_path
        from pdf2image.exceptions import PDFInfoNotInstalledError
    except ImportError as exc:
        raise RuntimeError("pdf2image is required for PDF OCR conversion.") from exc

    try:
        pages = convert_from_path(source)
    except PDFInfoNotInstalledError as exc:
        raise RuntimeError(POPPLER_ERROR_MESSAGE) from exc

    output_directory = ensure_directory(output_dir)
    output_path = ocr_output_path(source, output_directory)
    chunks: list[str] = []

    for index, page in enumerate(pages, start=1):
        text = _image_to_text(page, language).strip()
        chunks.append(f"--- Page {index} ---\n{text}")

    output_path.write_text("\n\n".join(chunks), encoding="utf-8")
    return output_path
