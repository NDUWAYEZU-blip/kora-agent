"""
modules/backend_manager.py — Start the FastAPI backend in a visible terminal.

Opens a new Git Bash window running:
    source .venv/Scripts/activate && uvicorn main:app --reload

Then polls port 8000 to confirm it is up.
"""

import time
from pathlib import Path

import config
from core.healthcheck import port_in_use, wait_for_port
from core.logger import get_logger
from utils.terminal import launch_in_new_window

logger = get_logger("backend_manager")


class BackendManager:

    def start(self) -> bool:
        port = config.BACKEND_PORT
        backend_path = config.BACKEND_PATH

        # ── Already running ───────────────────────────────────────────────
        if port_in_use(port):
            logger.info(f"Backend already reachable on port {port}.")
            return True

        # ── Validate directory ────────────────────────────────────────────
        if not Path(backend_path).exists():
            logger.error(
                f"Backend directory not found: {backend_path}\n"
                "  -> Update BACKEND_PATH in your .env"
            )
            return False

        # ── Build the bash command ────────────────────────────────────────
        venv_activate = self._find_venv_activate(backend_path)

        if venv_activate:
            # source activate then run uvicorn
            cmd = (
                f'source "{venv_activate}" && '
                f'uvicorn main:app --reload --host 0.0.0.0 --port {port}'
            )
        else:
            logger.warning(
                "No virtual environment found (.venv / venv / env). "
                "Running uvicorn globally."
            )
            cmd = f'uvicorn main:app --reload --host 0.0.0.0 --port {port}'

        logger.info(f"Opening backend terminal in: {backend_path}")
        logger.info(f"Command: {cmd}")

        proc = launch_in_new_window(
            command=cmd,
            cwd=backend_path,
            title="Kora Backend",
        )

        if proc is None:
            logger.error("Failed to open backend terminal window.")
            return False

        # ── Poll the port until uvicorn is up ────────────────────────────
        logger.info(
            f"Waiting for backend to become reachable on port {port} "
            f"(timeout={config.BACKEND_STARTUP_TIMEOUT}s)..."
        )
        ok = wait_for_port(
            "localhost", port,
            timeout=config.BACKEND_STARTUP_TIMEOUT,
            poll=2.0,
            label="Backend",
        )

        if ok:
            logger.info(f"Backend is active on port {port}.")
        else:
            logger.error(
                f"Backend did not become reachable within "
                f"{config.BACKEND_STARTUP_TIMEOUT}s.\n"
                "  -> Check the backend terminal window for errors."
            )
        return ok

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_venv_activate(self, base: str) -> str:
        """
        Search common venv locations and return the POSIX activate path
        (forward slashes, for Git Bash), or empty string if not found.
        """
        candidates = [
            Path(base) / ".venv"  / "Scripts" / "activate",
            Path(base) / "venv"   / "Scripts" / "activate",
            Path(base) / "env"    / "Scripts" / "activate",
        ]
        for p in candidates:
            if p.exists():
                return p.as_posix()
        return ""
