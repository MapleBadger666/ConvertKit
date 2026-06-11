from pathlib import Path
from types import SimpleNamespace

from app.converters import media_converter
from app.converters.media_converter import (
    FFMPEG_ERROR_MESSAGE,
    audio_output_path,
    ensure_ffmpeg_available,
    normalize_audio_format,
    video_to_audio,
)


def test_ensure_ffmpeg_available_raises_readable_error_when_missing(monkeypatch):
    monkeypatch.setattr(media_converter, "which", lambda command: None)

    try:
        ensure_ffmpeg_available()
    except RuntimeError as exc:
        assert str(exc) == FFMPEG_ERROR_MESSAGE
    else:
        raise AssertionError("Expected missing ffmpeg to raise RuntimeError")


def test_normalize_audio_format_accepts_wav_and_mp3():
    assert normalize_audio_format("WAV") == "wav"
    assert normalize_audio_format(".mp3") == "mp3"


def test_normalize_audio_format_rejects_unknown_format():
    try:
        normalize_audio_format("aac")
    except ValueError as exc:
        assert "Unsupported audio output format" in str(exc)
    else:
        raise AssertionError("Expected unsupported audio format to raise ValueError")


def test_audio_output_path_uses_requested_extension(tmp_path: Path):
    output_path = audio_output_path("movie.mp4", tmp_path, "mp3")

    assert output_path == tmp_path / "movie.mp3"


def test_video_to_audio_uses_ffmpeg_without_requiring_real_ffmpeg(
    monkeypatch,
    tmp_path: Path,
):
    source = tmp_path / "movie.mp4"
    source.write_bytes(b"fake video")

    def fake_run(command, check, capture_output, text):
        assert command[:4] == ["ffmpeg", "-y", "-i", str(source)]
        assert "-vn" in command
        Path(command[-1]).write_bytes(b"fake audio")
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(media_converter, "ensure_ffmpeg_available", lambda: None)
    monkeypatch.setattr(media_converter.subprocess, "run", fake_run)

    output_path = video_to_audio(source, tmp_path, "wav")

    assert output_path == tmp_path / "movie.wav"
    assert output_path.read_bytes() == b"fake audio"
