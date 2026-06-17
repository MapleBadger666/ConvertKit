#!/bin/bash

set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"
APP_ENTRY="$APP_DIR/app/main.py"
LOCAL_URL="http://127.0.0.1:8501"

cd "$APP_DIR"

print_header() {
  echo
  echo "========================================"
  echo " FileMorph local desktop launcher"
  echo "========================================"
  echo
}

pause_on_error() {
  local status="$1"
  if [[ "$status" -ne 0 ]]; then
    echo
    echo "FileMorph could not start. Check the message above, then press Return to close this window."
    read -r
  fi
}

ensure_python() {
  if [[ -x "$VENV_DIR/bin/python" ]]; then
    return
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found. Install Python 3, then run this launcher again."
    exit 1
  fi

  echo "Creating local Python environment in .venv ..."
  python3 -m venv "$VENV_DIR"
}

ensure_python_dependencies() {
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"

  if python -c "import streamlit" >/dev/null 2>&1; then
    return
  fi

  echo "Installing FileMorph Python dependencies ..."
  python -m pip install -r "$REQUIREMENTS_FILE"
}

warn_missing_system_tools() {
  local missing=()

  for tool in pdfinfo pdftoppm tesseract soffice ffmpeg; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      missing+=("$tool")
    fi
  done

  if [[ "${#missing[@]}" -eq 0 ]]; then
    return
  fi

  echo "Some optional system tools were not detected:"
  printf ' - %s\n' "${missing[@]}"
  echo
  echo "Install the full macOS toolchain with:"
  echo "  brew install poppler tesseract tesseract-lang ffmpeg"
  echo "  brew install --cask libreoffice"
  echo
  echo "FileMorph will still start, but related conversion features may fail until those tools are installed."
  echo
}

print_header
ensure_python
ensure_python_dependencies
warn_missing_system_tools

echo "Starting FileMorph ..."
echo "If a browser does not open automatically, visit:"
echo "  $LOCAL_URL"
echo

if command -v curl >/dev/null 2>&1 && curl -fsS "$LOCAL_URL" >/dev/null 2>&1; then
  echo "FileMorph is already running. Opening the local app."
  open "$LOCAL_URL" >/dev/null 2>&1 || true
  exit 0
fi

set +e
python -m streamlit run "$APP_ENTRY" \
  --server.address 127.0.0.1 \
  --server.port 8501
status="$?"
set -e
pause_on_error "$status"
exit "$status"
