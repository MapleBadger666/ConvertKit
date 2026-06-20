#!/bin/bash

set -euo pipefail
export COPYFILE_DISABLE=1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
APP_NAME="FileMorph"
APP_PATH="$DIST_DIR/$APP_NAME.app"
PKG_PATH="$DIST_DIR/FileMorph-Installer.pkg"
IDENTIFIER="local.filemorph.desktop"
VERSION="${FILEMORPH_VERSION:-0.7.0}"
PKG_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/filemorph-pkg.XXXXXX")"

cleanup() {
  rm -rf "$PKG_ROOT"
}
trap cleanup EXIT

"$PROJECT_ROOT/scripts/build_macos_app.sh"

rm -f "$PKG_PATH"
find "$APP_PATH" -name "._*" -delete
mkdir -p "$PKG_ROOT/Applications"
ditto --norsrc --noextattr "$APP_PATH" "$PKG_ROOT/Applications/$APP_NAME.app"
find "$PKG_ROOT" -name "._*" -delete

pkgbuild \
  --root "$PKG_ROOT" \
  --install-location / \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  "$PKG_PATH"

echo "Created $PKG_PATH"
