# FileMorph Deployment Guide

This guide covers two ways to present FileMorph:

- A local Mac desktop app for private day-to-day file conversion.
- A hosted online demo for showing the product to other people.

## Local Mac App

For ordinary users, publish macOS installers through GitHub Releases:

- `FileMorph-macOS.dmg`: contains `FileMorph.app` and an `Applications`
  shortcut so users can drag the app into `/Applications`.
- `FileMorph-Installer.pkg`: installs `FileMorph.app` directly into
  `/Applications`.

Make the `.dmg` and `.pkg` the primary downloads. GitHub's automatic
`Source code (zip)` and `Source code (tar.gz)` files are not installers; they are
for developers who want to build from source.

Unsigned builds may trigger macOS Gatekeeper. Tell users to right-click
`FileMorph.app`, choose Open, then confirm. A signed and notarized build can
remove that extra step later.

Source users can build those installers locally. First create the desktop
runtime:

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

Build release artifacts:

```bash
./scripts/release_macos.sh v0.6.1
```

The release script runs tests, validates shell script syntax, builds the app,
creates both installers, checks artifact sizes, and prints SHA256 checksums. It
does not commit, push, tag, or create a GitHub Release.

For targeted builds, use:

```bash
./scripts/build_macos_dmg.sh
./scripts/build_macos_pkg.sh
./scripts/verify_release_assets.sh
```

The build scripts first run `scripts/build_macos_app.sh`, then create:

```text
dist/FileMorph.app
dist/FileMorph-macOS.dmg
dist/FileMorph-Installer.pkg
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

That folder contains `uploads/`, `output/`, and `logs/`. The desktop launcher
creates those folders automatically, keeps runtime files out of the app bundle,
and writes startup diagnostics to `logs/filemorph-desktop-ui.log`. This means
`/Applications/FileMorph.app` does not depend on the original project folder
after installation and does not install key dependencies on first launch.

The local app starts `desktop/main.py`, launches the same Streamlit UI used by
the online demo as an internal localhost service, and embeds it in a FileMorph
WebView window. It does not open Safari, Chrome, Edge, or the system default
browser. Closing the FileMorph window stops the local Streamlit service. The
launcher also records the Python executable, bundled-runtime status, selected
Streamlit port, health check result, and shutdown cleanup result in the desktop
log so startup failures can be diagnosed without a blank window.

App version and build channel metadata are defined in:

```text
app/version.py
```

Runtime path constants are defined in:

```text
app/runtime_paths.py
```

The source defaults do not depend on a GitHub Release tag. Packaged builds can
override the version through build-time environment variables.

Do not upload local runtime folders to GitHub. `.gitignore` excludes `.venv/`,
`dist/`, `uploads/`, `output/`, `logs/`, Python caches, and `.DS_Store`.
Commit the build scripts and docs, then attach `.dmg` and `.pkg` as release
artifacts instead of committing them to the repository.

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
