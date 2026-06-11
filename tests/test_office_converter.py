from pathlib import Path
from types import SimpleNamespace

from app.converters import office_converter
from app.converters.office_converter import (
    LIBREOFFICE_ERROR_MESSAGE,
    clean_text_lines,
    ensure_soffice_available,
    pptx_to_pdf,
    slide_text_sections,
)


class FakeTextFrame:
    def __init__(self, text: str):
        self.text = text


class FakeShape:
    has_text_frame = True

    def __init__(self, text: str):
        self.text_frame = FakeTextFrame(text)


class FakeShapes(list):
    def __init__(self, title, *shapes):
        super().__init__((title, *shapes))
        self.title = title


class FakeNotesSlide:
    def __init__(self, text: str):
        self.notes_text_frame = FakeTextFrame(text)


class FakeSlide:
    def __init__(self, shapes, notes: str = ""):
        self.shapes = shapes
        self.notes_slide = FakeNotesSlide(notes)


def test_ensure_soffice_available_raises_readable_error_when_missing(
    monkeypatch,
    tmp_path: Path,
):
    monkeypatch.setattr(office_converter, "which", lambda command: None)
    monkeypatch.setattr(office_converter, "MACOS_SOFFICE_PATH", tmp_path / "missing")

    try:
        ensure_soffice_available()
    except RuntimeError as exc:
        assert str(exc) == LIBREOFFICE_ERROR_MESSAGE
    else:
        raise AssertionError("Expected missing LibreOffice to raise RuntimeError")


def test_clean_text_lines_removes_empty_lines_and_whitespace():
    assert clean_text_lines("  Title  \n\n body \n\t") == ["Title", "body"]


def test_slide_text_sections_extracts_title_content_and_notes():
    title = FakeShape("Quarterly Plan")
    body = FakeShape("First point\nSecond point")
    slide = FakeSlide(FakeShapes(title, body), notes="Presenter reminder")

    slide_title, content, notes = slide_text_sections(slide)

    assert slide_title == "Quarterly Plan"
    assert content == ["First point", "Second point"]
    assert notes == ["Presenter reminder"]


def test_pptx_to_pdf_uses_soffice_output_without_requiring_real_libreoffice(
    monkeypatch,
    tmp_path: Path,
):
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake pptx")
    output_dir = tmp_path / "output"

    def fake_run(command, check, capture_output, text):
        assert "--headless" in command
        assert "--convert-to" in command
        assert "pdf" in command
        temporary_output_dir = Path(command[5])
        (temporary_output_dir / "deck.pdf").write_bytes(b"fake pdf")
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(office_converter, "ensure_soffice_available", lambda: "soffice")
    monkeypatch.setattr(office_converter.subprocess, "run", fake_run)

    output_path = pptx_to_pdf(source, output_dir)

    assert output_path == output_dir / "deck.pdf"
    assert output_path.read_bytes() == b"fake pdf"
