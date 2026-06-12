from pathlib import Path
from types import SimpleNamespace

from app.converters import office_converter
from app.converters.office_converter import (
    LIBREOFFICE_ERROR_MESSAGE,
    POPPLER_ERROR_MESSAGE,
    PPTX_DOCX_MODE_SLIDE_IMAGES,
    PPTX_DOCX_MODE_SLIDE_IMAGES_WITH_TEXT,
    PPTX_DOCX_MODE_TEXT_OUTLINE,
    PPTX_SLIDE_IMAGE_EXPORT_ERROR_MESSAGE,
    clean_text_lines,
    ensure_soffice_available,
    export_pptx_slide_images,
    normalize_pptx_docx_mode,
    pptx_to_pdf,
    pptx_to_docx,
    pptx_to_docx_text_outline,
    pptx_to_docx_with_slide_images,
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


class FakeSection:
    page_width = 1000
    left_margin = 100
    right_margin = 100


class FakeDocument:
    def __init__(self):
        self.sections = [FakeSection()]
        self.events = []

    def add_heading(self, text: str, level: int):
        self.events.append(("heading", level, text))

    def add_page_break(self):
        self.events.append(("page_break",))

    def add_paragraph(self, text: str, style: str | None = None):
        self.events.append(("paragraph", text, style))

    def add_picture(self, path: str, width):
        self.events.append(("picture", Path(path).name, width))

    def save(self, path: str | Path):
        self.events.append(("save", Path(path).name))
        Path(path).write_bytes(b"fake docx")


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


def test_normalize_pptx_docx_mode_accepts_supported_modes():
    assert normalize_pptx_docx_mode("Text Outline") == PPTX_DOCX_MODE_TEXT_OUTLINE
    assert normalize_pptx_docx_mode("slide-images") == PPTX_DOCX_MODE_SLIDE_IMAGES
    assert (
        normalize_pptx_docx_mode("Slide Images + Extracted Text")
        == PPTX_DOCX_MODE_SLIDE_IMAGES_WITH_TEXT
    )


def test_normalize_pptx_docx_mode_rejects_unknown_mode():
    try:
        normalize_pptx_docx_mode("editable visuals")
    except ValueError as exc:
        assert "Unsupported PPTX to DOCX mode" in str(exc)
    else:
        raise AssertionError("Expected unsupported PPTX DOCX mode to raise ValueError")


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


def test_pptx_to_pdf_wraps_broken_soffice_wrapper_as_dependency_error(
    monkeypatch,
    tmp_path: Path,
):
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake pptx")

    def fake_run(command, check, capture_output, text):
        raise office_converter.subprocess.CalledProcessError(
            127,
            command,
            stderr="/Applications/LibreOffice.app/Contents/MacOS/soffice: No such file or directory",
        )

    monkeypatch.setattr(office_converter, "ensure_soffice_available", lambda: "soffice")
    monkeypatch.setattr(office_converter.subprocess, "run", fake_run)

    try:
        pptx_to_pdf(source, tmp_path / "output")
    except RuntimeError as exc:
        assert str(exc) == LIBREOFFICE_ERROR_MESSAGE
    else:
        raise AssertionError("Expected broken soffice wrapper to raise dependency error")


def test_export_pptx_slide_images_uses_pdf_pages_without_real_libreoffice(
    monkeypatch,
    tmp_path: Path,
):
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake pptx")
    output_dir = tmp_path / "output"

    def fake_pptx_to_pdf(input_path, temporary_output_dir):
        pdf_path = Path(temporary_output_dir) / "deck.pdf"
        pdf_path.write_bytes(b"fake pdf")
        return pdf_path

    def fake_pdf_to_png(pdf_path, temporary_output_dir, dpi):
        first = Path(temporary_output_dir) / "deck-page-1.png"
        second = Path(temporary_output_dir) / "deck-page-2.png"
        first.write_bytes(b"first")
        second.write_bytes(b"second")
        return [first, second]

    monkeypatch.setattr(office_converter, "pptx_to_pdf", fake_pptx_to_pdf)
    monkeypatch.setattr(office_converter, "pdf_to_png", fake_pdf_to_png)

    image_paths = export_pptx_slide_images(source, output_dir)

    assert image_paths == [
        output_dir / "deck-slide-1.png",
        output_dir / "deck-slide-2.png",
    ]
    assert image_paths[0].read_bytes() == b"first"
    assert image_paths[1].read_bytes() == b"second"


def test_export_pptx_slide_images_wraps_missing_poppler_error(
    monkeypatch,
    tmp_path: Path,
):
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake pptx")

    def fake_pptx_to_pdf(input_path, temporary_output_dir):
        pdf_path = Path(temporary_output_dir) / "deck.pdf"
        pdf_path.write_bytes(b"fake pdf")
        return pdf_path

    def fake_pdf_to_png(pdf_path, temporary_output_dir, dpi):
        raise RuntimeError(POPPLER_ERROR_MESSAGE)

    monkeypatch.setattr(office_converter, "pptx_to_pdf", fake_pptx_to_pdf)
    monkeypatch.setattr(office_converter, "pdf_to_png", fake_pdf_to_png)

    try:
        export_pptx_slide_images(source, tmp_path / "output")
    except RuntimeError as exc:
        assert str(exc) == PPTX_SLIDE_IMAGE_EXPORT_ERROR_MESSAGE
    else:
        raise AssertionError("Expected missing Poppler to raise a slide export error")


def test_pptx_to_docx_default_keeps_text_outline_mode(monkeypatch, tmp_path: Path):
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake pptx")
    expected = tmp_path / "outline.docx"

    def fake_text_outline(input_path, output_dir):
        assert input_path == source
        assert output_dir == tmp_path
        return expected

    monkeypatch.setattr(office_converter, "pptx_to_docx_text_outline", fake_text_outline)

    assert pptx_to_docx(source, tmp_path) == expected


def test_pptx_to_docx_dispatches_slide_image_modes(monkeypatch, tmp_path: Path):
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake pptx")
    calls = []

    def fake_slide_images(input_path, output_dir, include_extracted_text):
        calls.append((input_path, output_dir, include_extracted_text))
        return output_dir / "deck.docx"

    monkeypatch.setattr(
        office_converter,
        "pptx_to_docx_with_slide_images",
        fake_slide_images,
    )

    pptx_to_docx(source, tmp_path, PPTX_DOCX_MODE_SLIDE_IMAGES)
    pptx_to_docx(source, tmp_path, PPTX_DOCX_MODE_SLIDE_IMAGES_WITH_TEXT)

    assert calls == [
        (source, tmp_path, False),
        (source, tmp_path, True),
    ]


def test_pptx_to_docx_text_outline_keeps_existing_outline_structure(
    monkeypatch,
    tmp_path: Path,
):
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake pptx")
    document = FakeDocument()
    slide = FakeSlide(
        FakeShapes(FakeShape("Roadmap"), FakeShape("Alpha\nBeta")),
        notes="Talk track",
    )

    monkeypatch.setattr(office_converter, "load_presentation_slides", lambda path: [slide])
    monkeypatch.setattr(office_converter, "new_docx_document", lambda: document)

    output_path = pptx_to_docx_text_outline(source, tmp_path)

    assert output_path == tmp_path / "deck.docx"
    assert document.events == [
        ("heading", 1, "Slide 1"),
        ("paragraph", "Title: Roadmap", None),
        ("paragraph", "Content:", None),
        ("paragraph", "Alpha", "List Bullet"),
        ("paragraph", "Beta", "List Bullet"),
        ("paragraph", "Speaker Notes:", None),
        ("paragraph", "Talk track", "List Bullet"),
        ("save", "deck.docx"),
    ]


def test_pptx_to_docx_with_slide_images_can_include_extracted_text(
    monkeypatch,
    tmp_path: Path,
):
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake pptx")
    image = tmp_path / "slide.png"
    image.write_bytes(b"fake image")
    document = FakeDocument()
    slide = FakeSlide(FakeShapes(FakeShape("Launch"), FakeShape("Ready")))

    monkeypatch.setattr(
        office_converter,
        "export_pptx_slide_images",
        lambda input_path, output_dir: [image],
    )
    monkeypatch.setattr(office_converter, "load_presentation_slides", lambda path: [slide])
    monkeypatch.setattr(office_converter, "new_docx_document", lambda: document)

    output_path = pptx_to_docx_with_slide_images(
        source,
        tmp_path,
        include_extracted_text=True,
    )

    assert output_path == tmp_path / "deck.docx"
    assert document.events == [
        ("heading", 1, "Slide 1"),
        ("picture", "slide.png", 800),
        ("heading", 2, "Extracted Text"),
        ("paragraph", "Title: Launch", None),
        ("paragraph", "Content:", None),
        ("paragraph", "Ready", "List Bullet"),
        ("save", "deck.docx"),
    ]
