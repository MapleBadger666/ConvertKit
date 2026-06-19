#!/bin/bash

set -euo pipefail
export COPYFILE_DISABLE=1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
APP_NAME="FileMorph"
APP_PATH="$DIST_DIR/$APP_NAME.app"
DMG_PATH="$DIST_DIR/FileMorph-macOS.dmg"
VOLUME_NAME="FileMorph"
DMG_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/filemorph-dmg.XXXXXX")"

cleanup() {
  rm -rf "$DMG_ROOT"
}
trap cleanup EXIT

"$PROJECT_ROOT/scripts/build_macos_app.sh"

rm -f "$DMG_PATH"
mkdir -p "$DMG_ROOT"
ditto --norsrc --noextattr "$APP_PATH" "$DMG_ROOT/$APP_NAME.app"
ln -s /Applications "$DMG_ROOT/Applications"
find "$DMG_ROOT" -name "._*" -delete

hdiutil create \
  -volname "$VOLUME_NAME" \
  -srcfolder "$DMG_ROOT" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

echo "Created $DMG_PATH"
