#!/bin/bash

set -euo pipefail
export COPYFILE_DISABLE=1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_NAME="FileMorph"
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

rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR" "$BUNDLE_SOURCE_ROOT"

ICON_PYTHON="python3"
if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  ICON_PYTHON="$PROJECT_ROOT/.venv/bin/python"
fi

"$ICON_PYTHON" "$PROJECT_ROOT/scripts/create_macos_icon.py" "$ICON_FILE"

rsync -a \
  --exclude ".DS_Store" \
  --exclude ".git" \
  --exclude ".pytest_cache" \
  --exclude ".venv" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "dist" \
  --exclude "logs" \
  --exclude "output" \
  --exclude "uploads" \
  "$PROJECT_ROOT/" "$BUNDLE_SOURCE_ROOT/"

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

echo "Bundling existing Python environment into $BUNDLE_VENV_DIR"
rsync -a \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  "$PROJECT_ROOT/.venv/" "$BUNDLE_VENV_DIR/"

find "$BUNDLE_SOURCE_ROOT" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$BUNDLE_SOURCE_ROOT" -type f -name "*.pyc" -delete
find "$APP_DIR" -name "._*" -delete
if [[ -d "$BUNDLE_VENV_DIR" ]]; then
  find "$BUNDLE_VENV_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +
  find "$BUNDLE_VENV_DIR" -type f -name "*.pyc" -delete
  find "$BUNDLE_VENV_DIR" -name "._*" -delete
fi

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
  <string>0.5.0</string>
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
