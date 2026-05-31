"""System helpers and subprocess wrappers (Windows + macOS)."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Sequence


class CommandError(RuntimeError):
    """Raised when a system command fails."""

    def __init__(self, args: Sequence[str], returncode: int, stderr: str | None = None):
        message = f"Command failed with exit code {returncode}: {' '.join(args)}"
        if stderr:
            message = f"{message}\n{stderr.strip()}"
        super().__init__(message)
        self.args_list = list(args)
        self.returncode = returncode
        self.stderr = stderr or ""


def is_windows() -> bool:
    return sys.platform.startswith("win")


def is_macos() -> bool:
    return sys.platform == "darwin"


def require_windows() -> None:
    if not is_windows():
        raise RuntimeError("Esta acao e suportada apenas no Windows.")


def is_admin() -> bool:
    if is_windows():
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
        except AttributeError:
            return False
    # On macOS/Linux check effective user id
    return os.geteuid() == 0


def run_command(
    args: Sequence[str],
    *,
    check: bool = True,
    capture_output: bool = False,
    text: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(args),
        check=False,
        capture_output=capture_output,
        text=text,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr if capture_output else None
        raise CommandError(args, completed.returncode, stderr)
    return completed


def run_powershell(script: str) -> subprocess.CompletedProcess[str]:
    require_windows()
    return run_command(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ]
    )


def open_path(target: str) -> None:
    if is_windows():
        os.startfile(target)  # type: ignore[attr-defined]
    elif is_macos():
        run_command(["open", target], check=False)
    else:
        run_command(["xdg-open", target], check=False)


def open_url(url: str) -> None:
    webbrowser.open(url)


def set_clipboard_text(text: str) -> None:
    if is_macos():
        proc = subprocess.run(["pbcopy"], input=text, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError("pbcopy falhou ao copiar para a area de transferencia.")
    elif is_windows():
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
    else:
        raise RuntimeError("set_clipboard_text nao suportado nesta plataforma.")


def get_local_ipv4() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        except OSError:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def service_config(service_name: str, startup_type: str) -> None:
    require_windows()
    mapping = {
        "automatic": "auto",
        "manual": "demand",
        "disabled": "disabled",
    }
    mode = mapping[startup_type.lower()]
    run_command(["sc", "config", service_name, f"start= {mode}"])


def service_start(service_name: str) -> None:
    require_windows()
    run_command(["sc", "start", service_name], check=False)


def startup_manual(service_name: str) -> None:
    service_config(service_name, "manual")


def startup_automatic(service_name: str) -> None:
    service_config(service_name, "automatic")
