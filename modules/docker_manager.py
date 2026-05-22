"""
modules/docker_manager.py — Ensure Docker Desktop is running and ready.
"""

from pathlib import Path
import config
from core.healthcheck import docker_is_ready, wait_for_docker
from core.logger import get_logger
from utils.process_utils import is_process_running, launch_executable, wait_for_process

logger = get_logger("docker_manager")

# Process name as it appears in Task Manager on Windows
_DOCKER_PROCESS = "Docker Desktop.exe"


class DockerManager:
    """Handles detection, launch, and readiness polling of Docker Desktop."""

    def ensure_running(self) -> bool:
        """
        Main entry point for the orchestrator.
        Returns True when Docker engine is fully ready.
        """
        if docker_is_ready():
            logger.info("Docker Desktop already running and engine ready.")
            return True

        logger.info("Docker Desktop not ready — attempting to start…")

        if not is_process_running(_DOCKER_PROCESS):
            if not self._launch():
                return False

        # Wait for the Docker engine to be responsive
        return wait_for_docker(
            boot_timeout=config.DOCKER_BOOT_TIMEOUT,
            poll=config.DOCKER_POLL_INTERVAL,
        )

    # ── Private helpers ───────────────────────────────────────────────────

    def _launch(self) -> bool:
        docker_path = config.DOCKER_DESKTOP_PATH

        if not Path(docker_path).exists():
            logger.error(
                f"Docker Desktop not found at: {docker_path}\n"
                "  → Update DOCKER_DESKTOP_PATH in your .env file."
            )
            return False

        logger.info(f"Launching Docker Desktop from: {docker_path}")
        proc = launch_executable(docker_path)
        if proc is None:
            logger.error("Failed to launch Docker Desktop.")
            return False

        # Wait until the process actually appears before polling the engine
        logger.info("Waiting for Docker Desktop process to start…")
        appeared = wait_for_process(_DOCKER_PROCESS, timeout=30, poll=2.0)
        if not appeared:
            logger.warning(
                "Docker Desktop process did not appear within 30 s "
                "— continuing anyway."
            )
        return True
