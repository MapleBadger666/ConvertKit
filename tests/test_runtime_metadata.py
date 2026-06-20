from app import runtime_paths
from app.version import APP_NAME, APP_VERSION, BUILD_CHANNEL


def test_version_metadata_has_desktop_defaults():
    assert APP_NAME == "FileMorph"
    assert APP_VERSION
    assert BUILD_CHANNEL


def test_runtime_paths_expose_expected_directories():
    assert runtime_paths.UPLOAD_DIR.name == "uploads"
    assert runtime_paths.OUTPUT_DIR.name == "output"
    assert runtime_paths.LOG_DIR.name == "logs"
