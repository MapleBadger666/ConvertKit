from __future__ import annotations

from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"
UPLOAD_DIR = PROJECT_ROOT / "uploads"

SUPPORTED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
SUPPORTED_PDF_EXTENSIONS = {"pdf"}


def ensure_directory(path: Path | str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_extension(filename: str | Path) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def is_supported_image(filename: str | Path) -> bool:
    return get_extension(filename) in SUPPORTED_IMAGE_EXTENSIONS


def is_supported_pdf(filename: str | Path) -> bool:
    return get_extension(filename) in SUPPORTED_PDF_EXTENSIONS


def unique_output_path(
    source_path: str | Path,
    target_extension: str,
    output_dir: str | Path = OUTPUT_DIR,
) -> Path:
    output_directory = ensure_directory(output_dir)
    source = Path(source_path)
    extension = target_extension.lower().lstrip(".")
    candidate = output_directory / f"{source.stem}.{extension}"

    if not candidate.exists():
        return candidate

    return output_directory / f"{source.stem}-{uuid4().hex[:8]}.{extension}"


def save_uploaded_file(uploaded_file, upload_dir: str | Path = UPLOAD_DIR) -> Path:
    upload_directory = ensure_directory(upload_dir)
    destination = upload_directory / Path(uploaded_file.name).name

    if destination.exists():
        destination = upload_directory / f"{destination.stem}-{uuid4().hex[:8]}{destination.suffix}"

    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def save_uploaded_files(uploaded_files, upload_dir: str | Path = UPLOAD_DIR) -> list[Path]:
    return [save_uploaded_file(uploaded_file, upload_dir) for uploaded_file in uploaded_files]
