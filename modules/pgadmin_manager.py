"""
modules/pgadmin_manager.py — Launch pgAdmin 4 and verify it is running.
MVP: process-existence check only (no computer vision / OCR).
"""

from pathlib import Path
import config
from core.logger import get_logger
from utils.process_utils import (
    is_process_running,
    launch_executable,
    wait_for_process,
)

logger = get_logger("pgadmin_manager")

_PGADMIN_PROCESS = "pgAdmin4.exe"


class PgAdminManager:

    def ensure_running(self) -> bool:
        if is_process_running(_PGADMIN_PROCESS):
            logger.info("pgAdmin is already running.")
            return True

        path = config.PGADMIN_PATH
        if not Path(path).exists():
            logger.warning(
                f"pgAdmin not found at: {path}\n"
                "  → Update PGADMIN_PATH in your .env  (non-critical, skipping)."
            )
            return False

        logger.info(f"Launching pgAdmin from: {path}")
        proc = launch_executable(path)
        if proc is None:
            return False

        logger.info(
            f"Waiting for pgAdmin process (up to "
            f"{config.PGADMIN_STARTUP_TIMEOUT}s)…"
        )
        found = wait_for_process(
            _PGADMIN_PROCESS,
            timeout=config.PGADMIN_STARTUP_TIMEOUT,
            poll=2.0,
        )
        if found:
            logger.info("pgAdmin is running.")
        else:
            logger.warning("pgAdmin process did not appear within timeout.")
        return found
