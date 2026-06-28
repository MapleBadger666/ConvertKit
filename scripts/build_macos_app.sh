#!/bin/bash

set -euo pipefail
export COPYFILE_DISABLE=1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_NAME="FileMorph"
APP_VERSION="${FILEMORPH_VERSION:-0.7.0}"
PLIST_VERSION="${APP_VERSION%%-*}"
BUILD_CHANNEL="${FILEMORPH_BUILD_CHANNEL:-local}"
BUILD_PROFILE="${FILEMORPH_BUILD_PROFILE:-lite}"
APP_DIR="$PROJECT_ROOT/dist/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
BUNDLE_APP_ROOT="$RESOURCES_DIR/FileMorph"
BUNDLE_SOURCE_ROOT="$BUNDLE_APP_ROOT/source"
BUNDLE_VENV_DIR="$BUNDLE_APP_ROOT/.venv"
EXECUTABLE="$MACOS_DIR/$APP_NAME"
PLIST="$CONTENTS_DIR/Info.plist"
ICON_FILE="$RESOURCES_DIR/FileMorph.icns"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      if [[ $# -lt 2 ]]; then
        echo "--profile requires lite or full" >&2
        exit 1
      fi
      BUILD_PROFILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ "$BUILD_PROFILE" != "lite" && "$BUILD_PROFILE" != "full" ]]; then
  echo "Profile must be lite or full" >&2
  exit 1
fi

rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR" "$BUNDLE_SOURCE_ROOT"
echo "$BUILD_PROFILE" > "$BUNDLE_APP_ROOT/build-profile.txt"

ICON_PYTHON="python3"
if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  ICON_PYTHON="$PROJECT_ROOT/.venv/bin/python"
fi

"$ICON_PYTHON" "$PROJECT_ROOT/scripts/create_macos_icon.py" "$ICON_FILE"

echo "Copying runtime source files into $BUNDLE_SOURCE_ROOT"
rsync -a \
  --exclude ".DS_Store" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "*.pyo" \
  "$PROJECT_ROOT/app/" "$BUNDLE_SOURCE_ROOT/app/"

rsync -a \
  --exclude ".DS_Store" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "*.pyo" \
  "$PROJECT_ROOT/desktop/" "$BUNDLE_SOURCE_ROOT/desktop/"

if [[ -d "$PROJECT_ROOT/.streamlit" ]]; then
  rsync -a \
    --exclude ".DS_Store" \
    "$PROJECT_ROOT/.streamlit/" "$BUNDLE_SOURCE_ROOT/.streamlit/"
fi

for runtime_file in \
  requirements.txt \
  requirements-runtime-core.txt \
  requirements-runtime-heavy.txt \
  requirements-desktop.txt \
  README.md \
  LICENSE; do
  if [[ -f "$PROJECT_ROOT/$runtime_file" ]]; then
    rsync -a "$PROJECT_ROOT/$runtime_file" "$BUNDLE_SOURCE_ROOT/$runtime_file"
  fi
done

if [[ ! -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  echo "A usable project .venv is required to build the macOS app." >&2
  echo "Run: python -m venv .venv && .venv/bin/python -m pip install -r requirements-desktop.txt" >&2
  exit 1
fi

if ! "$PROJECT_ROOT/.venv/bin/python" -c "import PIL.Image, streamlit, webview" >/dev/null 2>&1; then
  echo "The project .venv is missing required desktop dependencies." >&2
  echo "Run: .venv/bin/python -m pip install -r requirements-desktop.txt" >&2
  exit 1
fi

prune_site_package_patterns() {
  local site_packages="$1"
  shift

  for pattern in "$@"; do
    find "$site_packages" -maxdepth 1 -name "$pattern" -exec rm -rf {} +
  done
}

prune_lite_runtime() {
  local site_packages
  while IFS= read -r site_packages; do
    prune_site_package_patterns "$site_packages" \
      "av" \
      "av-*.dist-info" \
      "ctranslate2" \
      "ctranslate2-*.dist-info" \
      "cv2" \
      "faster_whisper" \
      "faster_whisper-*.dist-info" \
      "fitz" \
      "fire" \
      "fire-*.dist-info" \
      "hf_xet" \
      "hf_xet-*.dist-info" \
      "huggingface_hub" \
      "huggingface_hub-*.dist-info" \
      "onnxruntime" \
      "onnxruntime-*.dist-info" \
      "opencv_python*" \
      "pdf2docx" \
      "pdf2docx-*.dist-info" \
      "pymupdf" \
      "pymupdf-*.dist-info" \
      "PyMuPDF*" \
      "pytesseract" \
      "pytesseract-*.dist-info" \
      "tokenizers" \
      "tokenizers-*.dist-info" \
      "tqdm" \
      "tqdm-*.dist-info"
    rm -rf "$site_packages/streamlit/.agents"
  done < <(find "$BUNDLE_VENV_DIR/lib" -type d -name site-packages)

  rm -f \
    "$BUNDLE_VENV_DIR"/bin/ct2-* \
    "$BUNDLE_VENV_DIR"/bin/hf \
    "$BUNDLE_VENV_DIR"/bin/huggingface-cli \
    "$BUNDLE_VENV_DIR"/bin/onnxruntime_test \
    "$BUNDLE_VENV_DIR"/bin/pdf2docx \
    "$BUNDLE_VENV_DIR"/bin/pyav \
    "$BUNDLE_VENV_DIR"/bin/pymupdf \
    "$BUNDLE_VENV_DIR"/bin/pytesseract \
    "$BUNDLE_VENV_DIR"/bin/tiny-agents \
    "$BUNDLE_VENV_DIR"/bin/tqdm
}

clean_bundle_metadata() {
  find "$APP_DIR" -name "._*" -delete
  find "$APP_DIR" -name ".DS_Store" -delete
  if command -v dot_clean >/dev/null 2>&1; then
    dot_clean -m "$APP_DIR" || true
  fi
  if command -v xattr >/dev/null 2>&1; then
    xattr -cr "$APP_DIR" || true
  fi
  find "$APP_DIR" -name "._*" -delete
  find "$APP_DIR" -name ".DS_Store" -delete
}

validate_lite_runtime() {
  local forbidden
  forbidden="$(
    find "$BUNDLE_VENV_DIR" \
      \( -iname "*onnxruntime*" \
      -o -iname "*pymupdf*" \
      -o -iname "cv2" \
      -o -iname "*faster_whisper*" \
      -o -iname "*tokenizers*" \
      -o -iname "*hf_xet*" \
      -o -iname "av" \
      -o -path "*/av/*" \) \
      -print
  )"

  if [[ -n "$forbidden" ]]; then
    echo "Lite runtime still contains optional heavy dependencies:" >&2
    echo "$forbidden" >&2
    exit 1
  fi
}

echo "Bundling existing Python environment into $BUNDLE_VENV_DIR"
rsync -a \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "*.pyo" \
  --exclude ".pytest_cache" \
  --exclude ".mypy_cache" \
  --exclude ".ruff_cache" \
  --exclude "pip/cache" \
  "$PROJECT_ROOT/.venv/" "$BUNDLE_VENV_DIR/"

find "$BUNDLE_SOURCE_ROOT" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$BUNDLE_SOURCE_ROOT" -type f -name "*.pyc" -delete
find "$BUNDLE_SOURCE_ROOT" -type f -name "*.pyo" -delete
if [[ -d "$BUNDLE_VENV_DIR" ]]; then
  find "$BUNDLE_VENV_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +
  find "$BUNDLE_VENV_DIR" -type d -name ".pytest_cache" -prune -exec rm -rf {} +
  find "$BUNDLE_VENV_DIR" -type d -name ".mypy_cache" -prune -exec rm -rf {} +
  find "$BUNDLE_VENV_DIR" -type d -name ".ruff_cache" -prune -exec rm -rf {} +
  find "$BUNDLE_VENV_DIR" -type d -name "*.dSYM" -prune -exec rm -rf {} +
  find "$BUNDLE_VENV_DIR" -type d \( -name tests -o -name test \) -prune -exec rm -rf {} +
  find "$BUNDLE_VENV_DIR" -type f -name "*.pyc" -delete
  find "$BUNDLE_VENV_DIR" -type f -name "*.pyo" -delete
  find "$BUNDLE_VENV_DIR" -type f -name "*.map" -delete
  find "$BUNDLE_VENV_DIR" -name "._*" -delete
  rm -rf "$BUNDLE_VENV_DIR/share/jupyter" "$BUNDLE_VENV_DIR/share/man"
  if [[ "$BUILD_PROFILE" == "lite" ]]; then
    echo "Pruning optional heavy dependencies for lite profile"
    prune_lite_runtime
    validate_lite_runtime
  fi
fi

clean_bundle_metadata

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleDisplayName</key>
  <string>$APP_NAME</string>
  <key>CFBundleExecutable</key>
  <string>$APP_NAME</string>
  <key>CFBundleIdentifier</key>
  <string>local.filemorph.desktop</string>
  <key>CFBundleIconFile</key>
  <string>FileMorph.icns</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>$APP_NAME</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>$PLIST_VERSION</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSMinimumSystemVersion</key>
  <string>11.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
PLIST

cat > "$EXECUTABLE" <<LAUNCHER
#!/bin/bash

set -euo pipefail

APP_ROOT="\$(cd "\$(dirname "\$0")/../Resources/FileMorph/source" && pwd)"
BUNDLE_VENV_DIR="\$(cd "\$(dirname "\$0")/../Resources/FileMorph" && pwd)/.venv"
DATA_ROOT="\${FILEMORPH_DATA_DIR:-\$HOME/Library/Application Support/FileMorph}"
VENV_DIR="\$BUNDLE_VENV_DIR"
PYTHON="\$VENV_DIR/bin/python"
APP_ENTRY="\$APP_ROOT/desktop/main.py"
LOG_DIR="\$DATA_ROOT/logs"
LOG_FILE="\$LOG_DIR/filemorph.log"

export FILEMORPH_DATA_DIR="\$DATA_ROOT"
export FILEMORPH_RUNTIME="local"
export FILEMORPH_APP_VERSION="${APP_VERSION}"
export FILEMORPH_BUILD_CHANNEL="${BUILD_CHANNEL}"
export FILEMORPH_BUILD_PROFILE="${BUILD_PROFILE}"
export STREAMLIT_SERVER_HEADLESS="true"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\$PATH"

show_error() {
  local message="\$1"
  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display dialog \"\$message\" buttons {\"OK\"} default button \"OK\" with title \"FileMorph\" with icon caution" >/dev/null 2>&1 || true
  fi
  echo "\$message"
}

python_environment_usable() {
  if [[ ! -x "\$PYTHON" ]]; then
    return 1
  fi

  "\$PYTHON" -c "import PIL.Image, streamlit, webview" >/dev/null 2>&1
}

mkdir -p "\$DATA_ROOT/uploads" "\$DATA_ROOT/output" "\$LOG_DIR"
exec >> "\$LOG_FILE" 2>&1

cd "\$APP_ROOT"
if ! python_environment_usable; then
  show_error "FileMorph's bundled runtime is missing or unusable. Rebuild and reinstall FileMorph.app."
  exit 1
fi

echo "Using bundled Python environment at \$BUNDLE_VENV_DIR"

exec "\$PYTHON" "\$APP_ENTRY"
LAUNCHER

chmod +x "$EXECUTABLE"

echo "Created $APP_DIR"
