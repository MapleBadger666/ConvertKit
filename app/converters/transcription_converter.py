from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

from app.converters.media_converter import ensure_ffmpeg_available, video_to_audio
from app.services.file_service import (
    OUTPUT_DIR,
    ensure_directory,
    is_supported_audio,
    is_supported_video,
    unique_output_path,
)


FASTER_WHISPER_ERROR_MESSAGE = (
    "This feature requires optional transcription dependencies. Please install the full version."
)
AUDIO_PREPROCESSING_ERROR_MESSAGE = (
    "Audio preprocessing failed. Make sure ffmpeg is installed and the file has a "
    "valid audio track."
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


def transcription_beam_size(model_size: str) -> int:
    if model_size == "tiny":
        return 1

    return 5


def language_display_name(language: str | None) -> str:
    if language == "en":
        return "English"

    if language == "zh":
        return "Simplified Chinese"

    return "Auto-detect"


def transcription_header(
    input_filename: str,
    conversion_name: str,
    model_size: str,
    language: str | None,
) -> str:
    return "\n".join(
        [
            f"File: {input_filename}",
            f"Conversion: {conversion_name}",
            f"Model: {model_size}",
            f"Language: {language_display_name(language)}",
            "Notes: Local faster-whisper transcription. Accuracy depends on audio quality.",
        ]
    )


def transcription_text(
    input_filename: str,
    conversion_name: str,
    model_size: str,
    language: str | None,
    segment_lines: list[str],
) -> str:
    header = transcription_header(input_filename, conversion_name, model_size, language)
    if not segment_lines:
        return f"{header}\n\n(No speech detected.)"

    return f"{header}\n\n" + "\n".join(segment_lines)


def normalized_audio_path(
    input_path: str | Path,
    output_dir: str | Path,
) -> Path:
    output_directory = ensure_directory(output_dir)
    return output_directory / f"{Path(input_path).stem}-normalized.wav"


def normalize_audio_to_wav(
    input_path: str | Path,
    output_dir: str | Path,
) -> Path:
    source = Path(input_path)
    output_path = normalized_audio_path(source, output_dir)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]

    try:
        ensure_ffmpeg_available()
        subprocess.run(command, check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        raise RuntimeError(AUDIO_PREPROCESSING_ERROR_MESSAGE) from exc

    if not output_path.exists():
        raise RuntimeError(AUDIO_PREPROCESSING_ERROR_MESSAGE)

    return output_path


def load_whisper_model(model_size: str):
    WhisperModel = load_whisper_model_class()
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def load_whisper_model_class():
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(FASTER_WHISPER_ERROR_MESSAGE) from exc

    return WhisperModel


def ensure_transcription_dependency_available() -> None:
    load_whisper_model_class()


def transcribe_audio_segments(
    input_path: str | Path,
    model_size: str = "base",
    language: str | None = None,
) -> list[str]:
    model = load_whisper_model(model_size)
    segments, _info = model.transcribe(
        str(input_path),
        language=language,
        beam_size=transcription_beam_size(model_size),
    )
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

    ensure_transcription_dependency_available()
    output_directory = ensure_directory(output_dir)
    output_path = unique_output_path(source, "txt", output_directory)
    with tempfile.TemporaryDirectory(dir=output_directory) as temporary_dir:
        normalized_audio = normalize_audio_to_wav(source, temporary_dir)
        lines = transcribe_audio_segments(normalized_audio, model_size, language)

    output_path.write_text(
        transcription_text(source.name, "Audio to TXT", model_size, language, lines),
        encoding="utf-8",
    )
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

    ensure_transcription_dependency_available()
    output_directory = ensure_directory(output_dir)
    output_path = unique_output_path(source, "txt", output_directory)
    with tempfile.TemporaryDirectory(dir=output_directory) as temporary_dir:
        extracted_audio = video_to_audio(source, temporary_dir, "wav")
        normalized_audio = normalize_audio_to_wav(extracted_audio, temporary_dir)
        lines = transcribe_audio_segments(normalized_audio, model_size, language)

    output_path.write_text(
        transcription_text(source.name, "Video to TXT", model_size, language, lines),
        encoding="utf-8",
    )
    return output_path
