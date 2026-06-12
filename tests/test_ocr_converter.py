from pathlib import Path

from app.converters import ocr_converter
from app.converters.ocr_converter import (
    OCR_LANGUAGE_ERROR_PREFIX,
    OCR_MODE_DOCUMENT,
    OCR_MODE_SCREENSHOT,
    OCR_MODE_STANDARD,
    TESSERACT_ERROR_MESSAGE,
    ensure_tesseract_available,
    image_to_text,
    normalize_ocr_mode,
    ocr_output_path,
    parse_tesseract_languages,
    prepare_image_for_ocr_mode,
    preprocess_image_for_ocr,
    required_ocr_languages,
    validate_ocr_language_available,
)
from PIL import Image


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


def test_image_to_text_checks_heif_support_before_tesseract(
    tmp_path: Path,
    monkeypatch,
):
    source = tmp_path / "photo.heic"
    source.write_text("not a real heic", encoding="utf-8")
    monkeypatch.setattr(
        ocr_converter,
        "ensure_heif_support",
        lambda path: (_ for _ in ()).throw(RuntimeError("missing heif support")),
    )
    monkeypatch.setattr(
        ocr_converter,
        "ensure_tesseract_available",
        lambda: (_ for _ in ()).throw(AssertionError("should not check tesseract")),
    )

    try:
        image_to_text(source)
    except RuntimeError as exc:
        assert str(exc) == "missing heif support"
    else:
        raise AssertionError("Expected missing HEIF support to raise RuntimeError")


def test_parse_tesseract_languages_skips_header_lines():
    output = """
List of available languages in "/opt/homebrew/share/tessdata/" (3):
eng
chi_sim
chi_tra
"""

    assert parse_tesseract_languages(output) == {"eng", "chi_sim", "chi_tra"}


def test_required_ocr_languages_splits_combined_language():
    assert required_ocr_languages("eng+chi_sim") == {"eng", "chi_sim"}


def test_validate_ocr_language_available_accepts_installed_languages():
    validate_ocr_language_available("eng+chi_sim", {"eng", "chi_sim"})


def test_validate_ocr_language_available_raises_readable_error_for_missing_language():
    try:
        validate_ocr_language_available("eng+chi_sim", {"eng"})
    except RuntimeError as exc:
        assert OCR_LANGUAGE_ERROR_PREFIX in str(exc)
        assert "chi_sim" in str(exc)
        assert "tesseract --list-langs" in str(exc)
    else:
        raise AssertionError("Expected missing OCR language to raise RuntimeError")


def test_preprocess_image_for_ocr_returns_processed_image():
    image = Image.new("RGB", (8, 10), (120, 120, 120))

    processed = preprocess_image_for_ocr(
        image,
        scale_factor=2,
        contrast_factor=1.5,
        threshold=128,
    )

    assert isinstance(processed, Image.Image)
    assert processed.mode == "L"
    assert processed.size == (16, 20)


def test_prepare_image_for_ocr_mode_keeps_standard_copy():
    image = Image.new("RGB", (8, 10), (120, 120, 120))

    processed = prepare_image_for_ocr_mode(image, OCR_MODE_STANDARD)

    assert isinstance(processed, Image.Image)
    assert processed.mode == "RGB"
    assert processed.size == image.size
    assert processed is not image


def test_prepare_image_for_ocr_mode_enhances_screenshot_and_document_modes():
    image = Image.new("RGB", (8, 10), (120, 120, 120))

    screenshot = prepare_image_for_ocr_mode(image, OCR_MODE_SCREENSHOT)
    document = prepare_image_for_ocr_mode(image, OCR_MODE_DOCUMENT)

    assert screenshot.mode == "L"
    assert screenshot.size == (24, 30)
    assert document.mode == "L"
    assert document.size == (16, 20)


def test_normalize_ocr_mode_rejects_unknown_mode():
    try:
        normalize_ocr_mode("magic")
    except ValueError as exc:
        assert "Unsupported OCR mode" in str(exc)
    else:
        raise AssertionError("Expected unknown OCR mode to raise ValueError")
