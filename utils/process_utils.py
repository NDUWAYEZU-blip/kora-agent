"""
utils/process_utils.py — Cross-process helpers (detection, killing, waiting).
"""

import subprocess
import time
from typing import Optional
import psutil
from core.logger import get_logger

logger = get_logger("process_utils")


def is_process_running(name: str) -> bool:
    """
    Return True if at least one process whose name contains `name`
    (case-insensitive) is currently running.
    """
    name_lower = name.lower()
    for proc in psutil.process_iter(["name"]):
        try:
            if name_lower in proc.info["name"].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def find_process_by_name(name: str) -> list[psutil.Process]:
    """Return all running processes whose name contains `name`."""
    matches = []
    name_lower = name.lower()
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if name_lower in proc.info["name"].lower():
                matches.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return matches


def wait_for_process(
    name: str,
    timeout: int = 30,
    poll: float = 2.0,
) -> bool:
    """
    Wait until a process named `name` appears or timeout expires.
    Returns True if found within the timeout.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_process_running(name):
            return True
        time.sleep(poll)
    return False


def launch_executable(
    path: str,
    args: Optional[list[str]] = None,
    shell: bool = False,
) -> Optional[subprocess.Popen]:
    """
    Launch an executable at `path` with optional args.
    Returns the Popen object on success, None on failure.
    """
    cmd = [path] + (args or [])
    try:
        proc = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.debug(f"Launched '{path}' with PID {proc.pid}.")
        return proc
    except FileNotFoundError:
        logger.error(f"Executable not found: {path}")
        return None
    except Exception as e:
        logger.error(f"Failed to launch '{path}': {e}")
        return None
