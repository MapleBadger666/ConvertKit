from pathlib import Path

from app.converters import ocr_converter
from app.converters.ocr_converter import (
    TESSERACT_ERROR_MESSAGE,
    ensure_tesseract_available,
    image_to_text,
    ocr_output_path,
)


def test_ensure_tesseract_available_raises_clear_error_when_missing(monkeypatch):
    monkeypatch.setattr(ocr_converter, "which", lambda command: None)

    try:
        ensure_tesseract_available()
    except RuntimeError as exc:
        assert str(exc) == TESSERACT_ERROR_MESSAGE
    else:
        raise AssertionError("Expected missing Tesseract to raise RuntimeError")


def test_ensure_tesseract_available_passes_when_binary_exists(monkeypatch):
    monkeypatch.setattr(ocr_converter, "which", lambda command: "/usr/bin/tesseract")

    ensure_tesseract_available()


def test_ocr_output_path_uses_txt_extension_and_deduplicates(tmp_path: Path):
    (tmp_path / "scan.txt").write_text("existing", encoding="utf-8")

    output_path = ocr_output_path(tmp_path / "scan.pdf", tmp_path)

    assert output_path == tmp_path / "scan_1.txt"


def test_image_to_text_rejects_unsupported_extension_before_tesseract_check(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setattr(
        ocr_converter,
        "ensure_tesseract_available",
        lambda: (_ for _ in ()).throw(AssertionError("should not check tesseract")),
    )
    source = tmp_path / "notes.txt"
    source.write_text("hello", encoding="utf-8")

    try:
        image_to_text(source)
    except ValueError as exc:
        assert "Unsupported image format for OCR" in str(exc)
    else:
        raise AssertionError("Expected unsupported image format to raise ValueError")
