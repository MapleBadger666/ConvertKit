# FileMorph Deployment Guide

This guide covers two ways to present FileMorph:

- A local Mac desktop app for private day-to-day file conversion.
- A hosted online demo for showing the product to other people.

## Local Mac App

Create the desktop runtime:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-desktop.txt
```

Install FileMorph into `/Applications`:

```bash
./scripts/install_macos_app.sh
```

Open:

```text
/Applications/FileMorph.app
```

The generated `.app` bundles the FileMorph project source snapshot inside:

```text
Contents/Resources/FileMorph/source/
```

The build requires a usable project `.venv` with the desktop dependencies
installed. It bundles that runtime inside:

```text
Contents/Resources/FileMorph/.venv/
```

Runtime state is stored outside the bundle in:

```text
~/Library/Application Support/FileMorph/
```

That folder contains `uploads/`, `output/`, and logs. This means
`/Applications/FileMorph.app` does not depend on the original project folder
after installation and does not install key dependencies on first launch.

The local app starts `desktop/main.py`, launches the same Streamlit UI used by
the online demo as an internal localhost service, and embeds it in a FileMorph
WebView window. It does not open Safari, Chrome, Edge, or the system default
browser. Closing the FileMorph window stops the local Streamlit service.

Do not upload local runtime folders to GitHub. `.gitignore` excludes `.venv/`,
`dist/`, `uploads/`, `output/`, `logs/`, Python caches, and `.DS_Store`.

## Web Demo

The Streamlit interface remains available for online demos:

```bash
streamlit run app/main.py
```

Use the hosted Streamlit version for public previews and the `/Applications`
desktop app for private local work. Both modes render `app/main.py`, but the
macOS app is a local WebView wrapper, not a browser page and not the online
deployment.

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
