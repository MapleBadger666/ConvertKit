from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.converters.pdf_converter import images_to_pdf, pdf_to_docx, pdf_to_png, pdf_to_txt
from app.converters.ocr_converter import image_to_text, pdf_to_text_with_ocr
from app.services.file_service import (
    OUTPUT_DIR,
    create_zip_archive,
    ensure_directory,
    is_supported_image,
    is_supported_pdf,
    save_uploaded_files,
    unique_output_path,
)


CONVERSION_OPTIONS = {
    "Images to JPG": "image:jpg",
    "Images to PNG": "image:png",
    "Images to WEBP": "image:webp",
    "Images to one PDF": "images:pdf",
    "PDF pages to PNG": "pdf:png",
    "PDF to TXT": "pdf:txt",
    "PDF to DOCX": "pdf:docx",
    "Image to TXT (OCR)": "ocr:image_txt",
    "Scanned PDF to TXT (OCR)": "ocr:pdf_txt",
}

OCR_LANGUAGE_OPTIONS = {
    "English": "eng",
    "Simplified Chinese": "chi_sim",
    "Traditional Chinese": "chi_tra",
    "English + Simplified Chinese": "eng+chi_sim",
}

MIME_TYPES = {
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".zip": "application/zip",
}

EMPTY_TXT_PREVIEW_MESSAGE = (
    "The TXT file was generated, but no readable text was found."
)


def readable_error(exc: Exception) -> str:
    message = str(exc).strip()
    return message or exc.__class__.__name__


def convert_file_paths(
    file_paths: list[Path],
    conversion_type: str,
    ocr_language: str = "eng",
) -> tuple[list[Path], list[str]]:
    output_paths: list[Path] = []
    failed_files: list[str] = []
    ensure_directory(OUTPUT_DIR)

    if conversion_type.startswith("image:"):
        target_format = conversion_type.split(":", maxsplit=1)[1]
        for file_path in file_paths:
            if not is_supported_image(file_path):
                failed_files.append(f"{file_path.name}: unsupported image format.")
                continue

            try:
                from app.converters.image_converter import convert_image

                output_paths.append(convert_image(file_path, target_format, OUTPUT_DIR))
            except Exception as exc:
                failed_files.append(f"{file_path.name}: {readable_error(exc)}")

        return output_paths, failed_files

    if conversion_type == "images:pdf":
        image_paths = []
        for file_path in file_paths:
            if is_supported_image(file_path):
                image_paths.append(file_path)
            else:
                failed_files.append(f"{file_path.name}: unsupported image format.")

        if image_paths:
            try:
                output_paths.append(images_to_pdf(image_paths, OUTPUT_DIR))
            except Exception as exc:
                failed_files.append(f"Images to PDF: {readable_error(exc)}")
        else:
            failed_files.append("Images to PDF: upload at least one supported image.")

        return output_paths, failed_files

    if conversion_type == "ocr:image_txt":
        for file_path in file_paths:
            if not is_supported_image(file_path):
                failed_files.append(f"{file_path.name}: expected a supported image file.")
                continue

            try:
                text = image_to_text(file_path, ocr_language)
                output_path = unique_output_path(file_path, "txt", OUTPUT_DIR)
                output_path.write_text(text, encoding="utf-8")
                output_paths.append(output_path)
            except Exception as exc:
                failed_files.append(f"{file_path.name}: {readable_error(exc)}")

        return output_paths, failed_files

    if conversion_type == "ocr:pdf_txt":
        for file_path in file_paths:
            if not is_supported_pdf(file_path):
                failed_files.append(f"{file_path.name}: expected a PDF file.")
                continue

            try:
                output_paths.append(
                    pdf_to_text_with_ocr(file_path, OUTPUT_DIR, ocr_language)
                )
            except Exception as exc:
                failed_files.append(f"{file_path.name}: {readable_error(exc)}")

        return output_paths, failed_files

    if conversion_type.startswith("pdf:"):
        for file_path in file_paths:
            if not is_supported_pdf(file_path):
                failed_files.append(f"{file_path.name}: expected a PDF file.")
                continue

            try:
                if conversion_type == "pdf:png":
                    output_paths.extend(pdf_to_png(file_path, OUTPUT_DIR))
                elif conversion_type == "pdf:txt":
                    output_paths.append(pdf_to_txt(file_path, OUTPUT_DIR))
                elif conversion_type == "pdf:docx":
                    output_paths.append(pdf_to_docx(file_path, OUTPUT_DIR))
                else:
                    failed_files.append(f"{file_path.name}: unsupported PDF conversion.")
            except Exception as exc:
                failed_files.append(f"{file_path.name}: {readable_error(exc)}")

        return output_paths, failed_files

    return output_paths, [f"Unsupported conversion type: {conversion_type}"]


def mime_type_for_file(file_path: Path) -> str:
    return MIME_TYPES.get(file_path.suffix.lower(), "application/octet-stream")


def download_label_for_file(file_path: Path) -> str:
    extension = file_path.suffix.lower().lstrip(".")
    label = "FILE" if not extension else extension.upper()
    return f"Download {label}"


def txt_preview_for_file(file_path: Path, character_limit: int = 1000) -> str:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    preview = text[:character_limit]
    if not preview.strip():
        return EMPTY_TXT_PREVIEW_MESSAGE

    return preview


def show_download_button(file_path: Path, label: str) -> None:
    st.download_button(
        label,
        data=file_path.read_bytes(),
        file_name=file_path.name,
        mime=mime_type_for_file(file_path),
    )


def show_txt_preview(file_path: Path) -> None:
    if file_path.suffix.lower() != ".txt":
        return

    st.write(f"TXT preview: {file_path.name}")
    st.text_area(
        "Preview",
        txt_preview_for_file(file_path),
        height=240,
        disabled=True,
        label_visibility="collapsed",
    )


def main() -> None:
    st.set_page_config(page_title="FileMorph", page_icon="FM", layout="centered")
    st.title("FileMorph")
    st.caption("Local file conversion MVP. Files stay on this machine.")

    selected_label = st.selectbox("Conversion type", list(CONVERSION_OPTIONS))
    conversion_type = CONVERSION_OPTIONS[selected_label]
    selected_ocr_language = "eng"
    if conversion_type.startswith("ocr:"):
        selected_ocr_language_label = st.selectbox(
            "OCR language",
            list(OCR_LANGUAGE_OPTIONS),
        )
        selected_ocr_language = OCR_LANGUAGE_OPTIONS[selected_ocr_language_label]
        st.info(
            "Chinese OCR may require extra Tesseract language packs. "
            "On macOS, install them with: brew install tesseract-lang"
        )

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "webp", "pdf"],
    )

    if uploaded_files:
        st.write("Uploaded files:")
        for uploaded_file in uploaded_files:
            st.code(uploaded_file.name)

    if st.button("Convert", type="primary"):
        if not uploaded_files:
            st.error("Upload at least one file first.")
            return

        status = st.empty()
        status.info("Saving uploaded files...")

        try:
            saved_files = save_uploaded_files(uploaded_files)
        except Exception as exc:
            status.error(f"Upload failed: {readable_error(exc)}")
            return

        status.info("Converting files...")
        with st.spinner("Converting..."):
            output_paths, failed_files = convert_file_paths(
                saved_files,
                conversion_type,
                selected_ocr_language,
            )

        if output_paths:
            status.success(
                f"Conversion complete. {len(output_paths)} successful output(s)."
            )
        else:
            status.error("Conversion finished with no successful outputs.")

        if failed_files:
            st.error("Some files could not be converted.")
            for failed_file in failed_files:
                st.warning(failed_file)

        if not output_paths:
            return

        zip_path = None
        if len(output_paths) > 1:
            try:
                zip_path = create_zip_archive(output_paths, OUTPUT_DIR)
            except Exception as exc:
                st.warning(f"ZIP packaging failed: {readable_error(exc)}")

        st.write("Generated files:")
        for output_path in output_paths:
            st.code(str(output_path))
            show_txt_preview(output_path)

        if len(output_paths) == 1:
            show_download_button(
                output_paths[0],
                download_label_for_file(output_paths[0]),
            )
        elif zip_path:
            st.code(str(zip_path))
            show_download_button(zip_path, "Download ZIP")


if __name__ == "__main__":
    main()
