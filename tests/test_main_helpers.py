from pathlib import Path

from app.main import (
    EMPTY_TXT_PREVIEW_MESSAGE,
    download_label_for_file,
    mime_type_for_file,
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
