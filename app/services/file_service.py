from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"
UPLOAD_DIR = PROJECT_ROOT / "uploads"

SUPPORTED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "heic", "heif"}
SUPPORTED_PDF_EXTENSIONS = {"pdf"}
SUPPORTED_PPTX_EXTENSIONS = {"pptx"}
SUPPORTED_VIDEO_EXTENSIONS = {"mp4", "mov", "mkv", "avi"}
SUPPORTED_AUDIO_EXTENSIONS = {"mp3", "wav", "m4a", "aac", "flac"}


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


def is_supported_pptx(filename: str | Path) -> bool:
    return get_extension(filename) in SUPPORTED_PPTX_EXTENSIONS


def is_supported_video(filename: str | Path) -> bool:
    return get_extension(filename) in SUPPORTED_VIDEO_EXTENSIONS


def is_supported_audio(filename: str | Path) -> bool:
    return get_extension(filename) in SUPPORTED_AUDIO_EXTENSIONS


def unique_output_path(
    source_path: str | Path,
    target_extension: str,
    output_dir: str | Path = OUTPUT_DIR,
) -> Path:
    output_directory = ensure_directory(output_dir)
    source = Path(source_path)
    extension = target_extension.lower().lstrip(".")
    candidate = output_directory / f"{source.stem}.{extension}"

    counter = 1
    while candidate.exists():
        candidate = output_directory / f"{source.stem}_{counter}.{extension}"
        counter += 1

    return candidate


def create_zip_archive(
    file_paths: list[str | Path],
    output_dir: str | Path = OUTPUT_DIR,
    archive_name: str = "converted-files.zip",
) -> Path:
    if not file_paths:
        raise ValueError("At least one file is required to create a ZIP archive.")

    output_path = unique_output_path(archive_name, "zip", output_dir)

    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as archive:
        used_names: set[str] = set()
        for file_path in file_paths:
            path = Path(file_path)
            arcname = path.name
            counter = 1
            while arcname in used_names:
                arcname = f"{path.stem}_{counter}{path.suffix}"
                counter += 1
            used_names.add(arcname)
            archive.write(path, arcname=arcname)

    return output_path


def save_uploaded_file(uploaded_file, upload_dir: str | Path = UPLOAD_DIR) -> Path:
    upload_directory = ensure_directory(upload_dir)
    destination = upload_directory / Path(uploaded_file.name).name

    if destination.exists():
        destination = upload_directory / f"{destination.stem}-{uuid4().hex[:8]}{destination.suffix}"

    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def save_uploaded_files(uploaded_files, upload_dir: str | Path = UPLOAD_DIR) -> list[Path]:
    return [save_uploaded_file(uploaded_file, upload_dir) for uploaded_file in uploaded_files]
