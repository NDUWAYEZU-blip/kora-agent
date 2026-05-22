"""
config.py — Loads environment variables and provides typed config.
All paths and timeouts are sourced from .env or sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the agent root directory
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def _get_int(key: str, default: int = 30) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


# ── Paths ────────────────────────────────────────────────────────────────────
BACKEND_PATH: str = _get("BACKEND_PATH", r"C:\Projects\kora-backend")
FRONTEND_PATH: str = _get("FRONTEND_PATH", r"C:\Projects\kora-frontend")

VSCODE_PATH: str = _get(
    "VSCODE_PATH",
    r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
)
PGADMIN_PATH: str = _get(
    "PGADMIN_PATH",
    r"C:\Program Files\pgAdmin 4\runtime\pgAdmin4.exe",
)
GIT_BASH_PATH: str = _get(
    "GIT_BASH_PATH",
    r"C:\Program Files\Git\bin\bash.exe",
)
DOCKER_DESKTOP_PATH: str = _get(
    "DOCKER_DESKTOP_PATH",
    r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
)

# ── Timeouts (seconds) ───────────────────────────────────────────────────────
DOCKER_BOOT_TIMEOUT: int = _get_int("DOCKER_BOOT_TIMEOUT", 120)
DOCKER_POLL_INTERVAL: int = _get_int("DOCKER_POLL_INTERVAL", 5)

REDIS_PORT: int = _get_int("REDIS_PORT", 6379)
REDIS_IMAGE: str = _get("REDIS_IMAGE", "redis:7")
REDIS_CONTAINER_NAME: str = _get("REDIS_CONTAINER_NAME", "kora-redis")

BACKEND_PORT: int = _get_int("BACKEND_PORT", 8000)
BACKEND_STARTUP_TIMEOUT: int = _get_int("BACKEND_STARTUP_TIMEOUT", 60)

FRONTEND_PORT: int = _get_int("FRONTEND_PORT", 3000)
FRONTEND_STARTUP_TIMEOUT: int = _get_int("FRONTEND_STARTUP_TIMEOUT", 90)

PGADMIN_STARTUP_TIMEOUT: int = _get_int("PGADMIN_STARTUP_TIMEOUT", 30)

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR: str = _get("LOG_DIR", str(Path(__file__).parent / "logs"))
LOG_LEVEL: str = _get("LOG_LEVEL", "INFO")
