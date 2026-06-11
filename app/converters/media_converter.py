from __future__ import annotations

from pathlib import Path
import subprocess
from shutil import which

from app.services.file_service import (
    OUTPUT_DIR,
    ensure_directory,
    is_supported_video,
    unique_output_path,
)


FFMPEG_ERROR_MESSAGE = (
    "Video to audio requires ffmpeg. On macOS, install it with: brew install ffmpeg"
)
SUPPORTED_AUDIO_FORMATS = {"wav", "mp3"}


def ensure_ffmpeg_available() -> None:
    if not which("ffmpeg"):
        raise RuntimeError(FFMPEG_ERROR_MESSAGE)


def normalize_audio_format(output_format: str) -> str:
    normalized = output_format.lower().strip().lstrip(".")
    if normalized not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(f"Unsupported audio output format: {output_format}")

    return normalized


def audio_output_path(
    input_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
    output_format: str = "wav",
) -> Path:
    return unique_output_path(input_path, normalize_audio_format(output_format), output_dir)


def video_to_audio(
    input_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
    output_format: str = "wav",
) -> Path:
    source = Path(input_path)
    if not is_supported_video(source):
        raise ValueError(f"Unsupported video file: {source.name}")

    audio_format = normalize_audio_format(output_format)
    ensure_ffmpeg_available()
    output_directory = ensure_directory(output_dir)
    output_path = audio_output_path(source, output_directory, audio_format)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vn",
        str(output_path),
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        message = "Video to audio conversion failed."
        if details:
            message = f"{message} {details}"
        raise RuntimeError(message) from exc

    if not output_path.exists():
        raise RuntimeError("Video to audio conversion failed: no audio file was generated.")

    return output_path
