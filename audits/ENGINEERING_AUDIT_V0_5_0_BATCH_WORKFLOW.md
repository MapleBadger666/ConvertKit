# Engineering Audit: v0.5.0 Batch Workflow

## Scope

- Added multi-file batch workflow support to the Streamlit UI.
- Added simple per-file job status tracking for synchronous conversions.
- Added generated output listing, individual downloads, and ZIP packaging for multiple successful outputs.
- Added session-only conversion history.
- Fixed Images to one PDF grouped conversion behavior before committing v0.5.0.
- Added Images to separate PDFs and optional HEIC/HEIF image input support.

## Manual Bug Found

- Manual testing found Images to one PDF failed when multiple PNG files were uploaded, with errors like `Images to PDF: 'JPEG'`.
- Root workflow issue: the batch layer needed explicit grouped semantics for Images to one PDF instead of treating it like ordinary per-file conversion.
- Fix: Images to one PDF now creates one grouped job, passes the full image list to the existing combined-PDF converter once, and reports one output group.
- Follow-up manual testing found Images to one PDF still failed for multiple PNG screenshots with different sizes, including transparent screenshots, with error `Images to PDF: 'JPEG'`.
- Root converter issue: Pillow's PDF writer uses JPEG encoding for RGB images and looked up `Image.SAVE["JPEG"]`, but the JPEG save handler was not guaranteed to be registered before PDF save.
- Converter fix: PDF image creation now initializes Pillow save plugins before PDF output, applies EXIF orientation, flattens alpha/transparency onto a white RGB background, converts unsupported modes to RGB, and saves with an explicit `PDF` format.

## Changed Files

- `app/main.py`
- `app/converters/image_converter.py`
- `app/converters/ocr_converter.py`
- `app/converters/pdf_converter.py`
- `app/services/file_service.py`
- `tests/test_main_helpers.py`
- `tests/test_file_service.py`
- `tests/test_image_converter.py`
- `tests/test_pdf_converter.py`
- `tests/test_ocr_converter.py`
- `README.md`
- `CHANGELOG.md`
- `requirements.txt`
- `audits/ENGINEERING_AUDIT_V0_5_0_BATCH_WORKFLOW.md`

## What Changed

- The upload widget now accepts multiple files for conversion.
- Batch helper functions track input filename, conversion type, status, output paths, and per-file error text.
- Conversions run one file at a time, with failures recorded per file so later files can continue.
- Images to one PDF is a multi-input, single-output grouped conversion.
- Images to separate PDFs is a multi-input, multi-output per-file conversion.
- PNG screenshot batches with mixed sizes and RGBA/transparency are normalized safely before PDF output.
- Grouped PDF conversion failures now use `Images to one PDF failed: <reason>` instead of exposing only raw exception fragments such as `'JPEG'`.
- HEIC/HEIF file extensions are accepted for image workflows.
- HEIC/HEIF image opening is registered through `pillow-heif`; if unavailable, the app raises install guidance.
- The UI now shows progress, total/success/failed metrics, failed file errors, and an output table.
- Successful outputs can be downloaded individually.
- Multiple successful outputs can be packaged into `filemorph_outputs.zip`.
- Recent conversion history is kept in `st.session_state` for the current app session and can be cleared.
- README and changelog document the batch workflow.

## Intentionally Not Added

- No cloud APIs.
- No database or persistent history.
- No background workers.
- No async queue.
- No multiprocessing.
- No cloud or speech-to-text provider changes.
- No expensive startup checks.

## Image PDF Semantics

- Images to one PDF: combines many supported images into one generated PDF, reports total input files, and counts the successful output group as one success.
- Images to separate PDFs: converts each supported image into its own PDF, continues after per-file failures, and includes all successful PDFs in ZIP packaging.

## HEIC/HEIF Support Decision

- Implemented with `pillow-heif` as a Python dependency in `requirements.txt`.
- Upload filtering and extension validation include `heic` and `heif`.
- HEIC/HEIF registration is lazy and only runs when opening a HEIC/HEIF image.
- If support cannot be imported, the user sees: `HEIC/HEIF support requires pillow-heif. Install dependencies with: python -m pip install -r requirements.txt`

## Verification Result

- `python -m pytest -q` passed with 99 tests.
- Direct converter check with the four reported screenshot files produced one combined PDF successfully in a temporary directory.

## Manual UI Check Notes

- Earlier smoke check opened Streamlit at `http://localhost:8502`.
- Confirmed FileMorph renders with category selection, system dependency guidance, conversion history section, upload control, and Convert button.
- Confirmed upload input is configured for multiple files and image filters expose image extensions.
- A fresh Streamlit smoke check after the Images to separate PDFs/HEIC pass could not be rerun because local server approval was rejected by the environment usage limit.
- Full upload/conversion interaction was not completed through the browser surface because file-picker automation is limited in this environment.
- Behavior-level coverage now includes grouped Images to one PDF dispatch, real mixed-size RGBA PNG combined PDF creation, direct conversion of the four reported screenshot files, separate PDFs dispatch, failed-file continuation, success/failure counting, output rows, ZIP packaging, HEIC/HEIF validation, HEIC/HEIF dependency guidance, and history helpers.
