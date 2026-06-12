from pathlib import Path

from app.main import (
    EMPTY_TXT_PREVIEW_MESSAGE,
    OCR_MODE_OPTIONS,
    PPTX_DOCX_MODE_OPTIONS,
    TRANSCRIPTION_LANGUAGE_OPTIONS,
    TRANSCRIPTION_MODEL_OPTIONS,
    download_label_for_file,
    default_ocr_mode_index,
    get_allowed_upload_types,
    get_transcription_language_code,
    get_available_ocr_language_options,
    is_low_quality_ocr_text,
    mime_type_for_file,
    should_show_ocr_quality_warning,
    txt_preview_for_file,
)


def test_mime_type_for_known_output_files():
    assert mime_type_for_file(Path("result.txt")) == "text/plain"
    assert mime_type_for_file(Path("result.png")) == "image/png"
    assert mime_type_for_file(Path("result.jpg")) == "image/jpeg"
    assert mime_type_for_file(Path("result.jpeg")) == "image/jpeg"
    assert mime_type_for_file(Path("result.pdf")) == "application/pdf"
    assert (
        mime_type_for_file(Path("result.docx"))
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert mime_type_for_file(Path("result.wav")) == "audio/wav"
    assert mime_type_for_file(Path("result.mp3")) == "audio/mpeg"
    assert mime_type_for_file(Path("result.zip")) == "application/zip"


def test_mime_type_for_unknown_file_falls_back_to_binary():
    assert mime_type_for_file(Path("result.bin")) == "application/octet-stream"


def test_download_label_for_file_uses_uppercase_extension():
    assert download_label_for_file(Path("result.txt")) == "Download TXT"
    assert download_label_for_file(Path("result.png")) == "Download PNG"
    assert download_label_for_file(Path("result.docx")) == "Download DOCX"
    assert download_label_for_file(Path("result")) == "Download FILE"


def test_txt_preview_is_limited_to_first_1000_characters(tmp_path: Path):
    output_path = tmp_path / "result.txt"
    output_path.write_text("a" * 1005, encoding="utf-8")

    preview = txt_preview_for_file(output_path)

    assert preview == "a" * 1000


def test_txt_preview_shows_empty_message_for_whitespace_only_file(tmp_path: Path):
    output_path = tmp_path / "empty.txt"
    output_path.write_text(" \n\t", encoding="utf-8")

    preview = txt_preview_for_file(output_path)

    assert preview == EMPTY_TXT_PREVIEW_MESSAGE


def test_get_allowed_upload_types_for_image_conversions():
    assert get_allowed_upload_types("image:jpg") == ["jpg", "jpeg", "png", "webp"]
    assert get_allowed_upload_types("image:png") == ["jpg", "jpeg", "png", "webp"]
    assert get_allowed_upload_types("images:pdf") == ["jpg", "jpeg", "png", "webp"]
    assert get_allowed_upload_types("ocr:image_txt") == ["jpg", "jpeg", "png", "webp"]


def test_get_allowed_upload_types_for_pdf_conversions():
    assert get_allowed_upload_types("pdf:txt") == ["pdf"]
    assert get_allowed_upload_types("pdf:png") == ["pdf"]
    assert get_allowed_upload_types("pdf:docx") == ["pdf"]
    assert get_allowed_upload_types("ocr:pdf_txt") == ["pdf"]


def test_get_allowed_upload_types_for_pptx_conversions():
    assert get_allowed_upload_types("office:pptx_pdf") == ["pptx"]
    assert get_allowed_upload_types("office:pptx_docx") == ["pptx"]


def test_get_allowed_upload_types_for_video_to_audio():
    assert get_allowed_upload_types("media:audio") == ["mp4", "mov", "mkv", "avi"]


def test_get_allowed_upload_types_for_transcription_conversions():
    assert get_allowed_upload_types("transcription:audio_txt") == [
        "mp3",
        "wav",
        "m4a",
        "aac",
        "flac",
    ]
    assert get_allowed_upload_types("transcription:video_txt") == [
        "mp4",
        "mov",
        "mkv",
        "avi",
    ]


def test_get_allowed_upload_types_falls_back_to_all_supported_types():
    assert get_allowed_upload_types("unknown") == [
        "jpg",
        "jpeg",
        "png",
        "webp",
        "pdf",
        "pptx",
        "mp4",
        "mov",
        "mkv",
        "avi",
        "mp3",
        "wav",
        "m4a",
        "aac",
        "flac",
    ]


def test_get_available_ocr_language_options_filters_missing_languages():
    available = get_available_ocr_language_options({"eng", "chi_sim"})

    assert available == {
        "English": "eng",
        "Simplified Chinese": "chi_sim",
        "English + Simplified Chinese": "eng+chi_sim",
    }


def test_default_ocr_mode_prefers_screenshot_for_image_ocr():
    labels = list(OCR_MODE_OPTIONS)

    assert labels[default_ocr_mode_index("ocr:image_txt")] == (
        "Enhanced OCR for screenshots"
    )


def test_default_ocr_mode_prefers_document_for_pdf_ocr():
    labels = list(OCR_MODE_OPTIONS)

    assert labels[default_ocr_mode_index("ocr:pdf_txt")] == (
        "Enhanced OCR for scanned documents"
    )


def test_pptx_docx_mode_options_default_to_text_outline():
    assert list(PPTX_DOCX_MODE_OPTIONS) == [
        "Text Outline",
        "Slide Images",
        "Slide Images + Extracted Text",
    ]
    assert PPTX_DOCX_MODE_OPTIONS["Text Outline"] == "text_outline"


def test_transcription_options_default_to_base_and_map_languages():
    assert TRANSCRIPTION_MODEL_OPTIONS == ["tiny", "base", "small"]
    assert TRANSCRIPTION_MODEL_OPTIONS.index("base") == 1
    assert TRANSCRIPTION_LANGUAGE_OPTIONS == {
        "Auto-detect": None,
        "English": "en",
        "Simplified Chinese": "zh",
    }
    assert get_transcription_language_code("Auto-detect") is None
    assert get_transcription_language_code("English") == "en"
    assert get_transcription_language_code("Simplified Chinese") == "zh"


def test_is_low_quality_ocr_text_detects_short_or_whitespace_text():
    assert is_low_quality_ocr_text("   \n")
    assert is_low_quality_ocr_text("short")
    assert not is_low_quality_ocr_text("This OCR result has enough readable text.")


def test_should_show_ocr_quality_warning_only_for_low_quality_txt(tmp_path: Path):
    low_quality = tmp_path / "low.txt"
    high_quality = tmp_path / "high.txt"
    image_output = tmp_path / "image.png"
    low_quality.write_text("  ", encoding="utf-8")
    high_quality.write_text("This OCR result has enough readable text.", encoding="utf-8")
    image_output.write_text("not a txt output", encoding="utf-8")

    assert should_show_ocr_quality_warning(low_quality)
    assert not should_show_ocr_quality_warning(high_quality)
    assert not should_show_ocr_quality_warning(image_output)
