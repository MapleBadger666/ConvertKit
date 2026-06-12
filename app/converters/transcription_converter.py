from __future__ import annotations

from pathlib import Path

from app.converters.media_converter import video_to_audio
from app.services.file_service import (
    OUTPUT_DIR,
    ensure_directory,
    is_supported_audio,
    is_supported_video,
    unique_output_path,
)


FASTER_WHISPER_ERROR_MESSAGE = (
    "Audio transcription requires faster-whisper. Install dependencies with: "
    "python -m pip install -r requirements.txt"
)


def format_timestamp(seconds: float | int | None) -> str:
    total_seconds = max(0, int(seconds or 0))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_transcription_segment(segment) -> str:
    text = getattr(segment, "text", "").strip()
    start = getattr(segment, "start", None)
    end = getattr(segment, "end", None)
    if start is None or end is None:
        return text

    return f"[{format_timestamp(start)} - {format_timestamp(end)}] {text}".rstrip()


def load_whisper_model(model_size: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(FASTER_WHISPER_ERROR_MESSAGE) from exc

    return WhisperModel(model_size, device="cpu", compute_type="int8")


def transcribe_audio_segments(
    input_path: str | Path,
    model_size: str = "base",
    language: str | None = None,
) -> list[str]:
    model = load_whisper_model(model_size)
    segments, _info = model.transcribe(str(input_path), language=language)
    return [
        formatted
        for formatted in (format_transcription_segment(segment) for segment in segments)
        if formatted.strip()
    ]


def audio_to_txt(
    input_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
    model_size: str = "base",
    language: str | None = None,
) -> Path:
    source = Path(input_path)
    if not is_supported_audio(source):
        raise ValueError(f"Unsupported audio file: {source.name}")

    output_directory = ensure_directory(output_dir)
    output_path = unique_output_path(source, "txt", output_directory)
    lines = transcribe_audio_segments(source, model_size, language)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def video_to_txt(
    input_path: str | Path,
    output_dir: str | Path = OUTPUT_DIR,
    model_size: str = "base",
    language: str | None = None,
) -> Path:
    source = Path(input_path)
    if not is_supported_video(source):
        raise ValueError(f"Unsupported video file: {source.name}")

    output_directory = ensure_directory(output_dir)
    audio_path = video_to_audio(source, output_directory, "wav")
    output_path = unique_output_path(source, "txt", output_directory)
    lines = transcribe_audio_segments(audio_path, model_size, language)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
