from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.converters.image_converter import prepare_image_for_format
from app.services.file_service import (
    OUTPUT_DIR,
    ensure_directory,
    is_supported_image,
    is_supported_pdf,
    unique_output_path,
)


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

    try:
        for image_path in image_paths:
            source = Path(image_path)
            if not is_supported_image(source):
                raise ValueError(f"Unsupported image format: {source.name}")

            with Image.open(source) as image:
                pdf_images.append(prepare_image_for_format(image, "jpg").copy())

        first, *remaining = pdf_images
        first.save(output_path, save_all=True, append_images=remaining)
    finally:
        for image in pdf_images:
            image.close()

    return output_path


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
    except ImportError as exc:
        raise RuntimeError("pdf2image is required for PDF to PNG conversion.") from exc

    output_directory = ensure_directory(output_dir)
    pages = convert_from_path(source, dpi=dpi)
    output_paths: list[Path] = []

    for index, page in enumerate(pages, start=1):
        output_path = output_directory / f"{source.stem}-page-{index}.png"
        if output_path.exists():
            output_path = unique_output_path(f"{source.stem}-page-{index}.png", "png", output_directory)
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
