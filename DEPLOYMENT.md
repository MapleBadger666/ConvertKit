# FileMorph Deployment Guide

This guide covers two ways to present FileMorph:

- A local Mac desktop app for private day-to-day file conversion.
- A hosted online demo for showing the product to other people.

## Local Mac App

Create or refresh the macOS app wrapper and Desktop shortcut:

```bash
./scripts/install_macos_shortcut.sh
```

Open:

```text
~/Desktop/FileMorph.app
```

The app opens a local Streamlit service at:

```text
http://127.0.0.1:8501
```

This is still a local app experience: the `.app` is the shortcut, Terminal keeps
the local Streamlit process alive, and the browser displays the UI.

## Docker

Build:

```bash
docker build -t filemorph .
```

Run:

```bash
docker run --rm -p 8501:8501 filemorph
```

Open:

```text
http://127.0.0.1:8501
```

The Docker image installs the system tools needed for the broadest feature set:
Poppler, Tesseract with Chinese language data, LibreOffice, and ffmpeg.

## Render

This repository includes `render.yaml` for Render Blueprint deployment.

1. Push the repository to GitHub.
2. In Render, create a new Blueprint from the repository.
3. Render will use `Dockerfile`, expose the app on the platform `PORT`, and use
   `/_stcore/health` for health checks.

The Render config sets:

```text
FILEMORPH_RUNTIME=online
STREAMLIT_SERVER_HEADLESS=true
```

## Railway, Fly.io, Or Any Docker Host

Use the included `Dockerfile`.

The container command is:

```bash
streamlit run app/main.py --server.address 0.0.0.0 --server.port ${PORT:-8501}
```

Set `FILEMORPH_RUNTIME=online` so visitors see the correct server-side upload
notice.

## Streamlit Community Cloud

Use:

- Main file: `app/main.py`
- Python dependencies: `requirements.txt`
- System packages: `packages.txt`
- Environment variable: `FILEMORPH_RUNTIME=online`

Streamlit Community Cloud is convenient for demos, but the full conversion stack
can be heavy. Docker hosting is more predictable for LibreOffice conversions,
media workflows, and transcription model downloads.

## Online Privacy And Cleanup

Online deployments process files on the remote server. Before using FileMorph for
private or customer files online, add:

- Authentication.
- File retention and cleanup jobs for `uploads/` and `output/`.
- Storage limits.
- Request size limits.
- Clear user-facing privacy language.

For a public demo, use non-sensitive sample files.
