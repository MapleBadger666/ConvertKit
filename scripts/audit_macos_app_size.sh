#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
APP_PATH="$DIST_DIR/FileMorph.app"
BUNDLE_ROOT="$APP_PATH/Contents/Resources/FileMorph"
SOURCE_PATH="$BUNDLE_ROOT/source"
VENV_PATH="$BUNDLE_ROOT/.venv"
PROFILE_PATH="$BUNDLE_ROOT/build-profile.txt"
DMG_PATH="$DIST_DIR/FileMorph-macOS.dmg"
PKG_PATH="$DIST_DIR/FileMorph-Installer.pkg"
AUDIT_DIR="$PROJECT_ROOT/audits"
REPORT_PATH="$AUDIT_DIR/APP_SIZE_AUDIT_STAGE4.md"

size_or_missing() {
  local path="$1"
  if [[ -e "$path" ]]; then
    du -sh "$path" | awk '{print $1}'
  else
    echo "missing"
  fi
}

top_bundle_entries() {
  du -ah "$APP_PATH" | sort -hr | sed -n '1,20p'
}

top_bundle_files() {
  find "$APP_PATH" -type f -print0 | xargs -0 du -h | sort -hr | sed -n '1,20p'
}

bytes_or_zero() {
  local path="$1"
  if [[ -e "$path" ]]; then
    du -sk "$path" | awk '{print $1 * 1024}'
  else
    echo "0"
  fi
}

current_profile() {
  if [[ -f "$PROFILE_PATH" ]]; then
    tr -d '\n' < "$PROFILE_PATH"
  else
    echo "${FILEMORPH_BUILD_PROFILE:-unknown}"
  fi
}

write_report() {
  mkdir -p "$AUDIT_DIR"
  {
    echo "# FileMorph Stage 4.1 App Size Audit"
    echo
    echo "Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo
    echo "Current profile: $(current_profile)"
    echo
    echo "## Baseline Before Stage 4"
    echo
    echo "| Artifact | Size |"
    echo "| --- | ---: |"
    echo "| dist/FileMorph.app | 701M |"
    echo "| dist/FileMorph.app/Contents/Resources/FileMorph | 701M |"
    echo "| dist/FileMorph.app/Contents/Resources/FileMorph/source | 1.2M |"
    echo "| dist/FileMorph.app/Contents/Resources/FileMorph/.venv | 699M |"
    echo "| dist/FileMorph-macOS.dmg | 295M |"
    echo "| dist/FileMorph-Installer.pkg | 216M |"
    echo
    echo "## Stage 4 Full Runtime Baseline"
    echo
    echo "| Artifact | Size |"
    echo "| --- | ---: |"
    echo "| dist/FileMorph.app | 610M |"
    echo "| dist/FileMorph.app/Contents/Resources/FileMorph/.venv | 610M |"
    echo "| dist/FileMorph-macOS.dmg | 261M |"
    echo "| dist/FileMorph-Installer.pkg | 195M |"
    echo
    echo "## Current Build"
    echo
    echo "| Artifact | Size | Bytes |"
    echo "| --- | ---: | ---: |"
    echo "| dist/FileMorph.app | $(size_or_missing "$APP_PATH") | $(bytes_or_zero "$APP_PATH") |"
    echo "| dist/FileMorph.app/Contents/Resources/FileMorph | $(size_or_missing "$BUNDLE_ROOT") | $(bytes_or_zero "$BUNDLE_ROOT") |"
    echo "| dist/FileMorph.app/Contents/Resources/FileMorph/source | $(size_or_missing "$SOURCE_PATH") | $(bytes_or_zero "$SOURCE_PATH") |"
    echo "| dist/FileMorph.app/Contents/Resources/FileMorph/.venv | $(size_or_missing "$VENV_PATH") | $(bytes_or_zero "$VENV_PATH") |"
    echo "| dist/FileMorph-macOS.dmg | $(size_or_missing "$DMG_PATH") | $(bytes_or_zero "$DMG_PATH") |"
    echo "| dist/FileMorph-Installer.pkg | $(size_or_missing "$PKG_PATH") | $(bytes_or_zero "$PKG_PATH") |"
    echo
    echo "## Largest Files And Directories"
    echo
    if [[ -d "$APP_PATH" ]]; then
      echo '```text'
      top_bundle_entries
      echo '```'
    else
      echo "dist/FileMorph.app is missing. Build the macOS app before auditing bundle contents."
    fi
    echo
    echo "## Largest Files"
    echo
    if [[ -d "$APP_PATH" ]]; then
      echo '```text'
      top_bundle_files
      echo '```'
    else
      echo "dist/FileMorph.app is missing. Build the macOS app before auditing files."
    fi
    echo
    echo "## Notes"
    echo
    echo "- Stage 4.1 optimizes only the packaged app contents under dist/FileMorph.app."
    echo "- Repository source folders such as tests/, docs/, and audits/ are not deleted."
    echo "- dist/, .venv/, uploads/, output/, logs/, .dmg, and .pkg artifacts remain untracked release/build outputs."
  } > "$REPORT_PATH"
}

write_report
cat "$REPORT_PATH"
