#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_NAME="FileMorph"
APP_DIR="$PROJECT_ROOT/dist/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
EXECUTABLE="$MACOS_DIR/$APP_NAME"
PLIST="$CONTENTS_DIR/Info.plist"
ICON_FILE="$RESOURCES_DIR/FileMorph.icns"

mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

ICON_PYTHON="python3"
if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  ICON_PYTHON="$PROJECT_ROOT/.venv/bin/python"
fi

"$ICON_PYTHON" "$PROJECT_ROOT/scripts/create_macos_icon.py" "$ICON_FILE"

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

PROJECT_ROOT="$PROJECT_ROOT"
LAUNCHER="\$PROJECT_ROOT/FileMorph.command"

show_error() {
  local message="\$1"
  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display dialog \"\$message\" buttons {\"OK\"} default button \"OK\" with title \"FileMorph\" with icon caution" >/dev/null 2>&1 || true
  fi
  echo "\$message"
}

if [[ ! -x "\$LAUNCHER" ]]; then
  show_error "FileMorph.command was not found or is not executable. Rebuild the app wrapper from the FileMorph project folder."
  exit 1
fi

osascript - "\$PROJECT_ROOT" <<'APPLESCRIPT'
on run argv
  set projectRoot to item 1 of argv
  set quotedRoot to quoted form of projectRoot
  tell application "Terminal"
    activate
    do script "cd " & quotedRoot & " && ./FileMorph.command"
  end tell
end run
APPLESCRIPT
LAUNCHER

chmod +x "$EXECUTABLE"

echo "Created $APP_DIR"
