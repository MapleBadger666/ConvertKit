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
PKG_VERSION="${VERSION%%-*}"
PKG_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/filemorph-pkg.XXXXXX")"
BUILD_PROFILE="${FILEMORPH_BUILD_PROFILE:-lite}"

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

cleanup() {
  rm -rf "$PKG_ROOT"
}
trap cleanup EXIT

"$PROJECT_ROOT/scripts/build_macos_app.sh" --profile "$BUILD_PROFILE"

rm -f "$PKG_PATH"
find "$APP_PATH" -name "._*" -delete
mkdir -p "$PKG_ROOT/Applications"
ditto --norsrc --noextattr "$APP_PATH" "$PKG_ROOT/Applications/$APP_NAME.app"
find "$PKG_ROOT" -name "._*" -delete

pkgbuild \
  --root "$PKG_ROOT" \
  --install-location / \
  --identifier "$IDENTIFIER" \
  --version "$PKG_VERSION" \
  "$PKG_PATH"

echo "Created $PKG_PATH"
