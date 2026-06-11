from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
from shutil import which

from app.services.file_service import (
    OUTPUT_DIR,
    ensure_directory,
    is_supported_pptx,
    unique_output_path,
)


LIBREOFFICE_ERROR_MESSAGE = (
    "PPTX to PDF requires LibreOffice. On macOS, install it with: "
    "brew install --cask libreoffice"
)
MACOS_SOFFICE_PATH = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")


def soffice_executable() -> str | None:
    executable = which("soffice")
    if executable:
        return executable

    if MACOS_SOFFICE_PATH.exists():
        return str(MACOS_SOFFICE_PATH)

    return None


def ensure_soffice_available() -> str:
    executable = soffice_executable()
    if not executable:
        raise RuntimeError(LIBREOFFICE_ERROR_MESSAGE)

    return executable


def pptx_to_pdf(
    input_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
) -> Path:
    source = Path(input_path)
    if not is_supported_pptx(source):
        raise ValueError(f"Unsupported PowerPoint file: {source.name}")

    executable = ensure_soffice_available()
    output_directory = ensure_directory(output_dir)

    with tempfile.TemporaryDirectory(dir=output_directory) as temporary_directory:
        try:
            subprocess.run(
                [
                    executable,
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    temporary_directory,
                    str(source),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            details = (exc.stderr or exc.stdout or "").strip()
            message = "PPTX to PDF conversion failed."
            if details:
                message = f"{message} {details}"
            raise RuntimeError(message) from exc

        converted_path = Path(temporary_directory) / f"{source.stem}.pdf"
        if not converted_path.exists():
            raise RuntimeError("PPTX to PDF conversion failed: no PDF was generated.")

        output_path = unique_output_path(source, "pdf", output_directory)
        shutil.move(str(converted_path), output_path)

    return output_path


def clean_text_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def text_lines_from_shape(shape) -> list[str]:
    if not shape or not getattr(shape, "has_text_frame", False):
        return []

    text_frame = getattr(shape, "text_frame", None)
    return clean_text_lines(getattr(text_frame, "text", ""))


def speaker_note_lines(slide) -> list[str]:
    try:
        notes_slide = slide.notes_slide
    except Exception:
        return []

    text_frame = getattr(notes_slide, "notes_text_frame", None)
    return clean_text_lines(getattr(text_frame, "text", ""))


def slide_text_sections(slide) -> tuple[str, list[str], list[str]]:
    shapes = getattr(slide, "shapes", [])
    title_shape = getattr(shapes, "title", None)
    title_lines = text_lines_from_shape(title_shape)
    title = title_lines[0] if title_lines else ""
    content_lines: list[str] = []

    for shape in shapes:
        if shape is title_shape:
            continue
        content_lines.extend(text_lines_from_shape(shape))

    return title, content_lines, speaker_note_lines(slide)


def pptx_to_docx(
    input_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
) -> Path:
    source = Path(input_path)
    if not is_supported_pptx(source):
        raise ValueError(f"Unsupported PowerPoint file: {source.name}")

    try:
        from docx import Document
        from pptx import Presentation
    except ImportError as exc:
        raise RuntimeError(
            "python-pptx and python-docx are required for PPTX to DOCX conversion."
        ) from exc

    output_path = unique_output_path(source, "docx", output_dir)
    presentation = Presentation(str(source))
    document = Document()

    for index, slide in enumerate(presentation.slides, start=1):
        if index > 1:
            document.add_page_break()

        title, content_lines, notes_lines = slide_text_sections(slide)
        document.add_heading(f"Slide {index}", level=1)
        document.add_paragraph(f"Title: {title}")
        document.add_paragraph("Content:")
        if content_lines:
            for line in content_lines:
                document.add_paragraph(line, style="List Bullet")
        else:
            document.add_paragraph("(No slide body text found.)")

        if notes_lines:
            document.add_paragraph("Speaker Notes:")
            for line in notes_lines:
                document.add_paragraph(line, style="List Bullet")

    document.save(output_path)
    return output_path
