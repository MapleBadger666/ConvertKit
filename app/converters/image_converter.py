from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.services.file_service import (
    OUTPUT_DIR,
    is_supported_image,
    unique_output_path,
)


TARGET_FORMATS = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}
HEIF_EXTENSIONS = {"heic", "heif"}
HEIF_SUPPORT_ERROR_MESSAGE = (
    "HEIC/HEIF support requires pillow-heif. Install dependencies with: "
    "python -m pip install -r requirements.txt"
)
_HEIF_OPENER_REGISTERED = False


def is_heif_image_path(image_path: str | Path) -> bool:
    return Path(image_path).suffix.lower().lstrip(".") in HEIF_EXTENSIONS


def ensure_heif_support(image_path: str | Path) -> None:
    global _HEIF_OPENER_REGISTERED
    if not is_heif_image_path(image_path):
        return

    if _HEIF_OPENER_REGISTERED:
        return

    try:
        from pillow_heif import register_heif_opener
    except ImportError as exc:
        raise RuntimeError(HEIF_SUPPORT_ERROR_MESSAGE) from exc

    register_heif_opener()
    _HEIF_OPENER_REGISTERED = True


def normalize_image_target_format(target_format: str) -> str:
    normalized = target_format.lower().lstrip(".")
    if normalized == "jpeg":
        normalized = "jpg"

    if normalized not in {"jpg", "png", "webp"}:
        raise ValueError(f"Unsupported image target format: {target_format}")

    return normalized


def prepare_image_for_format(image: Image.Image, target_format: str) -> Image.Image:
    normalized = normalize_image_target_format(target_format)

    if normalized == "jpg":
        if image.mode in {"RGBA", "LA"} or (
            image.mode == "P" and "transparency" in image.info
        ):
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.getchannel("A"))
            return background

        return image.convert("RGB")

    if normalized in {"png", "webp"} and image.mode not in {"RGB", "RGBA"}:
        return image.convert("RGBA" if "A" in image.getbands() else "RGB")

    return image


def convert_image(
    image_path: str | Path,
    target_format: str,
    output_dir: str | Path = OUTPUT_DIR,
) -> Path:
    source = Path(image_path)
    if not is_supported_image(source):
        raise ValueError(f"Unsupported image format: {source.name}")

    normalized = normalize_image_target_format(target_format)
    output_path = unique_output_path(source, normalized, output_dir)
    pil_format = TARGET_FORMATS[normalized]
    ensure_heif_support(source)

    with Image.open(source) as image:
        prepared = prepare_image_for_format(image, normalized)
        save_kwargs = {"quality": 95} if normalized in {"jpg", "webp"} else {}
        prepared.save(output_path, format=pil_format, **save_kwargs)

    return output_path


def convert_images(
    image_paths: list[str | Path],
    target_format: str,
    output_dir: str | Path = OUTPUT_DIR,
) -> list[Path]:
    return [convert_image(path, target_format, output_dir) for path in image_paths]
