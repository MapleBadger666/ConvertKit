from __future__ import annotations

import os
import sys
from pathlib import Path

from app.version import APP_NAME


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MACOS_APPLICATION_SUPPORT = Path.home() / "Library" / "Application Support" / APP_NAME
RUNTIME_MODE = os.environ.get("FILEMORPH_RUNTIME", "local").strip().lower()


def is_development_runtime() -> bool:
    return RUNTIME_MODE in {"dev", "development", "test"} or "pytest" in sys.modules


def default_data_root() -> Path:
    if is_development_runtime():
        return PROJECT_ROOT
    return MACOS_APPLICATION_SUPPORT


DATA_ROOT = Path(os.environ.get("FILEMORPH_DATA_DIR", default_data_root())).expanduser()
UPLOAD_DIR = DATA_ROOT / "uploads"
OUTPUT_DIR = DATA_ROOT / "output"
LOG_DIR = DATA_ROOT / "logs"
DESKTOP_LOG = LOG_DIR / "filemorph-desktop-ui.log"
LOCK_FILE = DATA_ROOT / "filemorph.lock"


def ensure_runtime_directories() -> None:
    for directory in (UPLOAD_DIR, OUTPUT_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
