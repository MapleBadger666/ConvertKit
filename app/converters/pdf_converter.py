from __future__ import annotations

from pathlib import Path
from shutil import which

from PIL import Image, ImageOps

from app.converters.image_converter import ensure_heif_support
from app.services.file_service import (
    OUTPUT_DIR,
    ensure_directory,
    is_supported_image,
    is_supported_pdf,
    unique_output_path,
)


POPPLER_ERROR_MESSAGE = (
    "PDF-to-PNG requires Poppler. On macOS, install it with: brew install poppler"
)


def ensure_pdf_image_save_support() -> None:
    if "JPEG" not in Image.SAVE:
        Image.init()


def prepare_image_for_pdf(image: Image.Image) -> Image.Image:
    prepared = ImageOps.exif_transpose(image)
    if prepared.mode in {"RGBA", "LA"} or (
        prepared.mode == "P" and "transparency" in prepared.info
    ):
        rgba = prepared.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background

    if prepared.mode != "RGB":
        return prepared.convert("RGB")

    return prepared.copy()


def ensure_poppler_available() -> None:
    if not which("pdfinfo") or not which("pdftoppm"):
        raise RuntimeError(POPPLER_ERROR_MESSAGE)


def images_to_pdf(
    image_paths: list[str | Path],
    output_dir: str | Path = OUTPUT_DIR,
    output_name: str = "converted-images.pdf",
) -> Path:
    if not image_paths:
        raise ValueError("At least one image is required to create a PDF.")

    output_directory = ensure_directory(output_dir)
    output_path = unique_output_path(output_name, "pdf", output_directory)
    pdf_images: list[Image.Image] = []
    ensure_pdf_image_save_support()

    try:
        for image_path in image_paths:
            source = Path(image_path)
            if not is_supported_image(source):
                raise ValueError(f"Unsupported image format: {source.name}")

            ensure_heif_support(source)
            with Image.open(source) as image:
                pdf_images.append(prepare_image_for_pdf(image))

        first, *remaining = pdf_images
        first.save(output_path, "PDF", save_all=True, append_images=remaining)
    finally:
        for image in pdf_images:
            image.close()

    return output_path


def image_to_pdf(
    image_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
) -> Path:
    source = Path(image_path)
    return images_to_pdf([source], output_dir, f"{source.stem}.pdf")


def pdf_to_png(
    pdf_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
    dpi: int = 200,
) -> list[Path]:
    source = Path(pdf_path)
    if not is_supported_pdf(source):
        raise ValueError(f"Unsupported PDF file: {source.name}")

    try:
        from pdf2image import convert_from_path
        from pdf2image.exceptions import PDFInfoNotInstalledError
    except ImportError as exc:
        raise RuntimeError("pdf2image is required for PDF to PNG conversion.") from exc

    ensure_poppler_available()
    output_directory = ensure_directory(output_dir)
    try:
        pages = convert_from_path(source, dpi=dpi)
    except PDFInfoNotInstalledError as exc:
        raise RuntimeError(POPPLER_ERROR_MESSAGE) from exc

    output_paths: list[Path] = []

    for index, page in enumerate(pages, start=1):
        output_path = unique_output_path(
            f"{source.stem}-page-{index}.png",
            "png",
            output_directory,
        )
        page.save(output_path, "PNG")
        output_paths.append(output_path)

    return output_paths


def pdf_to_txt(pdf_path: str | Path, output_dir: str | Path = OUTPUT_DIR) -> Path:
    source = Path(pdf_path)
    if not is_supported_pdf(source):
        raise ValueError(f"Unsupported PDF file: {source.name}")

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required for PDF to TXT conversion.") from exc

    output_path = unique_output_path(source, "txt", output_dir)
    reader = PdfReader(str(source))
    text_chunks = []

    for page in reader.pages:
        text_chunks.append(page.extract_text() or "")

    output_path.write_text("\n\n".join(text_chunks), encoding="utf-8")
    return output_path


def pdf_to_docx(pdf_path: str | Path, output_dir: str | Path = OUTPUT_DIR) -> Path:
    source = Path(pdf_path)
    if not is_supported_pdf(source):
        raise ValueError(f"Unsupported PDF file: {source.name}")

    try:
        from pdf2docx import Converter
    except ImportError as exc:
        raise RuntimeError("pdf2docx is required for PDF to DOCX conversion.") from exc

    output_path = unique_output_path(source, "docx", output_dir)
    converter = Converter(str(source))

    try:
        converter.convert(str(output_path))
    finally:
        converter.close()

    return output_path
