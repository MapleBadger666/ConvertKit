#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILT_APP="$PROJECT_ROOT/dist/FileMorph.app"
APPLICATIONS_APP="/Applications/FileMorph.app"

"$PROJECT_ROOT/scripts/build_macos_app.sh"

if [[ -e "$APPLICATIONS_APP" || -L "$APPLICATIONS_APP" ]]; then
  BACKUP_APP="/Applications/FileMorph.app.backup.$(date +%Y%m%d%H%M%S)"
  mv "$APPLICATIONS_APP" "$BACKUP_APP"
  echo "Moved existing FileMorph app to $BACKUP_APP"
fi

cp -R "$BUILT_APP" "$APPLICATIONS_APP"

echo "Installed FileMorph to $APPLICATIONS_APP"
