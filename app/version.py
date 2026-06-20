from __future__ import annotations

import os


APP_NAME = "FileMorph"
APP_VERSION = os.environ.get("FILEMORPH_APP_VERSION", "0.7.0-dev")
BUILD_CHANNEL = os.environ.get("FILEMORPH_BUILD_CHANNEL", "local")
