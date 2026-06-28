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
COMPONENT_PLIST="$(mktemp "${TMPDIR:-/tmp}/filemorph-components.XXXXXX")"
EXPANDED_PKG="$(mktemp -d "${TMPDIR:-/tmp}/filemorph-pkg-expanded.XXXXXX")"
PAYLOAD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/filemorph-payload.XXXXXX")"
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
  rm -rf "$EXPANDED_PKG"
  rm -rf "$PAYLOAD_ROOT"
  rm -f "$COMPONENT_PLIST"
}
trap cleanup EXIT

clean_metadata() {
  local path="$1"
  find "$path" -name "._*" -delete
  find "$path" -name ".DS_Store" -delete
  if command -v dot_clean >/dev/null 2>&1; then
    dot_clean -m "$path" || true
  fi
  if command -v xattr >/dev/null 2>&1; then
    xattr -cr "$path" || true
  fi
  find "$path" -name "._*" -delete
  find "$path" -name ".DS_Store" -delete
}

prepare_component_plist() {
  pkgbuild --analyze --root "$PKG_ROOT" "$COMPONENT_PLIST"
  if command -v /usr/libexec/PlistBuddy >/dev/null 2>&1; then
    /usr/libexec/PlistBuddy -c "Set :0:BundleIsRelocatable false" "$COMPONENT_PLIST"
    /usr/libexec/PlistBuddy -c "Set :0:BundleOverwriteAction upgrade" "$COMPONENT_PLIST"
  fi
}

assert_no_appledouble_files() {
  local path="$1"
  local appledouble
  appledouble="$(find "$path" -name "._*" -print)"
  if [[ -n "$appledouble" ]]; then
    echo "AppleDouble metadata files remain in $path:" >&2
    echo "$appledouble" >&2
    exit 1
  fi
}

assert_clean_pkg_payload() {
  local payload_files
  local payload_matches
  if ! payload_files="$(pkgutil --payload-files "$PKG_PATH")"; then
    echo "Unable to inspect PKG payload for AppleDouble metadata." >&2
    exit 1
  fi
  payload_matches="$(printf "%s\n" "$payload_files" | grep -E '(^|/)\._' || true)"
  if [[ -n "$payload_matches" ]]; then
    echo "AppleDouble metadata files found in PKG payload:" >&2
    echo "$payload_matches" >&2
    exit 1
  fi
}

repack_without_appledouble() {
  local cleaned_pkg
  cleaned_pkg="$PKG_PATH.cleaned"

  rm -rf "$EXPANDED_PKG"
  rm -rf "$PAYLOAD_ROOT"
  mkdir -p "$PAYLOAD_ROOT"
  pkgutil --expand "$PKG_PATH" "$EXPANDED_PKG"

  (
    cd "$PAYLOAD_ROOT"
    gzip -dc "$EXPANDED_PKG/Payload" | cpio -idm
  ) >/dev/null

  clean_metadata "$PAYLOAD_ROOT"
  assert_no_appledouble_files "$PAYLOAD_ROOT"
  mkbom "$PAYLOAD_ROOT" "$EXPANDED_PKG/Bom"

  (
    cd "$PAYLOAD_ROOT"
    find . -print | LC_ALL=C sort | cpio -o -H odc | gzip -c -n > "$EXPANDED_PKG/Payload"
  ) >/dev/null

  rm -f "$cleaned_pkg"
  pkgutil --flatten "$EXPANDED_PKG" "$cleaned_pkg"
  mv "$cleaned_pkg" "$PKG_PATH"
}

assert_lite_pkg_payload() {
  if [[ "$BUILD_PROFILE" != "lite" ]]; then
    return
  fi

  local payload_files
  local heavy_matches
  if ! payload_files="$(pkgutil --payload-files "$PKG_PATH")"; then
    echo "Unable to inspect PKG payload for lite dependency validation." >&2
    exit 1
  fi
  heavy_matches="$(printf "%s\n" "$payload_files" |
    grep -Ei 'onnxruntime|pymupdf|cv2|faster_whisper|tokenizers|hf_xet|/av/' || true
  )"
  if [[ -n "$heavy_matches" ]]; then
    echo "Optional heavy dependencies found in lite PKG payload:" >&2
    echo "$heavy_matches" >&2
    exit 1
  fi
}

"$PROJECT_ROOT/scripts/build_macos_app.sh" --profile "$BUILD_PROFILE"

rm -f "$PKG_PATH"
clean_metadata "$APP_PATH"
mkdir -p "$PKG_ROOT/Applications"
ditto --norsrc --noextattr "$APP_PATH" "$PKG_ROOT/Applications/$APP_NAME.app"
clean_metadata "$PKG_ROOT"
prepare_component_plist
clean_metadata "$PKG_ROOT"
assert_no_appledouble_files "$PKG_ROOT"

pkgbuild \
  --root "$PKG_ROOT" \
  --component-plist "$COMPONENT_PLIST" \
  --install-location / \
  --identifier "$IDENTIFIER" \
  --version "$PKG_VERSION" \
  "$PKG_PATH"

if pkgutil --payload-files "$PKG_PATH" | grep -E '(^|/)\._' >/dev/null 2>&1; then
  echo "PKG payload contains AppleDouble metadata after pkgbuild; repacking clean payload"
  repack_without_appledouble
fi

assert_clean_pkg_payload
assert_lite_pkg_payload

echo "Created $PKG_PATH"
