from pathlib import Path
from types import SimpleNamespace
import builtins

from app.converters import transcription_converter
from app.converters.transcription_converter import (
    AUDIO_PREPROCESSING_ERROR_MESSAGE,
    FASTER_WHISPER_ERROR_MESSAGE,
    audio_to_txt,
    format_timestamp,
    format_transcription_segment,
    language_display_name,
    load_whisper_model,
    normalize_audio_to_wav,
    transcription_beam_size,
    transcription_header,
    transcription_text,
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


def test_transcription_beam_size_prefers_quality_for_base_and_small():
    assert transcription_beam_size("tiny") == 1
    assert transcription_beam_size("base") == 5
    assert transcription_beam_size("small") == 5


def test_language_display_name_maps_codes_to_ui_labels():
    assert language_display_name(None) == "Auto-detect"
    assert language_display_name("en") == "English"
    assert language_display_name("zh") == "Simplified Chinese"


def test_transcription_header_includes_file_conversion_model_and_language():
    header = transcription_header("clip.mov", "Video to TXT", "small", "zh")

    assert header == (
        "File: clip.mov\n"
        "Conversion: Video to TXT\n"
        "Model: small\n"
        "Language: Simplified Chinese\n"
        "Notes: Local faster-whisper transcription. Accuracy depends on audio quality."
    )


def test_transcription_text_adds_header_before_segments():
    text = transcription_text(
        "speech.mp3",
        "Audio to TXT",
        "base",
        "en",
        ["[00:00:01 - 00:00:02] Hello"],
    )

    assert text == (
        "File: speech.mp3\n"
        "Conversion: Audio to TXT\n"
        "Model: base\n"
        "Language: English\n"
        "Notes: Local faster-whisper transcription. Accuracy depends on audio quality.\n\n"
        "[00:00:01 - 00:00:02] Hello"
    )


def test_normalize_audio_to_wav_uses_stable_ffmpeg_settings(monkeypatch, tmp_path: Path):
    source = tmp_path / "speech.m4a"
    source.write_bytes(b"fake audio")
    calls = []

    def fake_run(command, check, capture_output, text):
        calls.append(command)
        Path(command[-1]).write_bytes(b"normalized wav")

    monkeypatch.setattr(transcription_converter, "ensure_ffmpeg_available", lambda: None)
    monkeypatch.setattr(transcription_converter.subprocess, "run", fake_run)

    output_path = normalize_audio_to_wav(source, tmp_path)

    assert output_path == tmp_path / "speech-normalized.wav"
    assert calls == [
        [
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
    ]


def test_normalize_audio_to_wav_wraps_ffmpeg_failures(monkeypatch, tmp_path: Path):
    source = tmp_path / "broken.wav"
    source.write_bytes(b"fake audio")

    def fake_run(command, check, capture_output, text):
        raise transcription_converter.subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(transcription_converter, "ensure_ffmpeg_available", lambda: None)
    monkeypatch.setattr(transcription_converter.subprocess, "run", fake_run)

    try:
        normalize_audio_to_wav(source, tmp_path)
    except RuntimeError as exc:
        assert str(exc) == AUDIO_PREPROCESSING_ERROR_MESSAGE
    else:
        raise AssertionError("Expected ffmpeg failure to raise preprocessing error")


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
        def transcribe(self, input_path, language=None, beam_size=None):
            calls.append((input_path, language, beam_size))
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

    assert calls == [(str(audio_path), "en", 1)]
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
    monkeypatch.setattr(
        transcription_converter,
        "normalize_audio_to_wav",
        lambda input_path, output_dir: tmp_path / "speech-normalized.wav",
    )

    output_path = audio_to_txt(source, tmp_path, "base", None)

    assert output_path == tmp_path / "speech.txt"
    assert output_path.read_text(encoding="utf-8") == (
        "File: speech.mp3\n"
        "Conversion: Audio to TXT\n"
        "Model: base\n"
        "Language: Auto-detect\n"
        "Notes: Local faster-whisper transcription. Accuracy depends on audio quality.\n\n"
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
    normalized_audio = tmp_path / "clip-normalized.wav"
    calls = []

    def fake_video_to_audio(input_path, output_dir, output_format):
        calls.append((input_path, output_dir, output_format))
        extracted_audio.write_bytes(b"fake audio")
        return extracted_audio

    def fake_normalize(input_path, output_dir):
        assert input_path == extracted_audio
        normalized_audio.write_bytes(b"normalized audio")
        return normalized_audio

    def fake_transcribe(input_path, model_size, language):
        assert input_path == normalized_audio
        assert model_size == "small"
        assert language == "zh"
        return ["[00:00:01 - 00:00:02] 你好"]

    monkeypatch.setattr(transcription_converter, "video_to_audio", fake_video_to_audio)
    monkeypatch.setattr(transcription_converter, "normalize_audio_to_wav", fake_normalize)
    monkeypatch.setattr(
        transcription_converter,
        "transcribe_audio_segments",
        fake_transcribe,
    )

    output_path = video_to_txt(source, tmp_path, "small", "zh")

    assert calls[0][0] == source
    assert calls[0][2] == "wav"
    assert output_path == tmp_path / "clip.txt"
    assert output_path.read_text(encoding="utf-8") == (
        "File: clip.mp4\n"
        "Conversion: Video to TXT\n"
        "Model: small\n"
        "Language: Simplified Chinese\n"
        "Notes: Local faster-whisper transcription. Accuracy depends on audio quality.\n\n"
        "[00:00:01 - 00:00:02] 你好"
    )


def test_video_to_txt_rejects_unsupported_video(tmp_path: Path):
    source = tmp_path / "clip.wav"
    source.write_bytes(b"fake audio")

    try:
        video_to_txt(source, tmp_path)
    except ValueError as exc:
        assert "Unsupported video file" in str(exc)
    else:
        raise AssertionError("Expected unsupported video file to raise ValueError")
