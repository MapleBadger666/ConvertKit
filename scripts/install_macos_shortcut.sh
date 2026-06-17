#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_PATH="$PROJECT_ROOT/dist/FileMorph.app"
SHORTCUT_PATH="$HOME/Desktop/FileMorph.app"

"$PROJECT_ROOT/scripts/build_macos_app.sh"

if [[ -L "$SHORTCUT_PATH" ]]; then
  rm "$SHORTCUT_PATH"
elif [[ -e "$SHORTCUT_PATH" ]]; then
  echo "A file already exists at $SHORTCUT_PATH."
  echo "Move or rename it, then run this script again."
  exit 1
fi

ln -s "$APP_PATH" "$SHORTCUT_PATH"
echo "Created desktop shortcut: $SHORTCUT_PATH"
