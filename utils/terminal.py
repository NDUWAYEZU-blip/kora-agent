"""
utils/terminal.py — Terminal helpers for the Kora bootstrap agent.

Two launch modes:
  1. launch_in_new_window()  — opens a VISIBLE Git Bash window (for backend /
                               frontend so the developer can see live output).
  2. run_managed()           — silent subprocess with output captured for
                               pattern-matching (used internally when needed).
"""

import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import config
from core.logger import get_logger

logger = get_logger("terminal")

# Windows process-creation flag — opens a new console window
_NEW_CONSOLE = 0x00000010  # CREATE_NEW_CONSOLE


# ── Visible window launcher ───────────────────────────────────────────────────

def launch_in_new_window(
    command: str,
    cwd: str,
    title: str = "Kora",
) -> Optional[subprocess.Popen]:
    """
    Open a new, visible Git Bash window and run `command` inside it.
    The window stays open after the command exits (exec bash at the end).
    Falls back to a plain cmd window if Git Bash is not found.

    Returns the Popen handle (the window process), or None on failure.
    """
    git_bash = config.GIT_BASH_PATH

    try:
        if Path(git_bash).exists():
            # Build:  bash --login -i -c 'cd "<cwd>" && <command>; exec bash'
            # exec bash keeps the window open so the developer can read output.
            bash_cmd = f'cd "{_posix(cwd)}" && {command}; exec bash'
            proc = subprocess.Popen(
                [git_bash, "--login", "-i", "-c", bash_cmd],
                creationflags=_NEW_CONSOLE,
            )
        else:
            # Fallback: cmd /k keeps the window open
            proc = subprocess.Popen(
                ["cmd", "/k", f'title {title} && cd /d "{cwd}" && {command}'],
                creationflags=_NEW_CONSOLE,
            )
        logger.debug(f"[{title}] Opened new terminal window (PID {proc.pid}).")
        return proc

    except FileNotFoundError as e:
        logger.error(f"[{title}] Could not open terminal: {e}")
        return None
    except Exception as e:
        logger.error(f"[{title}] Unexpected error opening terminal: {e}")
        return None


def _posix(path: str) -> str:
    """Convert Windows backslash path to forward-slash for bash."""
    return path.replace("\\", "/")


# ── Silent managed process (output captured) ──────────────────────────────────

def _stream_output(
    stream,
    log_fn: Callable[[str], None],
    stop_event: threading.Event,
):
    """Read lines from a stream and forward to log_fn until stop_event set."""
    try:
        for line in iter(stream.readline, ""):
            if stop_event.is_set():
                break
            stripped = line.rstrip("\n")
            if stripped:
                log_fn(stripped)
    except Exception:
        pass


class ManagedProcess:
    """
    Wraps a silent subprocess.  Streams stdout/stderr to the logger and
    exposes wait_for_pattern() for startup detection.
    """

    def __init__(self, name: str, proc: subprocess.Popen):
        self.name = name
        self.proc = proc
        self._lines: list[str] = []
        self._lock = threading.Lock()
        self._stop = threading.Event()

        def _capture(line: str):
            with self._lock:
                self._lines.append(line)
            logger.debug(f"[{self.name}] {line}")

        self._t_out = threading.Thread(
            target=_stream_output,
            args=(proc.stdout, _capture, self._stop),
            daemon=True,
        )
        self._t_err = threading.Thread(
            target=_stream_output,
            args=(proc.stderr, _capture, self._stop),
            daemon=True,
        )
        self._t_out.start()
        self._t_err.start()

    def wait_for_pattern(
        self,
        patterns: list[str],
        timeout: int = 60,
        poll: float = 1.0,
    ) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                for line in self._lines:
                    for pat in patterns:
                        if pat.lower() in line.lower():
                            return True
            if self.proc.poll() is not None:
                logger.error(
                    f"[{self.name}] process exited prematurely "
                    f"(returncode={self.proc.returncode})."
                )
                return False
            time.sleep(poll)
        return False

    def is_alive(self) -> bool:
        return self.proc.poll() is None

    def stop(self):
        self._stop.set()
        self.proc.terminate()


def run_managed(
    name: str,
    command: list[str],
    cwd: str,
    use_git_bash: bool = True,
) -> Optional[ManagedProcess]:
    """
    Launch `command` as a silent managed subprocess (output captured).
    Used when you need pattern-matching without a visible window.
    """
    try:
        if use_git_bash and Path(config.GIT_BASH_PATH).exists():
            cmd_str = " ".join(command)
            full_cmd = [config.GIT_BASH_PATH, "--login", "-i", "-c", cmd_str]
        else:
            full_cmd = command

        proc = subprocess.Popen(
            full_cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        return ManagedProcess(name, proc)
    except FileNotFoundError as e:
        logger.error(f"[{name}] Command not found: {e}")
        return None
    except Exception as e:
        logger.error(f"[{name}] Failed to start: {e}")
        return None
