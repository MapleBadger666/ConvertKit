from __future__ import annotations

import contextlib
import fcntl
import os
import signal
import socket
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_DATA_DIR = Path.home() / "Library" / "Application Support" / "FileMorph"
os.environ.setdefault("FILEMORPH_DATA_DIR", str(DEFAULT_DATA_DIR))
os.environ.setdefault("FILEMORPH_RUNTIME", "local")

DATA_DIR = Path(os.environ["FILEMORPH_DATA_DIR"])
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DESKTOP_LOG = LOG_DIR / "filemorph-desktop-ui.log"
LOCK_FILE = DATA_DIR / "filemorph.lock"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STREAMLIT_ENTRY = PROJECT_ROOT / "app" / "main.py"
ACTIVE_PROCESS: subprocess.Popen | None = None
SHUTTING_DOWN = False
LOCK_HANDLE = None
WATCHDOG_CODE = r"""
import os
import signal
import sys
import time

parent_pid = int(sys.argv[1])
streamlit_pgid = int(sys.argv[2])
log_path = sys.argv[3]


def log(message):
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


while True:
    if not pid_alive(streamlit_pgid):
        raise SystemExit(0)

    if not pid_alive(parent_pid):
        log(f"Watchdog stopping Streamlit process group {streamlit_pgid}")
        try:
            os.killpg(streamlit_pgid, signal.SIGTERM)
            time.sleep(2)
            if pid_alive(streamlit_pgid):
                os.killpg(streamlit_pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        raise SystemExit(0)

    time.sleep(1)
"""


def log_event(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with DESKTOP_LOG.open("a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {message}\n")


def acquire_single_instance_lock():
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock_handle = LOCK_FILE.open("w", encoding="utf-8")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        lock_handle.close()
        raise RuntimeError(
            "FileMorph is already running. "
            "Bring the existing FileMorph window to the front, or quit it before opening a new one."
        ) from exc

    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(str(os.getpid()))
    lock_handle.flush()
    log_event(f"Acquired single-instance lock at {LOCK_FILE}")
    return lock_handle


def find_available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_streamlit(url: str, process: subprocess.Popen, timeout: float = 45.0) -> None:
    deadline = time.monotonic() + timeout
    health_url = f"{url}/_stcore/health"
    last_error = ""

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Streamlit exited early with code {process.returncode}.")

        try:
            with urllib.request.urlopen(health_url, timeout=1.5) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)

        time.sleep(0.35)

    raise TimeoutError(f"Timed out waiting for FileMorph to start. {last_error}")


def start_streamlit(port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env.update(
        {
            "FILEMORPH_DATA_DIR": str(DATA_DIR),
            "FILEMORPH_RUNTIME": "local",
            "STREAMLIT_SERVER_HEADLESS": "true",
            "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:"
            + env.get("PATH", ""),
        }
    )
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(STREAMLIT_ENTRY),
        "--server.address",
        "127.0.0.1",
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    log_event(f"Starting Streamlit: {' '.join(command)}")
    return subprocess.Popen(
        command,
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def start_streamlit_watchdog(process: subprocess.Popen) -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable,
            "-c",
            WATCHDOG_CODE,
            str(os.getpid()),
            str(process.pid),
            str(DESKTOP_LOG),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def stop_streamlit(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return

    log_event("Stopping Streamlit")
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGTERM)

    try:
        process.wait(timeout=6)
    except subprocess.TimeoutExpired:
        log_event("Streamlit did not stop in time; killing it")
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=3)


def handle_shutdown_signal(signum: int, _frame: object) -> None:
    global SHUTTING_DOWN
    if SHUTTING_DOWN:
        raise SystemExit(0)

    SHUTTING_DOWN = True
    log_event(f"Received signal {signum}; stopping FileMorph")
    stop_streamlit(ACTIVE_PROCESS)
    raise SystemExit(0)


def install_shutdown_handlers() -> None:
    for signal_name in ("SIGINT", "SIGTERM", "SIGHUP"):
        if hasattr(signal, signal_name):
            signal.signal(getattr(signal, signal_name), handle_shutdown_signal)


def show_error(message: str) -> None:
    log_event(message)
    with contextlib.suppress(Exception):
        import tkinter.messagebox

        tkinter.messagebox.showerror("FileMorph", message)


def open_in_webview(url: str) -> None:
    import webview

    log_event(f"Opening FileMorph WebView at {url}")
    window = webview.create_window("FileMorph", url, width=1180, height=820, min_size=(920, 640))
    window.events.closed += lambda: stop_streamlit(ACTIVE_PROCESS)
    webview.start()


def main() -> int:
    global ACTIVE_PROCESS, LOCK_HANDLE
    process: subprocess.Popen | None = None
    try:
        install_shutdown_handlers()
        try:
            import webview  # noqa: F401
        except Exception as exc:
            raise RuntimeError(
                "The bundled WebView runtime is missing or unusable. "
                "Rebuild FileMorph.app after installing requirements-desktop.txt."
            ) from exc

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "uploads").mkdir(exist_ok=True)
        (DATA_DIR / "output").mkdir(exist_ok=True)
        log_event(f"FileMorph log path: {DESKTOP_LOG}")
        LOCK_HANDLE = acquire_single_instance_lock()

        port = find_available_port()
        url = f"http://127.0.0.1:{port}"
        process = start_streamlit(port)
        ACTIVE_PROCESS = process
        start_streamlit_watchdog(process)
        wait_for_streamlit(url, process)
        log_event(f"FileMorph ready at {url}")
        open_in_webview(url)

        return 0
    except Exception as exc:
        log_event(traceback.format_exc())
        show_error(
            "FileMorph could not start. "
            f"Details were written to {DESKTOP_LOG}. Error: {exc}"
        )
        return 1
    finally:
        stop_streamlit(process)
        ACTIVE_PROCESS = None
        if LOCK_HANDLE is not None:
            with contextlib.suppress(Exception):
                fcntl.flock(LOCK_HANDLE, fcntl.LOCK_UN)
                LOCK_HANDLE.close()
            LOCK_HANDLE = None
        log_event("FileMorph desktop launcher exited")


if __name__ == "__main__":
    raise SystemExit(main())
