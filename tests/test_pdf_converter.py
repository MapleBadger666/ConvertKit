from pathlib import Path
import builtins

from PIL import Image

from app.converters.pdf_converter import (
    OPTIONAL_PDF_DOCX_DEPENDENCY_ERROR_MESSAGE,
    image_to_pdf,
    images_to_pdf,
    pdf_to_docx,
)


def test_images_to_pdf_combines_mixed_size_pngs_with_alpha(tmp_path: Path):
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    third = tmp_path / "third.png"
    Image.new("RGB", (8, 8), (255, 0, 0)).save(first)
    Image.new("RGBA", (12, 6), (0, 0, 255, 128)).save(second)
    Image.new("P", (4, 10)).save(third)

    output_path = images_to_pdf([first, second, third], tmp_path)

    assert output_path.exists()
    assert output_path.suffix == ".pdf"
    assert output_path.read_bytes().startswith(b"%PDF")


def test_image_to_pdf_uses_source_stem(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    Image.new("RGB", (8, 8), (20, 40, 60)).save(source)

    output_path = image_to_pdf(source, tmp_path)

    assert output_path == tmp_path / "photo.pdf"
    assert output_path.exists()


def test_pdf_to_docx_missing_optional_dependency_has_clear_error(
    monkeypatch,
    tmp_path: Path,
):
    source = tmp_path / "sample.pdf"
    source.write_bytes(b"%PDF-1.4\n")
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pdf2docx":
            raise ImportError("missing pdf2docx")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        pdf_to_docx(source, tmp_path)
    except RuntimeError as exc:
        assert str(exc) == OPTIONAL_PDF_DOCX_DEPENDENCY_ERROR_MESSAGE
    else:
        raise AssertionError("Expected missing pdf2docx to raise RuntimeError")
