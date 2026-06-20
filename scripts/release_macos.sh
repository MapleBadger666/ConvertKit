#!/bin/bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 v0.7.0-dev" >&2
  exit 1
fi

VERSION_TAG="$1"
if [[ ! "$VERSION_TAG" =~ ^v[0-9]+[.][0-9]+[.][0-9]+([-][A-Za-z0-9.]+)?$ ]]; then
  echo "Version must look like v0.7.0 or v0.7.0-dev" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
DMG_PATH="$DIST_DIR/FileMorph-macOS.dmg"
PKG_PATH="$DIST_DIR/FileMorph-Installer.pkg"

file_size() {
  stat -f%z "$1" 2>/dev/null || stat -c%s "$1"
}

check_asset_size() {
  local path="$1"
  local label="$2"

  if [[ ! -f "$path" ]]; then
    echo "Missing $label: $path" >&2
    exit 1
  fi

  local size
  size="$(file_size "$path")"
  echo "$label size: $size bytes"
}

cd "$PROJECT_ROOT"

echo "Running tests..."
if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  "$PROJECT_ROOT/.venv/bin/python" -m pytest -q
else
  pytest -q
fi

echo "Checking shell scripts..."
bash -n \
  "$PROJECT_ROOT/scripts/build_macos_app.sh" \
  "$PROJECT_ROOT/scripts/build_macos_dmg.sh" \
  "$PROJECT_ROOT/scripts/build_macos_pkg.sh" \
  "$PROJECT_ROOT/scripts/audit_macos_app_size.sh"

export FILEMORPH_VERSION="${VERSION_TAG#v}"

echo "Building DMG for $VERSION_TAG..."
"$PROJECT_ROOT/scripts/build_macos_dmg.sh"

echo "Building PKG for $VERSION_TAG..."
"$PROJECT_ROOT/scripts/build_macos_pkg.sh"

check_asset_size "$DMG_PATH" "DMG"
check_asset_size "$PKG_PATH" "PKG"

echo "Auditing app and installer size..."
"$PROJECT_ROOT/scripts/audit_macos_app_size.sh"

echo "SHA256 checksums:"
shasum -a 256 "$DMG_PATH" "$PKG_PATH"

echo
echo "GitHub Release upload suggestion:"
echo "gh release upload $VERSION_TAG \\"
echo "  dist/FileMorph-macOS.dmg \\"
echo "  dist/FileMorph-Installer.pkg \\"
echo "  --clobber"
echo
echo "This script does not commit, push, tag, or create GitHub Releases."
