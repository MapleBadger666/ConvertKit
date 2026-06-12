from __future__ import annotations

import sys
from pathlib import Path
from shutil import which

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.converters.pdf_converter import images_to_pdf, pdf_to_docx, pdf_to_png, pdf_to_txt
from app.converters.media_converter import video_to_audio
from app.converters.ocr_converter import (
    OCR_MODE_DOCUMENT,
    OCR_MODE_SCREENSHOT,
    OCR_MODE_STANDARD,
    get_installed_tesseract_languages,
    image_to_text,
    pdf_to_text_with_ocr,
    required_ocr_languages,
)
from app.converters.office_converter import (
    PPTX_DOCX_MODE_SLIDE_IMAGES,
    PPTX_DOCX_MODE_SLIDE_IMAGES_WITH_TEXT,
    PPTX_DOCX_MODE_TEXT_OUTLINE,
    pptx_to_docx,
    pptx_to_pdf,
)
from app.converters.transcription_converter import audio_to_txt, video_to_txt
from app.services.file_service import (
    OUTPUT_DIR,
    create_zip_archive,
    ensure_directory,
    is_supported_audio,
    is_supported_image,
    is_supported_pdf,
    is_supported_pptx,
    is_supported_video,
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
    "PPTX to PDF": "office:pptx_pdf",
    "PPTX to DOCX": "office:pptx_docx",
    "Video to Audio": "media:audio",
    "Audio to TXT": "transcription:audio_txt",
    "Video to TXT": "transcription:video_txt",
    "Image to TXT (OCR)": "ocr:image_txt",
    "Scanned PDF to TXT (OCR)": "ocr:pdf_txt",
}
CONVERSION_CATEGORIES = {
    "Images": [
        "Images to JPG",
        "Images to PNG",
        "Images to WEBP",
        "Images to one PDF",
    ],
    "PDF": [
        "PDF pages to PNG",
        "PDF to TXT",
        "PDF to DOCX",
    ],
    "OCR": [
        "Image to TXT (OCR)",
        "Scanned PDF to TXT (OCR)",
    ],
    "Office": [
        "PPTX to PDF",
        "PPTX to DOCX",
    ],
    "Media": [
        "Video to Audio",
    ],
    "Transcription": [
        "Audio to TXT",
        "Video to TXT",
    ],
}
CONVERSION_CATEGORY_HELP = {
    "Images": "Convert common image formats or combine images into one PDF.",
    "PDF": "Convert PDF pages, extract selectable text, or create DOCX drafts.",
    "OCR": "Use enhanced modes for screenshots or scanned documents.",
    "Office": "Convert presentations to PDF or DOCX.",
    "Media": "WAV is best for transcription; MP3 is smaller.",
    "Transcription": "Use small for better accuracy; choose language manually for short clips.",
}

OCR_LANGUAGE_OPTIONS = {
    "English": "eng",
    "Simplified Chinese": "chi_sim",
    "Traditional Chinese": "chi_tra",
    "English + Simplified Chinese": "eng+chi_sim",
}
OCR_MODE_OPTIONS = {
    "Standard OCR": OCR_MODE_STANDARD,
    "Enhanced OCR for screenshots": OCR_MODE_SCREENSHOT,
    "Enhanced OCR for scanned documents": OCR_MODE_DOCUMENT,
}
PPTX_DOCX_MODE_OPTIONS = {
    "Text Outline": PPTX_DOCX_MODE_TEXT_OUTLINE,
    "Slide Images": PPTX_DOCX_MODE_SLIDE_IMAGES,
    "Slide Images + Extracted Text": PPTX_DOCX_MODE_SLIDE_IMAGES_WITH_TEXT,
}
TRANSCRIPTION_MODEL_OPTIONS = ["tiny", "base", "small"]
TRANSCRIPTION_LANGUAGE_OPTIONS = {
    "Auto-detect": None,
    "English": "en",
    "Simplified Chinese": "zh",
}
CHINESE_OCR_LANGUAGE_WARNING = (
    "Chinese OCR language packs are not installed. "
    "On macOS, run: brew install tesseract-lang"
)

MIME_TYPES = {
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".zip": "application/zip",
}

EMPTY_TXT_PREVIEW_MESSAGE = (
    "The TXT file was generated, but no readable text was found."
)
OCR_LOW_QUALITY_WARNING = (
    "OCR completed, but the result may be low quality. Try a clearer image, "
    "higher resolution, or a different OCR mode."
)
TRANSCRIPTION_MODEL_GUIDANCE = (
    "tiny = fastest rough draft, base = balanced, small = better accuracy and slower."
)
TRANSCRIPTION_AUDIO_GUIDANCE = (
    "Use short, clear audio when possible. Background noise and low volume can reduce accuracy."
)
SYSTEM_DEPENDENCIES = [
    {
        "name": "Poppler",
        "commands": ["pdfinfo", "pdftoppm"],
        "required_for": "PDF to PNG, scanned PDF OCR, PPTX slide-image DOCX",
        "install": "brew install poppler",
    },
    {
        "name": "Tesseract",
        "commands": ["tesseract"],
        "required_for": "Image OCR, scanned PDF OCR",
        "install": "brew install tesseract",
    },
    {
        "name": "LibreOffice",
        "commands": ["soffice"],
        "required_for": "PPTX to PDF, PPTX slide-image DOCX",
        "install": "brew install --cask libreoffice",
    },
    {
        "name": "ffmpeg",
        "commands": ["ffmpeg"],
        "required_for": "Video to Audio, Video to TXT, audio preprocessing",
        "install": "brew install ffmpeg",
    },
    {
        "name": "faster-whisper",
        "commands": [],
        "required_for": "Audio to TXT, Video to TXT",
        "install": "python -m pip install -r requirements.txt",
    },
]


def readable_error(exc: Exception) -> str:
    message = str(exc).strip()
    return message or exc.__class__.__name__


def get_category_conversion_options(category: str) -> dict[str, str]:
    return {
        label: CONVERSION_OPTIONS[label]
        for label in CONVERSION_CATEGORIES[category]
    }


def command_group_available(commands: list[str]) -> bool | None:
    if not commands:
        return None

    return all(which(command) for command in commands)


def dependency_status_label(commands: list[str]) -> str:
    available = command_group_available(commands)
    if available is None:
        return "Python package"

    return "Detected" if available else "Not detected"


def system_dependency_rows() -> list[dict[str, str]]:
    return [
        {
            "Dependency": dependency["name"],
            "Required for": dependency["required_for"],
            "Install": dependency["install"],
            "Status": dependency_status_label(dependency["commands"]),
        }
        for dependency in SYSTEM_DEPENDENCIES
    ]


def conversion_help_text(conversion_type: str) -> str:
    if conversion_type.startswith("ocr:"):
        return "Use enhanced modes for screenshots or scanned documents."

    if conversion_type == "office:pptx_docx":
        return "Text Outline is editable; Slide Images preserves appearance; Mixed gives both."

    if conversion_type.startswith("transcription:"):
        return "Use small for better accuracy; choose language manually for short clips."

    if conversion_type == "media:audio":
        return "WAV is best for transcription; MP3 is smaller."

    if conversion_type.startswith("pdf:"):
        return "Some PDF workflows require local system tools such as Poppler."

    if conversion_type.startswith("office:"):
        return "PowerPoint visual conversion requires local LibreOffice."

    return "Files are processed locally and generated outputs are saved to output/."


def get_allowed_upload_types(conversion_type: str) -> list[str]:
    image_types = ["jpg", "jpeg", "png", "webp"]
    pdf_types = ["pdf"]
    pptx_types = ["pptx"]
    video_types = ["mp4", "mov", "mkv", "avi"]
    audio_types = ["mp3", "wav", "m4a", "aac", "flac"]

    if conversion_type.startswith("image:"):
        return image_types

    if conversion_type == "images:pdf":
        return image_types

    if conversion_type == "ocr:image_txt":
        return image_types

    if conversion_type.startswith("pdf:"):
        return pdf_types

    if conversion_type == "ocr:pdf_txt":
        return pdf_types

    if conversion_type.startswith("office:"):
        return pptx_types

    if conversion_type == "media:audio":
        return video_types

    if conversion_type == "transcription:audio_txt":
        return audio_types

    if conversion_type == "transcription:video_txt":
        return video_types

    return [*image_types, *pdf_types, *pptx_types, *video_types, *audio_types]


def get_available_ocr_language_options(
    installed_languages: set[str],
) -> dict[str, str]:
    return {
        label: language
        for label, language in OCR_LANGUAGE_OPTIONS.items()
        if required_ocr_languages(language).issubset(installed_languages)
    }


def default_ocr_mode_index(conversion_type: str) -> int:
    labels = list(OCR_MODE_OPTIONS)
    if conversion_type == "ocr:pdf_txt":
        return labels.index("Enhanced OCR for scanned documents")

    return labels.index("Enhanced OCR for screenshots")


def get_transcription_language_code(label: str) -> str | None:
    return TRANSCRIPTION_LANGUAGE_OPTIONS[label]


def transcription_language_guidance(label: str) -> str:
    if label == "English":
        return "For clearer English transcription, use base or small. tiny is fastest but less accurate."

    if label == "Simplified Chinese":
        return "For Chinese speech, choose Simplified Chinese instead of Auto-detect for better results."

    return "If the transcript looks wrong, choose the spoken language manually."


def transcription_post_conversion_messages(
    model_size: str,
    language_label: str,
) -> list[str]:
    messages: list[str] = []
    if model_size == "tiny":
        messages.append("For better accuracy, try base or small.")

    if language_label == "Auto-detect":
        messages.append("If the transcript looks wrong, choose the spoken language manually.")
    elif language_label == "Simplified Chinese":
        messages.append(
            "Chinese transcription works best with clear Mandarin audio and small model."
        )
    elif language_label == "English":
        messages.append(
            "English transcription improves with clear speech, low background noise, and base/small model."
        )

    return messages


def convert_file_paths(
    file_paths: list[Path],
    conversion_type: str,
    ocr_language: str = "eng",
    ocr_mode: str = OCR_MODE_STANDARD,
    audio_format: str = "wav",
    pptx_docx_mode: str = PPTX_DOCX_MODE_TEXT_OUTLINE,
    transcription_model_size: str = "base",
    transcription_language: str | None = None,
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
                text = image_to_text(file_path, ocr_language, ocr_mode)
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
                    pdf_to_text_with_ocr(
                        file_path,
                        OUTPUT_DIR,
                        ocr_language,
                        ocr_mode,
                    )
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

    if conversion_type.startswith("office:"):
        for file_path in file_paths:
            if not is_supported_pptx(file_path):
                failed_files.append(f"{file_path.name}: expected a PPTX file.")
                continue

            try:
                if conversion_type == "office:pptx_pdf":
                    output_paths.append(pptx_to_pdf(file_path, OUTPUT_DIR))
                elif conversion_type == "office:pptx_docx":
                    output_paths.append(
                        pptx_to_docx(file_path, OUTPUT_DIR, pptx_docx_mode)
                    )
                else:
                    failed_files.append(
                        f"{file_path.name}: unsupported Office conversion."
                    )
            except Exception as exc:
                failed_files.append(f"{file_path.name}: {readable_error(exc)}")

        return output_paths, failed_files

    if conversion_type == "media:audio":
        for file_path in file_paths:
            if not is_supported_video(file_path):
                failed_files.append(f"{file_path.name}: expected a supported video file.")
                continue

            try:
                output_paths.append(video_to_audio(file_path, OUTPUT_DIR, audio_format))
            except Exception as exc:
                failed_files.append(f"{file_path.name}: {readable_error(exc)}")

        return output_paths, failed_files

    if conversion_type == "transcription:audio_txt":
        for file_path in file_paths:
            if not is_supported_audio(file_path):
                failed_files.append(f"{file_path.name}: expected a supported audio file.")
                continue

            try:
                output_paths.append(
                    audio_to_txt(
                        file_path,
                        OUTPUT_DIR,
                        transcription_model_size,
                        transcription_language,
                    )
                )
            except Exception as exc:
                failed_files.append(f"{file_path.name}: {readable_error(exc)}")

        return output_paths, failed_files

    if conversion_type == "transcription:video_txt":
        for file_path in file_paths:
            if not is_supported_video(file_path):
                failed_files.append(f"{file_path.name}: expected a supported video file.")
                continue

            try:
                output_paths.append(
                    video_to_txt(
                        file_path,
                        OUTPUT_DIR,
                        transcription_model_size,
                        transcription_language,
                    )
                )
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


def is_low_quality_ocr_text(text: str, minimum_characters: int = 20) -> bool:
    return len(text.strip()) < minimum_characters


def should_show_ocr_quality_warning(file_path: Path) -> bool:
    if file_path.suffix.lower() != ".txt":
        return False

    return is_low_quality_ocr_text(file_path.read_text(encoding="utf-8", errors="replace"))


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
    st.caption(
        "FileMorph is a local-only file conversion toolkit for documents, images, OCR, media, and transcription."
    )
    st.write(
        "Runs locally. No cloud upload. Some conversions require system tools installed on this machine."
    )

    with st.expander("System dependencies"):
        st.table(system_dependency_rows())
        st.caption(
            "Status checks are lightweight command lookups. Python packages are managed through requirements.txt."
        )

    selected_category = st.selectbox("Category", list(CONVERSION_CATEGORIES))
    st.caption(CONVERSION_CATEGORY_HELP[selected_category])
    category_options = get_category_conversion_options(selected_category)
    selected_label = st.selectbox("Conversion type", list(category_options))
    conversion_type = category_options[selected_label]
    st.info(conversion_help_text(conversion_type))
    selected_ocr_language = "eng"
    selected_ocr_mode = OCR_MODE_STANDARD
    selected_audio_format = "wav"
    selected_pptx_docx_mode = PPTX_DOCX_MODE_TEXT_OUTLINE
    selected_transcription_model_size = "base"
    selected_transcription_language = None
    selected_transcription_language_label = "Auto-detect"
    if conversion_type.startswith("ocr:"):
        installed_ocr_languages: set[str] = set()
        try:
            installed_ocr_languages = get_installed_tesseract_languages()
        except Exception:
            st.warning(
                "OCR requires Tesseract. On macOS, install it with: brew install tesseract"
            )

        available_ocr_options = get_available_ocr_language_options(
            installed_ocr_languages
        )
        if not available_ocr_options:
            available_ocr_options = {"English": "eng"}

        selected_ocr_language_label = st.selectbox(
            "OCR language",
            list(available_ocr_options),
        )
        selected_ocr_language = available_ocr_options[selected_ocr_language_label]
        if not {"chi_sim", "chi_tra"}.issubset(installed_ocr_languages):
            st.warning(CHINESE_OCR_LANGUAGE_WARNING)

        selected_ocr_mode_label = st.selectbox(
            "OCR mode",
            list(OCR_MODE_OPTIONS),
            index=default_ocr_mode_index(conversion_type),
        )
        selected_ocr_mode = OCR_MODE_OPTIONS[selected_ocr_mode_label]

    if conversion_type == "media:audio":
        selected_audio_format_label = st.selectbox("Audio format", ["WAV", "MP3"])
        selected_audio_format = selected_audio_format_label.lower()

    if conversion_type == "office:pptx_docx":
        selected_pptx_docx_mode_label = st.selectbox(
            "DOCX mode",
            list(PPTX_DOCX_MODE_OPTIONS),
        )
        selected_pptx_docx_mode = PPTX_DOCX_MODE_OPTIONS[selected_pptx_docx_mode_label]

    if conversion_type.startswith("transcription:"):
        selected_transcription_model_size = st.selectbox(
            "Transcription model",
            TRANSCRIPTION_MODEL_OPTIONS,
            index=TRANSCRIPTION_MODEL_OPTIONS.index("base"),
        )
        st.caption(TRANSCRIPTION_MODEL_GUIDANCE)
        selected_transcription_language_label = st.selectbox(
            "Transcription language",
            list(TRANSCRIPTION_LANGUAGE_OPTIONS),
        )
        selected_transcription_language = get_transcription_language_code(
            selected_transcription_language_label
        )
        st.info(transcription_language_guidance(selected_transcription_language_label))
        st.caption(TRANSCRIPTION_AUDIO_GUIDANCE)

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        type=get_allowed_upload_types(conversion_type),
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
                selected_ocr_mode,
                selected_audio_format,
                selected_pptx_docx_mode,
                selected_transcription_model_size,
                selected_transcription_language,
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

        if conversion_type.startswith("transcription:"):
            for message in transcription_post_conversion_messages(
                selected_transcription_model_size,
                selected_transcription_language_label,
            ):
                st.info(message)

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
            if conversion_type.startswith("ocr:") and should_show_ocr_quality_warning(
                output_path
            ):
                st.warning(OCR_LOW_QUALITY_WARNING)

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
