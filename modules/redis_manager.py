"""
modules/redis_manager.py — Ensure Redis is running in Docker.

Handles three scenarios:
  1. Redis already reachable on the configured port → nothing to do.
  2. A stopped container named REDIS_CONTAINER_NAME exists → start it.
  3. No container exists → run a fresh one.
"""

import subprocess
import config
from core.healthcheck import wait_for_port, port_in_use
from core.logger import get_logger

logger = get_logger("redis_manager")


def _docker_run(args: list[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker"] + args,
        capture_output=True,
        text=True,
        check=check,
    )


class RedisManager:

    def ensure_running(self) -> bool:
        port = config.REDIS_PORT
        name = config.REDIS_CONTAINER_NAME

        # ── Case 1: Redis already reachable ──────────────────────────────
        if port_in_use(port):
            logger.info(f"Redis already reachable on port {port}.")
            return True

        # ── Case 2: Stopped container exists ────────────────────────────
        container_state = self._get_container_state(name)

        if container_state == "running":
            logger.info(f"Redis container '{name}' is running — waiting for port…")
            return wait_for_port("localhost", port, timeout=15, label="Redis")

        if container_state == "exited":
            logger.info(f"Starting existing stopped Redis container '{name}'…")
            result = _docker_run(["start", name])
            if result.returncode != 0:
                logger.error(
                    f"Failed to start container '{name}': {result.stderr.strip()}"
                )
                return False
            return wait_for_port("localhost", port, timeout=20, label="Redis")

        # ── Case 3: No container → run fresh ────────────────────────────
        if container_state == "not_found":
            return self._run_fresh(name, port)

        # Unknown state
        logger.error(f"Unknown Redis container state: '{container_state}'")
        return False

    # ── Private ───────────────────────────────────────────────────────────

    def _get_container_state(self, name: str) -> str:
        """Return 'running', 'exited', or 'not_found'."""
        result = _docker_run(
            ["inspect", "--format", "{{.State.Status}}", name]
        )
        if result.returncode != 0:
            return "not_found"
        state = result.stdout.strip()
        if state == "running":
            return "running"
        return "exited"

    def _run_fresh(self, name: str, port: int) -> bool:
        image = config.REDIS_IMAGE
        logger.info(
            f"No Redis container found — starting fresh: "
            f"docker run -d --name {name} -p {port}:6379 {image}"
        )
        result = _docker_run(
            [
                "run", "-d",
                "--name", name,
                "-p", f"{port}:6379",
                "--restart", "unless-stopped",
                image,
            ]
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            # Guard: another process bound the port between our check and run
            if "port is already allocated" in err or "address already in use" in err:
                logger.warning(
                    f"Port {port} claimed by another process — "
                    "checking if Redis is still reachable…"
                )
                return port_in_use(port)
            logger.error(f"Failed to start Redis container: {err}")
            return False

        logger.info("Redis container started — waiting for connectivity…")
        return wait_for_port("localhost", port, timeout=20, label="Redis")
