from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from app import main as app_main
from app.main import (
    CONVERSION_CATEGORIES,
    EMPTY_TXT_PREVIEW_MESSAGE,
    HISTORY_STATE_KEY,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    JOB_STATUS_SUCCESS,
    OCR_MODE_OPTIONS,
    PPTX_DOCX_MODE_OPTIONS,
    TRANSCRIPTION_LANGUAGE_OPTIONS,
    TRANSCRIPTION_MODEL_GUIDANCE,
    TRANSCRIPTION_MODEL_OPTIONS,
    TRANSCRIPTION_AUDIO_GUIDANCE,
    add_history_entry,
    app_intro_text,
    clear_conversion_history,
    conversion_help_text,
    create_history_entry,
    create_job_item,
    create_success_zip,
    dependency_status_label,
    download_label_for_file,
    default_ocr_mode_index,
    get_allowed_upload_types,
    get_category_conversion_options,
    get_transcription_language_code,
    get_available_ocr_language_options,
    get_conversion_history,
    is_low_quality_ocr_text,
    local_app_info_rows,
    job_summary,
    mark_job_failed,
    mark_job_running,
    mark_job_success,
    mime_type_for_file,
    output_table_rows,
    convert_file_paths,
    process_conversion_batch,
    process_images_to_pdf_batch,
    should_show_ocr_quality_warning,
    successful_output_paths,
    system_dependency_rows,
    transcription_language_guidance,
    transcription_post_conversion_messages,
    txt_preview_for_file,
    runtime_privacy_text,
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
    image_types = ["jpg", "jpeg", "png", "webp", "heic", "heif"]

    assert get_allowed_upload_types("image:jpg") == image_types
    assert get_allowed_upload_types("image:png") == image_types
    assert get_allowed_upload_types("images:pdf") == image_types
    assert get_allowed_upload_types("images:pdf_each") == image_types
    assert get_allowed_upload_types("ocr:image_txt") == image_types


def test_conversion_categories_cover_existing_options():
    labels = [
        label
        for category_labels in CONVERSION_CATEGORIES.values()
        for label in category_labels
    ]

    assert labels == [
        "Images to JPG",
        "Images to PNG",
        "Images to WEBP",
        "Images to one PDF",
        "Images to separate PDFs",
        "PDF pages to PNG",
        "PDF to TXT",
        "PDF to DOCX",
        "Image to TXT (OCR)",
        "Scanned PDF to TXT (OCR)",
        "PPTX to PDF",
        "PPTX to DOCX",
        "Video to Audio",
        "Audio to TXT",
        "Video to TXT",
    ]


def test_get_category_conversion_options_returns_only_category_items():
    assert get_category_conversion_options("Office") == {
        "PPTX to PDF": "office:pptx_pdf",
        "PPTX to DOCX": "office:pptx_docx",
    }
    assert get_category_conversion_options("Transcription") == {
        "Audio to TXT": "transcription:audio_txt",
        "Video to TXT": "transcription:video_txt",
    }


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


def test_job_item_status_helpers_track_outputs_and_errors():
    job_item = create_job_item("source.png", "image:png")

    assert job_item == {
        "input_filename": "source.png",
        "conversion_type": "image:png",
        "input_count": 1,
        "status": JOB_STATUS_PENDING,
        "output_paths": [],
        "error": "",
    }

    assert mark_job_running(job_item)["status"] == JOB_STATUS_RUNNING
    mark_job_success(job_item, [Path("output/source.png")])

    assert job_item["status"] == JOB_STATUS_SUCCESS
    assert job_item["output_paths"] == [Path("output/source.png")]
    assert job_item["error"] == ""

    failed_job = create_job_item("broken.png", "image:png")
    mark_job_failed(failed_job, "Cannot convert file.")

    assert failed_job["status"] == JOB_STATUS_FAILED
    assert failed_job["output_paths"] == []
    assert failed_job["error"] == "Cannot convert file."


def test_job_summary_counts_batch_statuses():
    successful_job = create_job_item("ok.png", "image:png")
    failed_job = create_job_item("bad.png", "image:png")
    pending_job = create_job_item("waiting.png", "image:png")
    mark_job_success(successful_job, [Path("output/ok.png")])
    mark_job_failed(failed_job, "Cannot convert file.")

    assert job_summary([successful_job, failed_job, pending_job]) == {
        "total": 3,
        "completed": 2,
        "successful": 1,
        "failed": 1,
    }


def test_successful_output_paths_returns_unique_success_outputs():
    shared_output = Path("output/slides.pdf")
    first_job = create_job_item("slide-1.png", "images:pdf")
    second_job = create_job_item("slide-2.png", "images:pdf")
    failed_job = create_job_item("bad.txt", "images:pdf")
    mark_job_success(first_job, [shared_output])
    mark_job_success(second_job, [shared_output])
    mark_job_failed(failed_job, "unsupported image format.")

    assert successful_output_paths([first_job, second_job, failed_job]) == [
        shared_output
    ]


def test_images_to_one_pdf_batch_dispatches_as_one_group(monkeypatch, tmp_path: Path):
    first_image = tmp_path / "first.png"
    second_image = tmp_path / "second.jpg"
    combined_pdf = tmp_path / "combined.pdf"
    calls = []

    def fake_convert_file_paths(file_paths, conversion_type, *args):
        calls.append((list(file_paths), conversion_type))
        return [combined_pdf], []

    monkeypatch.setattr(app_main, "convert_file_paths", fake_convert_file_paths)

    job_items = process_images_to_pdf_batch([first_image, second_image])

    assert calls == [([first_image, second_image], "images:pdf")]
    assert len(job_items) == 1
    assert job_items[0]["input_filename"] == "2 images"
    assert job_items[0]["output_paths"] == [combined_pdf]
    assert job_summary(job_items) == {
        "total": 2,
        "completed": 2,
        "successful": 1,
        "failed": 0,
    }


def test_images_to_one_pdf_group_failure_is_one_readable_error(
    monkeypatch,
    tmp_path: Path,
):
    first_image = tmp_path / "first.png"
    second_image = tmp_path / "second.jpg"

    def fake_convert_file_paths(file_paths, conversion_type, *args):
        return [], ["Images to one PDF failed: Cannot combine images."]

    monkeypatch.setattr(app_main, "convert_file_paths", fake_convert_file_paths)

    job_items = process_images_to_pdf_batch([first_image, second_image])

    assert len(job_items) == 1
    assert job_items[0]["status"] == JOB_STATUS_FAILED
    assert job_items[0]["error"] == "Images to one PDF failed: Cannot combine images."
    assert job_summary(job_items) == {
        "total": 2,
        "completed": 2,
        "successful": 0,
        "failed": 1,
    }


def test_images_to_separate_pdfs_processes_each_file_independently(
    monkeypatch,
    tmp_path: Path,
):
    first_image = tmp_path / "first.png"
    bad_image = tmp_path / "bad.png"
    next_image = tmp_path / "next.heic"
    calls = []

    def fake_convert_file_paths(file_paths, conversion_type, *args):
        file_path = file_paths[0]
        calls.append((file_path.name, conversion_type))
        if file_path.name == "bad.png":
            return [], ["bad.png: Cannot convert image."]
        return [tmp_path / f"{file_path.stem}.pdf"], []

    monkeypatch.setattr(app_main, "convert_file_paths", fake_convert_file_paths)

    job_items = process_conversion_batch(
        [first_image, bad_image, next_image],
        "images:pdf_each",
    )

    assert calls == [
        ("first.png", "images:pdf_each"),
        ("bad.png", "images:pdf_each"),
        ("next.heic", "images:pdf_each"),
    ]
    assert [item["status"] for item in job_items] == [
        JOB_STATUS_SUCCESS,
        JOB_STATUS_FAILED,
        JOB_STATUS_SUCCESS,
    ]
    assert successful_output_paths(job_items) == [
        tmp_path / "first.pdf",
        tmp_path / "next.pdf",
    ]
    assert job_summary(job_items) == {
        "total": 3,
        "completed": 3,
        "successful": 2,
        "failed": 1,
    }


def test_convert_file_paths_images_to_separate_pdfs_returns_successful_outputs(
    monkeypatch,
    tmp_path: Path,
):
    first_image = tmp_path / "first.png"
    bad_image = tmp_path / "bad.png"
    next_image = tmp_path / "next.heif"

    def fake_image_to_pdf(file_path, output_dir):
        source = Path(file_path)
        if source.name == "bad.png":
            raise RuntimeError("Cannot convert image.")
        return tmp_path / f"{source.stem}.pdf"

    monkeypatch.setattr(app_main, "image_to_pdf", fake_image_to_pdf)

    output_paths, failed_files = convert_file_paths(
        [first_image, bad_image, next_image],
        "images:pdf_each",
    )

    assert output_paths == [tmp_path / "first.pdf", tmp_path / "next.pdf"]
    assert failed_files == ["bad.png: Cannot convert image."]


def test_output_table_rows_lists_outputs_and_failures():
    successful_job = create_job_item("report.pdf", "pdf:png")
    failed_job = create_job_item("broken.pdf", "pdf:png")
    mark_job_success(
        successful_job,
        [Path("output/report_page_1.png"), Path("output/report_page_2.png")],
    )
    mark_job_failed(failed_job, "Cannot read PDF.")

    assert output_table_rows([successful_job, failed_job]) == [
        {
            "Source": "report.pdf",
            "Output": "report_page_1.png",
            "Status": JOB_STATUS_SUCCESS,
        },
        {
            "Source": "report.pdf",
            "Output": "report_page_2.png",
            "Status": JOB_STATUS_SUCCESS,
        },
        {
            "Source": "broken.pdf",
            "Output": "",
            "Status": JOB_STATUS_FAILED,
        },
    ]


def test_history_helpers_store_recent_session_entries():
    session_state = {}
    first_entry = create_history_entry(
        "Images to PNG",
        input_count=2,
        successful_count=2,
        failed_count=0,
        timestamp=datetime(2026, 6, 12, 10, 30, 0),
    )
    second_entry = create_history_entry(
        "PDF to TXT",
        input_count=1,
        successful_count=0,
        failed_count=1,
        timestamp=datetime(2026, 6, 12, 10, 31, 0),
    )

    assert get_conversion_history(session_state) == []
    assert first_entry == {
        "Timestamp": "2026-06-12 10:30:00",
        "Conversion": "Images to PNG",
        "Input files": 2,
        "Successful": 2,
        "Failed": 0,
    }

    add_history_entry(session_state, first_entry, limit=1)
    add_history_entry(session_state, second_entry, limit=1)

    assert session_state[HISTORY_STATE_KEY] == [second_entry]

    clear_conversion_history(session_state)

    assert session_state[HISTORY_STATE_KEY] == []


def test_create_success_zip_packages_successful_outputs(tmp_path: Path):
    first_output = tmp_path / "first.txt"
    second_output = tmp_path / "second.txt"
    first_output.write_text("first", encoding="utf-8")
    second_output.write_text("second", encoding="utf-8")

    zip_path = create_success_zip([first_output, second_output], tmp_path)

    assert zip_path.name == "filemorph_outputs.zip"
    with ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == ["first.txt", "second.txt"]
        assert archive.read("first.txt").decode("utf-8") == "first"
        assert archive.read("second.txt").decode("utf-8") == "second"


def test_process_conversion_batch_continues_after_failed_file(
    monkeypatch,
    tmp_path: Path,
):
    good_file = tmp_path / "good.pdf"
    bad_file = tmp_path / "bad.pdf"
    next_file = tmp_path / "next.pdf"
    good_file.write_text("good", encoding="utf-8")
    bad_file.write_text("bad", encoding="utf-8")
    next_file.write_text("next", encoding="utf-8")
    calls = []

    def fake_convert_file_paths(file_paths, *args):
        file_path = file_paths[0]
        calls.append(file_path.name)
        if file_path.name == "bad.pdf":
            raise RuntimeError("Cannot convert bad.pdf.")
        return [tmp_path / f"{file_path.stem}.txt"], []

    monkeypatch.setattr(app_main, "convert_file_paths", fake_convert_file_paths)

    job_items = process_conversion_batch(
        [good_file, bad_file, next_file],
        "pdf:txt",
    )

    assert calls == ["good.pdf", "bad.pdf", "next.pdf"]
    assert [item["status"] for item in job_items] == [
        JOB_STATUS_SUCCESS,
        JOB_STATUS_FAILED,
        JOB_STATUS_SUCCESS,
    ]
    assert job_items[1]["error"] == "Cannot convert bad.pdf."
    assert job_summary(job_items) == {
        "total": 3,
        "completed": 3,
        "successful": 2,
        "failed": 1,
    }


def test_dependency_status_label_uses_lightweight_command_lookup(monkeypatch):
    monkeypatch.setattr(app_main, "which", lambda command: f"/usr/bin/{command}")
    assert dependency_status_label(["ffmpeg"]) == "Detected"

    monkeypatch.setattr(app_main, "which", lambda command: None)
    assert dependency_status_label(["ffmpeg"]) == "Not detected"
    assert dependency_status_label([]) == "Python package"


def test_system_dependency_rows_include_install_guidance(monkeypatch):
    monkeypatch.setattr(app_main, "which", lambda command: f"/usr/bin/{command}")

    rows = system_dependency_rows()

    assert {
        "Dependency": "ffmpeg",
        "Required for": "Video to Audio, Video to TXT, audio preprocessing",
        "Install": "brew install ffmpeg",
        "Status": "Detected",
    } in rows
    assert any(row["Dependency"] == "faster-whisper" for row in rows)


def test_conversion_help_text_covers_major_groups():
    assert "enhanced modes" in conversion_help_text("ocr:image_txt")
    assert "single PDF" in conversion_help_text("images:pdf")
    assert "own PDF" in conversion_help_text("images:pdf_each")
    assert "Text Outline is editable" in conversion_help_text("office:pptx_docx")
    assert "small for better accuracy" in conversion_help_text("transcription:audio_txt")
    assert "MP3 is smaller" in conversion_help_text("media:audio")
    assert "processed locally" in conversion_help_text("image:png")


def test_default_runtime_copy_is_local_first():
    assert "local-first" in app_intro_text()
    assert "Local mode" in runtime_privacy_text()


def test_local_app_info_rows_include_version_and_runtime_paths():
    rows = local_app_info_rows()
    values_by_item = {row["Item"]: row["Value"] for row in rows}

    assert values_by_item["App version"]
    assert values_by_item["Build channel"]
    assert values_by_item["User data directory"]
    assert values_by_item["Output directory"].endswith("output")
    assert values_by_item["Logs directory"].endswith("logs")


def test_get_allowed_upload_types_falls_back_to_all_supported_types():
    assert get_allowed_upload_types("unknown") == [
        "jpg",
        "jpeg",
        "png",
        "webp",
        "heic",
        "heif",
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
    assert "base = balanced" in TRANSCRIPTION_MODEL_GUIDANCE
    assert "Background noise" in TRANSCRIPTION_AUDIO_GUIDANCE


def test_transcription_language_guidance_matches_language_choice():
    assert "English transcription" in transcription_language_guidance("English")
    assert "Chinese speech" in transcription_language_guidance("Simplified Chinese")
    assert "choose the spoken language manually" in transcription_language_guidance(
        "Auto-detect"
    )


def test_transcription_post_conversion_messages_match_quality_choices():
    assert transcription_post_conversion_messages("tiny", "Auto-detect") == [
        "For better accuracy, try base or small.",
        "If the transcript looks wrong, choose the spoken language manually.",
    ]
    assert transcription_post_conversion_messages("base", "Simplified Chinese") == [
        "Chinese transcription works best with clear Mandarin audio and small model."
    ]
    assert transcription_post_conversion_messages("small", "English") == [
        "English transcription improves with clear speech, low background noise, and base/small model."
    ]


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
