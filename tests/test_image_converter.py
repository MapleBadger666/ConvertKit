from pathlib import Path

from PIL import Image

from app.converters.image_converter import convert_image, convert_images


def test_convert_png_to_webp(tmp_path: Path):
    source = tmp_path / "sample.png"
    Image.new("RGB", (8, 8), (20, 40, 60)).save(source)

    output_path = convert_image(source, "webp", tmp_path)

    assert output_path.exists()
    assert output_path.suffix == ".webp"
    with Image.open(output_path) as converted:
        assert converted.format == "WEBP"


def test_convert_rgba_png_to_jpg_flattens_alpha(tmp_path: Path):
    source = tmp_path / "transparent.png"
    Image.new("RGBA", (8, 8), (255, 0, 0, 128)).save(source)

    output_path = convert_image(source, "jpg", tmp_path)

    assert output_path.exists()
    with Image.open(output_path) as converted:
        assert converted.format == "JPEG"
        assert converted.mode == "RGB"


def test_convert_images_handles_batch_uploads(tmp_path: Path):
    sources = []
    for index in range(2):
        source = tmp_path / f"sample-{index}.png"
        Image.new("RGB", (8, 8), (index * 40, 40, 60)).save(source)
        sources.append(source)

    output_paths = convert_images(sources, "png", tmp_path)

    assert len(output_paths) == 2
    assert all(path.exists() for path in output_paths)


def test_unsupported_image_format_raises_clear_error(tmp_path: Path):
    source = tmp_path / "notes.txt"
    source.write_text("hello", encoding="utf-8")

    try:
        convert_image(source, "png", tmp_path)
    except ValueError as exc:
        assert "Unsupported image format" in str(exc)
    else:
        raise AssertionError("Expected unsupported image format to raise ValueError")
