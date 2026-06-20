#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
DMG_PATH="$DIST_DIR/FileMorph-macOS.dmg"
PKG_PATH="$DIST_DIR/FileMorph-Installer.pkg"

file_size() {
  stat -f%z "$1" 2>/dev/null || stat -c%s "$1"
}

sha256_file() {
  shasum -a 256 "$1"
}

check_asset() {
  local path="$1"
  local label="$2"

  if [[ ! -f "$path" ]]; then
    echo "Missing $label: $path" >&2
    exit 1
  fi

  local size
  size="$(file_size "$path")"
  echo "$label size: $size bytes"
  echo "$label sha256:"
  sha256_file "$path"
}

cd "$PROJECT_ROOT"

check_asset "$DMG_PATH" "DMG"
check_asset "$PKG_PATH" "PKG"

if [[ -n "$(git ls-files dist .venv)" ]]; then
  echo "dist/ or .venv/ is tracked by Git; release artifacts must not be committed." >&2
  git ls-files dist .venv >&2
  exit 1
fi

browser_module="webbrowser"
browser_method="open"
new_window_call="open_""new"
new_tab_call="open_""new_tab"
forbidden_browser_pattern="${browser_module}[.]${browser_method}\|${new_window_call}\|${new_tab_call}"

if grep -R "$forbidden_browser_pattern" -n desktop scripts app; then
  echo "External browser launch call found in app startup path." >&2
  exit 1
fi

echo "Release asset verification passed."
