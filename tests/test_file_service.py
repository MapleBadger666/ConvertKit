from pathlib import Path
from zipfile import ZipFile

from app.services.file_service import (
    create_zip_archive,
    get_extension,
    is_supported_image,
    is_supported_pdf,
    is_supported_pptx,
    is_supported_video,
    unique_output_path,
)


def test_get_extension_is_case_insensitive():
    assert get_extension("Example.JPEG") == "jpeg"


def test_supported_image_extensions():
    assert is_supported_image("photo.jpg")
    assert is_supported_image("photo.jpeg")
    assert is_supported_image("photo.png")
    assert is_supported_image("photo.webp")
    assert not is_supported_image("photo.gif")


def test_supported_pdf_extension():
    assert is_supported_pdf("document.pdf")
    assert not is_supported_pdf("document.txt")


def test_supported_pptx_extension():
    assert is_supported_pptx("slides.pptx")
    assert is_supported_pptx("SLIDES.PPTX")
    assert not is_supported_pptx("slides.ppt")


def test_supported_video_extensions():
    assert is_supported_video("clip.mp4")
    assert is_supported_video("clip.mov")
    assert is_supported_video("clip.mkv")
    assert is_supported_video("clip.avi")
    assert not is_supported_video("clip.wav")


def test_unique_output_path_returns_original_name_when_available(tmp_path: Path):
    output_path = unique_output_path("file.jpg", "png", tmp_path)

    assert output_path == tmp_path / "file.png"


def test_unique_output_path_adds_incrementing_suffix(tmp_path: Path):
    (tmp_path / "file.png").write_text("existing", encoding="utf-8")
    (tmp_path / "file_1.png").write_text("existing", encoding="utf-8")

    output_path = unique_output_path("file.jpg", "png", tmp_path)

    assert output_path == tmp_path / "file_2.png"


def test_unique_output_path_normalizes_target_extension(tmp_path: Path):
    (tmp_path / "file.webp").write_text("existing", encoding="utf-8")

    output_path = unique_output_path("file.png", ".WEBP", tmp_path)

    assert output_path == tmp_path / "file_1.webp"


def test_create_zip_archive_packages_files(tmp_path: Path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("one", encoding="utf-8")
    second.write_text("two", encoding="utf-8")

    zip_path = create_zip_archive([first, second], tmp_path)

    assert zip_path == tmp_path / "converted-files.zip"
    with ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == ["first.txt", "second.txt"]
