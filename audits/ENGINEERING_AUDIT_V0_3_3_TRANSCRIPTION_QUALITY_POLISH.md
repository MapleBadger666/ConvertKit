# Engineering Audit: v0.3.3 Transcription Quality Polish

## Scope

This audit covers v0.3.3 transcription quality polish for ConvertKit/FileMorph. The work improves local Audio to TXT and Video to TXT transcription by normalizing audio before faster-whisper, adding clearer transcript metadata, and providing user-facing model and language guidance.

## Changed Files

- `app/converters/transcription_converter.py`: added ffmpeg-based audio normalization, transcript headers, language display labels, beam-size selection, and audio preprocessing errors.
- `app/main.py`: added transcription guidance text and post-conversion advice.
- `tests/test_transcription_converter.py`: added tests for normalization command construction, preprocessing errors, beam size, transcript headers, and normalized audio flow.
- `tests/test_main_helpers.py`: added tests for transcription guidance and advice helpers.
- `README.md`: added transcription quality tips and audio preprocessing error documentation.
- `CHANGELOG.md`: added v0.3.3 notes.
- `audits/ENGINEERING_AUDIT_V0_3_3_TRANSCRIPTION_QUALITY_POLISH.md`: added this audit.

## Transcription Behavior

- Audio uploads are normalized to temporary WAV before transcription.
- Video uploads first use the existing ffmpeg video-to-audio path, then normalize the extracted audio to temporary WAV before transcription.
- Normalized audio is mono, 16 kHz, PCM signed 16-bit WAV.
- Transcript TXT output includes file, conversion type, model size, language, and a local transcription quality note before timestamped segments.
- Existing uploaded files are not modified.

## Local-Only Notes

- No cloud APIs were added.
- Tests mock faster-whisper and ffmpeg behavior, so they do not download models or require network access.
- Real transcription still may download a selected Whisper model on first use.

## Verification

- Ran `python -m pytest -q`.
- Result: `79 passed in 0.50s`.
- Manual Streamlit UI check confirmed `Audio to TXT` still appears.
- Manual Streamlit UI check confirmed `Video to TXT` still appears.
- Manual Streamlit UI check confirmed transcription model and language selectors still appear.
- Manual Streamlit UI check confirmed model guidance is visible.
- Manual Streamlit UI check confirmed English guidance is visible when English is selected.
- Manual Streamlit UI check confirmed Chinese guidance is visible when Simplified Chinese is selected.
- Manual Streamlit UI check confirmed noisy/quiet audio guidance is visible.
- Manual Streamlit UI check confirmed audio upload filtering shows `MP3, WAV, M4A, AAC, FLAC`.
- Manual Streamlit UI check confirmed video upload filtering shows `MP4, MOV, MKV, AVI`.
- Manual Streamlit UI check confirmed existing image, PDF, Office, media, and OCR options still render.
- Formatter check confirmed TXT output includes file, conversion, model, language, notes, and timestamped segments.

## Existing Conversion Behavior

Image, PDF, OCR, Office, Video to Audio, TXT preview, ZIP, and download behavior should remain unchanged.
