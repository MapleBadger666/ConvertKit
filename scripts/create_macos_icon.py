from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError as exc:  # pragma: no cover - developer environment guard
    raise SystemExit(
        "Pillow is required to create the macOS icon. "
        "Run: python -m pip install -r requirements.txt"
    ) from exc


def rounded_rectangle(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill: tuple[int, ...]) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def create_base_icon(size: int = 1024) -> Image.Image:
    scale = size / 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    rounded_rectangle(
        shadow_draw,
        tuple(int(v * scale) for v in (92, 92, 932, 932)),
        int(196 * scale),
        (0, 0, 0, 88),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(28 * scale)))
    img.alpha_composite(shadow)

    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)
    rounded_rectangle(
        bg_draw,
        tuple(int(v * scale) for v in (96, 80, 928, 912)),
        int(188 * scale),
        (22, 92, 122, 255),
    )
    rounded_rectangle(
        bg_draw,
        tuple(int(v * scale) for v in (96, 80, 928, 480)),
        int(188 * scale),
        (40, 149, 151, 255),
    )
    img.alpha_composite(bg)

    draw = ImageDraw.Draw(img)

    # Back file
    draw.rounded_rectangle(
        tuple(int(v * scale) for v in (292, 186, 650, 682)),
        radius=int(44 * scale),
        fill=(230, 247, 247, 255),
    )
    draw.polygon(
        [
            (int(562 * scale), int(186 * scale)),
            (int(650 * scale), int(274 * scale)),
            (int(562 * scale), int(274 * scale)),
        ],
        fill=(180, 223, 224, 255),
    )

    # Front file
    draw.rounded_rectangle(
        tuple(int(v * scale) for v in (374, 292, 732, 788)),
        radius=int(44 * scale),
        fill=(255, 255, 248, 255),
    )
    draw.polygon(
        [
            (int(644 * scale), int(292 * scale)),
            (int(732 * scale), int(380 * scale)),
            (int(644 * scale), int(380 * scale)),
        ],
        fill=(230, 225, 204, 255),
    )

    # Conversion arrows
    arrow = (241, 121, 73, 255)
    draw.line(
        [
            (int(304 * scale), int(456 * scale)),
            (int(574 * scale), int(456 * scale)),
        ],
        fill=arrow,
        width=int(58 * scale),
    )
    draw.polygon(
        [
            (int(574 * scale), int(356 * scale)),
            (int(724 * scale), int(456 * scale)),
            (int(574 * scale), int(556 * scale)),
        ],
        fill=arrow,
    )

    draw.line(
        [
            (int(720 * scale), int(620 * scale)),
            (int(450 * scale), int(620 * scale)),
        ],
        fill=(31, 118, 166, 255),
        width=int(48 * scale),
    )
    draw.polygon(
        [
            (int(450 * scale), int(536 * scale)),
            (int(320 * scale), int(620 * scale)),
            (int(450 * scale), int(704 * scale)),
        ],
        fill=(31, 118, 166, 255),
    )

    # Small local dot, hinting the app runs on this machine.
    draw.ellipse(
        tuple(int(v * scale) for v in (690, 702, 764, 776)),
        fill=(123, 187, 97, 255),
    )

    return img


def save_png_sizes(base: Image.Image, iconset: Path) -> None:
    for size in [16, 32, 128, 256, 512]:
        resized = base.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(iconset / f"icon_{size}x{size}.png")

    for size in [16, 32, 128, 256, 512]:
        resized = base.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
        resized.save(iconset / f"icon_{size}x{size}@2x.png")


def build_icns(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    base = create_base_icon()
    png_output = output_path.with_suffix(".png")
    base.save(png_output)

    with tempfile.TemporaryDirectory(prefix="filemorph-icon-") as tmpdir:
        iconset = Path(tmpdir) / "FileMorph.iconset"
        iconset.mkdir()
        save_png_sizes(base, iconset)
        try:
            subprocess.run(
                ["iconutil", "--convert", "icns", "--output", str(output_path), str(iconset)],
                check=True,
            )
        except subprocess.CalledProcessError:
            tiff_path = Path(tmpdir) / "FileMorph.tiff"
            subprocess.run(
                ["sips", "-s", "format", "tiff", str(png_output), "--out", str(tiff_path)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(["tiff2icns", str(tiff_path), str(output_path)], check=True)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: create_macos_icon.py /path/to/FileMorph.icns")

    build_icns(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
