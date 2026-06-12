# Engineering Audit: v0.3.2 Audio and Video Transcription

## Scope

This audit covers v0.3.2 local audio and video transcription for ConvertKit/FileMorph. The work adds faster-whisper based TXT transcription while preserving the existing image, PDF, OCR, Office, media, TXT preview, and download flows.

## Changed Files

- `app/converters/transcription_converter.py`: added local audio transcription, video transcription through existing ffmpeg audio extraction, timestamp formatting, and faster-whisper dependency handling.
- `app/main.py`: added `Audio to TXT` and `Video to TXT`, upload filters, model selector, language selector, and conversion dispatch.
- `app/services/file_service.py`: added audio extension validation.
- `requirements.txt`: added `faster-whisper`.
- `tests/test_transcription_converter.py`: added timestamp, dependency error, mocked transcription, and mocked video extraction tests.
- `tests/test_file_service.py`: added audio extension tests.
- `tests/test_main_helpers.py`: added transcription upload filter and language/model option tests.
- `README.md`: documented local transcription, first-run model download behavior, model tradeoffs, and limitations.
- `CHANGELOG.md`: added v0.3.2 notes.
- `audits/ENGINEERING_AUDIT_V0_3_2_AUDIO_VIDEO_TRANSCRIPTION.md`: added this audit.

## New Conversion Options

- `Audio to TXT`
- `Video to TXT`

## Local-Only Behavior

- Audio transcription uses local faster-whisper after model files are available.
- Video transcription first extracts WAV audio through the existing local ffmpeg converter, then transcribes the extracted audio.
- No cloud APIs were added.

## Verification

- Ran `python -m pytest -q`.
- Result: `71 passed in 0.34s`.
- Manual Streamlit UI check confirmed `Audio to TXT` appears.
- Manual Streamlit UI check confirmed `Video to TXT` appears.
- Manual Streamlit UI check confirmed audio upload filtering shows `MP3, WAV, M4A, AAC, FLAC`.
- Manual Streamlit UI check confirmed video upload filtering shows `MP4, MOV, MKV, AVI`.
- Manual Streamlit UI check confirmed the transcription model selector shows `tiny`, `base`, and `small` with `base` selected by default.
- Manual Streamlit UI check confirmed the transcription language selector shows `Auto-detect`, `English`, and `Simplified Chinese`.
- Manual Streamlit UI check confirmed existing image, PDF, Office, media, and OCR options still render.

## Notes

- Tests mock faster-whisper model loading and transcription so they do not download models or require network access.
- Video transcription tests mock `video_to_audio` so ffmpeg is not required during tests.
