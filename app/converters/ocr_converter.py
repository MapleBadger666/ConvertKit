from __future__ import annotations

from pathlib import Path
import subprocess
from shutil import which

from PIL import Image, ImageEnhance

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
OCR_LANGUAGE_ERROR_PREFIX = "OCR language data is not installed for"
OCR_MODE_STANDARD = "standard"
OCR_MODE_SCREENSHOT = "screenshot"
OCR_MODE_DOCUMENT = "document"
OCR_MODES = {OCR_MODE_STANDARD, OCR_MODE_SCREENSHOT, OCR_MODE_DOCUMENT}


def ensure_tesseract_available() -> None:
    if not which("tesseract"):
        raise RuntimeError(TESSERACT_ERROR_MESSAGE)


def parse_tesseract_languages(command_output: str) -> set[str]:
    languages: set[str] = set()
    for line in command_output.splitlines():
        language = line.strip()
        if not language or language.lower().startswith("list of available languages"):
            continue
        languages.add(language)

    return languages


def get_installed_tesseract_languages() -> set[str]:
    ensure_tesseract_available()
    try:
        completed = subprocess.run(
            ["tesseract", "--list-langs"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.SubprocessError as exc:
        raise RuntimeError(
            "Could not read installed Tesseract languages. "
            "Run `tesseract --list-langs` to check your local installation."
        ) from exc

    return parse_tesseract_languages(f"{completed.stdout}\n{completed.stderr}")


def required_ocr_languages(language: str) -> set[str]:
    return {part.strip() for part in language.split("+") if part.strip()}


def validate_ocr_language_available(
    language: str,
    installed_languages: set[str] | None = None,
) -> None:
    available_languages = (
        get_installed_tesseract_languages()
        if installed_languages is None
        else installed_languages
    )
    missing_languages = sorted(required_ocr_languages(language) - available_languages)
    if missing_languages:
        missing = ", ".join(missing_languages)
        raise RuntimeError(
            f"{OCR_LANGUAGE_ERROR_PREFIX}: {missing}. "
            "Run `tesseract --list-langs` to see installed languages. "
            "On macOS, install additional language packs with: brew install tesseract-lang"
        )


def ocr_output_path(
    input_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
) -> Path:
    return unique_output_path(input_path, "txt", output_dir)


def normalize_ocr_mode(mode: str) -> str:
    normalized = mode.lower().strip()
    if normalized not in OCR_MODES:
        raise ValueError(f"Unsupported OCR mode: {mode}")

    return normalized


def preprocess_image_for_ocr(
    image: Image.Image,
    scale_factor: int = 2,
    contrast_factor: float = 1.6,
    threshold: int | None = None,
) -> Image.Image:
    processed = image.convert("L")

    if scale_factor > 1:
        width, height = processed.size
        processed = processed.resize(
            (width * scale_factor, height * scale_factor),
            Image.Resampling.LANCZOS,
        )

    if contrast_factor != 1:
        processed = ImageEnhance.Contrast(processed).enhance(contrast_factor)

    if threshold is not None:
        processed = processed.point(lambda pixel: 255 if pixel > threshold else 0)

    return processed


def prepare_image_for_ocr_mode(image: Image.Image, mode: str) -> Image.Image:
    normalized = normalize_ocr_mode(mode)

    if normalized == OCR_MODE_STANDARD:
        return image.copy()

    if normalized == OCR_MODE_SCREENSHOT:
        return preprocess_image_for_ocr(
            image,
            scale_factor=3,
            contrast_factor=1.8,
            threshold=None,
        )

    return preprocess_image_for_ocr(
        image,
        scale_factor=2,
        contrast_factor=2.0,
        threshold=180,
    )


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


def image_to_text(
    input_path: Path,
    language: str = "eng",
    mode: str = OCR_MODE_STANDARD,
) -> str:
    source = Path(input_path)
    if not is_supported_image(source):
        raise ValueError(f"Unsupported image format for OCR: {source.name}")

    ensure_tesseract_available()
    validate_ocr_language_available(language)
    with Image.open(source) as image:
        prepared = prepare_image_for_ocr_mode(image, mode)
        return _image_to_text(prepared, language)


def pdf_to_text_with_ocr(
    input_path: Path,
    output_dir: Path,
    language: str = "eng",
    mode: str = OCR_MODE_STANDARD,
) -> Path:
    source = Path(input_path)
    if not is_supported_pdf(source):
        raise ValueError(f"Unsupported PDF file for OCR: {source.name}")

    ensure_tesseract_available()
    validate_ocr_language_available(language)
    normalized_mode = normalize_ocr_mode(mode)
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
        pages = convert_from_path(source, dpi=300)
    except PDFInfoNotInstalledError as exc:
        raise RuntimeError(POPPLER_ERROR_MESSAGE) from exc

    output_directory = ensure_directory(output_dir)
    output_path = ocr_output_path(source, output_directory)
    chunks: list[str] = []

    for index, page in enumerate(pages, start=1):
        prepared = prepare_image_for_ocr_mode(page, normalized_mode)
        text = _image_to_text(prepared, language).strip()
        chunks.append(f"--- Page {index} ---\n{text}")

    output_path.write_text("\n\n".join(chunks), encoding="utf-8")
    return output_path
