from app.services.file_service import get_extension, is_supported_image, is_supported_pdf


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
