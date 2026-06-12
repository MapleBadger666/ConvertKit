from pathlib import Path
from types import SimpleNamespace
import builtins

from app.converters import transcription_converter
from app.converters.transcription_converter import (
    FASTER_WHISPER_ERROR_MESSAGE,
    audio_to_txt,
    format_timestamp,
    format_transcription_segment,
    load_whisper_model,
    transcribe_audio_segments,
    video_to_txt,
)


def test_format_timestamp_uses_hours_minutes_and_seconds():
    assert format_timestamp(0) == "00:00:00"
    assert format_timestamp(1.9) == "00:00:01"
    assert format_timestamp(65) == "00:01:05"
    assert format_timestamp(3661) == "01:01:01"


def test_format_transcription_segment_includes_timestamps_when_available():
    segment = SimpleNamespace(start=1.2, end=4.8, text=" hello world ")

    assert format_transcription_segment(segment) == "[00:00:01 - 00:00:04] hello world"


def test_format_transcription_segment_handles_missing_timestamps():
    segment = SimpleNamespace(text=" hello world ")

    assert format_transcription_segment(segment) == "hello world"


def test_load_whisper_model_raises_readable_error_when_missing(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "faster_whisper":
            raise ImportError("missing faster-whisper")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        load_whisper_model("base")
    except RuntimeError as exc:
        assert str(exc) == FASTER_WHISPER_ERROR_MESSAGE
    else:
        raise AssertionError("Expected missing faster-whisper to raise RuntimeError")


def test_transcribe_audio_segments_uses_model_without_downloading(monkeypatch, tmp_path: Path):
    audio_path = tmp_path / "speech.wav"
    audio_path.write_bytes(b"fake audio")
    calls = []

    class FakeModel:
        def transcribe(self, input_path, language=None):
            calls.append((input_path, language))
            return [
                SimpleNamespace(start=1, end=3, text=" First line "),
                SimpleNamespace(start=4, end=7, text=" Second line "),
            ], SimpleNamespace()

    monkeypatch.setattr(
        transcription_converter,
        "load_whisper_model",
        lambda model_size: FakeModel(),
    )

    lines = transcribe_audio_segments(audio_path, "tiny", "en")

    assert calls == [(str(audio_path), "en")]
    assert lines == [
        "[00:00:01 - 00:00:03] First line",
        "[00:00:04 - 00:00:07] Second line",
    ]


def test_audio_to_txt_writes_transcription_output(monkeypatch, tmp_path: Path):
    source = tmp_path / "speech.mp3"
    source.write_bytes(b"fake audio")

    monkeypatch.setattr(
        transcription_converter,
        "transcribe_audio_segments",
        lambda input_path, model_size, language: [
            "[00:00:01 - 00:00:03] Hello",
            "[00:00:04 - 00:00:06] World",
        ],
    )

    output_path = audio_to_txt(source, tmp_path, "base", None)

    assert output_path == tmp_path / "speech.txt"
    assert output_path.read_text(encoding="utf-8") == (
        "[00:00:01 - 00:00:03] Hello\n"
        "[00:00:04 - 00:00:06] World"
    )


def test_audio_to_txt_rejects_unsupported_audio(tmp_path: Path):
    source = tmp_path / "speech.mp4"
    source.write_bytes(b"fake video")

    try:
        audio_to_txt(source, tmp_path)
    except ValueError as exc:
        assert "Unsupported audio file" in str(exc)
    else:
        raise AssertionError("Expected unsupported audio file to raise ValueError")


def test_video_to_txt_extracts_audio_then_transcribes(monkeypatch, tmp_path: Path):
    source = tmp_path / "clip.mp4"
    source.write_bytes(b"fake video")
    extracted_audio = tmp_path / "clip.wav"
    calls = []

    def fake_video_to_audio(input_path, output_dir, output_format):
        calls.append((input_path, output_dir, output_format))
        extracted_audio.write_bytes(b"fake audio")
        return extracted_audio

    def fake_transcribe(input_path, model_size, language):
        assert input_path == extracted_audio
        assert model_size == "small"
        assert language == "zh"
        return ["[00:00:01 - 00:00:02] 你好"]

    monkeypatch.setattr(transcription_converter, "video_to_audio", fake_video_to_audio)
    monkeypatch.setattr(
        transcription_converter,
        "transcribe_audio_segments",
        fake_transcribe,
    )

    output_path = video_to_txt(source, tmp_path, "small", "zh")

    assert calls == [(source, tmp_path, "wav")]
    assert output_path == tmp_path / "clip.txt"
    assert output_path.read_text(encoding="utf-8") == "[00:00:01 - 00:00:02] 你好"


def test_video_to_txt_rejects_unsupported_video(tmp_path: Path):
    source = tmp_path / "clip.wav"
    source.write_bytes(b"fake audio")

    try:
        video_to_txt(source, tmp_path)
    except ValueError as exc:
        assert "Unsupported video file" in str(exc)
    else:
        raise AssertionError("Expected unsupported video file to raise ValueError")
