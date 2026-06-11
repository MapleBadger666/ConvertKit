from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.converters.image_converter import convert_images
from app.converters.pdf_converter import images_to_pdf, pdf_to_docx, pdf_to_png, pdf_to_txt
from app.services.file_service import (
    OUTPUT_DIR,
    ensure_directory,
    is_supported_image,
    is_supported_pdf,
    save_uploaded_files,
)


CONVERSION_OPTIONS = {
    "Images to JPG": "image:jpg",
    "Images to PNG": "image:png",
    "Images to WEBP": "image:webp",
    "Images to one PDF": "images:pdf",
    "PDF pages to PNG": "pdf:png",
    "PDF to TXT": "pdf:txt",
    "PDF to DOCX": "pdf:docx",
}


def validate_files(file_paths: list[Path], conversion_type: str) -> list[str]:
    errors = []

    if conversion_type.startswith("image:") or conversion_type == "images:pdf":
        for path in file_paths:
            if not is_supported_image(path):
                errors.append(f"{path.name}: unsupported image format.")

    if conversion_type.startswith("pdf:"):
        for path in file_paths:
            if not is_supported_pdf(path):
                errors.append(f"{path.name}: expected a PDF file.")

        if len(file_paths) > 1:
            errors.append("PDF conversions currently process one PDF at a time.")

    return errors


def run_conversion(file_paths: list[Path], conversion_type: str) -> list[Path]:
    ensure_directory(OUTPUT_DIR)

    if conversion_type.startswith("image:"):
        target_format = conversion_type.split(":", maxsplit=1)[1]
        return convert_images(file_paths, target_format, OUTPUT_DIR)

    if conversion_type == "images:pdf":
        return [images_to_pdf(file_paths, OUTPUT_DIR)]

    pdf_path = file_paths[0]

    if conversion_type == "pdf:png":
        return pdf_to_png(pdf_path, OUTPUT_DIR)

    if conversion_type == "pdf:txt":
        return [pdf_to_txt(pdf_path, OUTPUT_DIR)]

    if conversion_type == "pdf:docx":
        return [pdf_to_docx(pdf_path, OUTPUT_DIR)]

    raise ValueError(f"Unsupported conversion type: {conversion_type}")


def main() -> None:
    st.set_page_config(page_title="FileMorph", page_icon="FM", layout="centered")
    st.title("FileMorph")
    st.caption("Local file conversion MVP. Files stay on this machine.")

    selected_label = st.selectbox("Conversion type", list(CONVERSION_OPTIONS))
    conversion_type = CONVERSION_OPTIONS[selected_label]
    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "webp", "pdf"],
    )

    if st.button("Convert", type="primary"):
        if not uploaded_files:
            st.error("Upload at least one file first.")
            return

        try:
            saved_files = save_uploaded_files(uploaded_files)
            validation_errors = validate_files(saved_files, conversion_type)

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                return

            output_paths = run_conversion(saved_files, conversion_type)
        except Exception as exc:
            st.error(f"Conversion failed: {exc}")
            return

        st.success("Conversion complete.")
        st.write("Generated files:")
        for output_path in output_paths:
            st.code(str(output_path))


if __name__ == "__main__":
    main()
