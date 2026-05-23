"""
modules/frontend_manager.py — Start the Next.js frontend in a visible terminal.

Opens a new Git Bash window running:
    npm run dev

Then polls port 3000 to confirm it is up.
"""

import time
from pathlib import Path

import config
from core.healthcheck import port_in_use, wait_for_port
from core.logger import get_logger
from utils.terminal import launch_in_new_window

logger = get_logger("frontend_manager")


class FrontendManager:

    def start(self) -> bool:
        port = config.FRONTEND_PORT
        frontend_path = config.FRONTEND_PATH

        # ── Already running ───────────────────────────────────────────────
        if port_in_use(port):
            logger.info(f"Frontend already reachable on port {port}.")
            return True

        # ── Validate directory ────────────────────────────────────────────
        if not Path(frontend_path).exists():
            logger.error(
                f"Frontend directory not found: {frontend_path}\n"
                "  -> Update FRONTEND_PATH in your .env"
            )
            return False

        # ── Warn if node_modules missing ──────────────────────────────────
        if not (Path(frontend_path) / "node_modules").exists():
            logger.warning(
                "node_modules not found in frontend directory.\n"
                "  -> Run 'npm install' inside your frontend folder first.\n"
                "  Attempting to start anyway..."
            )

        logger.info(f"Opening frontend terminal in: {frontend_path}")

        proc = launch_in_new_window(
            command="npm run dev",
            cwd=frontend_path,
            title="Kora Frontend",
        )

        if proc is None:
            logger.error("Failed to open frontend terminal window.")
            return False

        # ── Give Git Bash + Next.js time to initialise ────────────────────
        logger.info("Giving the terminal 10s to initialise...")
        time.sleep(10)

        # ── Poll the port until Next.js is up ────────────────────────────
        logger.info(
            f"Waiting for Next.js to become reachable on port {port} "
            f"(timeout={config.FRONTEND_STARTUP_TIMEOUT}s)..."
        )
        ok = wait_for_port(
            "localhost", port,
            timeout=config.FRONTEND_STARTUP_TIMEOUT,
            poll=3.0,
            label="Frontend",
        )

        if ok:
            logger.info(f"Frontend is active on port {port}.")
        else:
            logger.error(
                f"Frontend did not become reachable within "
                f"{config.FRONTEND_STARTUP_TIMEOUT}s.\n"
                "  -> Check the frontend terminal window for errors."
            )
        return ok
