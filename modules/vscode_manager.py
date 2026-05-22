"""
modules/vscode_manager.py — Launch VS Code and open the Kora workspace.
"""

from pathlib import Path
import config
from core.logger import get_logger
from utils.process_utils import (
    is_process_running,
    launch_executable,
    wait_for_process,
)

logger = get_logger("vscode_manager")

_CODE_PROCESS = "Code.exe"


class VSCodeManager:

    def ensure_running(self) -> bool:
        path = config.VSCODE_PATH

        if not Path(path).exists():
            # Try the `code` command from PATH (portable / scoop installs)
            if self._launch_from_path():
                return True
            logger.warning(
                f"VS Code not found at: {path}\n"
                "  → Update VSCODE_PATH in your .env  (non-critical, skipping)."
            )
            return False

        if is_process_running(_CODE_PROCESS):
            logger.info("VS Code is already running.")
            # Still try to open the workspace folder in the existing instance
            self._open_workspace(path)
            return True

        logger.info(f"Launching VS Code from: {path}")
        backend = config.BACKEND_PATH
        self._open_workspace(path, folder=backend)

        found = wait_for_process(_CODE_PROCESS, timeout=20, poll=2.0)
        if found:
            logger.info("VS Code is running.")
        else:
            logger.warning("VS Code process did not appear within 20 s.")
        return found

    # ── Private ───────────────────────────────────────────────────────────

    def _open_workspace(self, exe: str, folder: str = "") -> None:
        args = []
        if folder and Path(folder).exists():
            args.append(folder)
        launch_executable(exe, args=args)

    def _launch_from_path(self) -> bool:
        """Try launching VS Code via the `code` command available on PATH."""
        import subprocess
        folder = config.BACKEND_PATH
        try:
            cmd = ["code"]
            if folder and Path(folder).exists():
                cmd.append(folder)
            subprocess.Popen(cmd, shell=True)
            found = wait_for_process(_CODE_PROCESS, timeout=20, poll=2.0)
            return found
        except Exception:
            return False
