"""
utils/paths.py — Path resolution helpers for Windows environments.
"""

import os
from pathlib import Path


def resolve_path(raw: str) -> str:
    """
    Expand environment variables and ~ in a path string, then normalise.
    Example: %APPDATA%\\..\\Local\\Programs\\...  → C:\\Users\\John\\...
    """
    expanded = os.path.expandvars(os.path.expanduser(raw))
    return str(Path(expanded))


def path_exists(raw: str) -> bool:
    return Path(resolve_path(raw)).exists()


def ensure_dir(raw: str) -> Path:
    p = Path(resolve_path(raw))
    p.mkdir(parents=True, exist_ok=True)
    return p
