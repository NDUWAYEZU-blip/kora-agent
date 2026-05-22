"""
core/healthcheck.py — Service health verification helpers.
"""

import socket
import subprocess
import time
from core.logger import get_logger

logger = get_logger("healthcheck")


def wait_for_port(
    host: str,
    port: int,
    timeout: int = 30,
    poll: float = 2.0,
    label: str = "",
) -> bool:
    """
    Poll host:port until it accepts a TCP connection or timeout expires.
    Returns True if the port opened within timeout, False otherwise.
    """
    label = label or f"{host}:{port}"
    deadline = time.time() + timeout
    attempt = 0

    while time.time() < deadline:
        attempt += 1
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info(f"[{label}] reachable after {attempt} attempt(s).")
                return True
        except (ConnectionRefusedError, OSError):
            remaining = int(deadline - time.time())
            logger.debug(
                f"[{label}] not ready yet (attempt {attempt}, "
                f"{remaining}s remaining)."
            )
            time.sleep(poll)

    logger.error(f"[{label}] did NOT become reachable within {timeout}s.")
    return False


def docker_is_ready(timeout: int = 5) -> bool:
    """
    Run `docker info` — returns True when the daemon responds successfully.
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def wait_for_docker(boot_timeout: int = 120, poll: int = 5) -> bool:
    """
    Poll `docker info` until Docker engine is ready or timeout expires.
    Returns True on success, False on timeout.
    """
    deadline = time.time() + boot_timeout
    attempt = 0

    logger.info("Waiting for Docker engine to become ready…")
    while time.time() < deadline:
        attempt += 1
        if docker_is_ready():
            logger.info(f"Docker engine ready after {attempt} poll(s).")
            return True
        remaining = int(deadline - time.time())
        logger.debug(
            f"Docker not ready yet (attempt {attempt}, {remaining}s left)."
        )
        time.sleep(poll)

    logger.error(f"Docker failed to initialise within {boot_timeout}s.")
    return False


def port_in_use(port: int, host: str = "localhost") -> bool:
    """Quick check: is the given port already bound?"""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (ConnectionRefusedError, OSError):
        return False
