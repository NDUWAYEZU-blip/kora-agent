"""
core/logger.py — Structured logger with console + file output.
Provides coloured console output on Windows via colorama (optional).
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

try:
    import colorama
    colorama.init(autoreset=True)
    _COLORAMA = True
except ImportError:
    _COLORAMA = False

import config

# ── Colour codes ─────────────────────────────────────────────────────────────
_COLOURS = {
    "DEBUG":    "\033[36m",   # cyan
    "INFO":     "\033[32m",   # green
    "WARNING":  "\033[33m",   # yellow
    "ERROR":    "\033[31m",   # red
    "CRITICAL": "\033[35m",   # magenta
    "SUCCESS":  "\033[92m",   # bright green
    "RESET":    "\033[0m",
}

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


def _success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


logging.Logger.success = _success  # type: ignore[attr-defined]


class _ColouredFormatter(logging.Formatter):
    """Console formatter with ANSI colour codes."""

    def __init__(self):
        # Use standard % formatting — 'message' is populated by Formatter.format()
        super().__init__(fmt="[%(levelname)-8s] %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        use_colour = _COLORAMA or sys.stdout.isatty()
        colour = _COLOURS.get(record.levelname, "") if use_colour else ""
        reset  = _COLOURS["RESET"]                  if use_colour else ""
        # Let the parent build the fully-rendered string (fills in %(message)s)
        base = super().format(record)
        return f"{colour}{base}{reset}"


class _PlainFormatter(logging.Formatter):
    """File formatter without colour codes."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


# ── Public factory ────────────────────────────────────────────────────────────
_loggers: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, creating it once and caching it."""
    if name in _loggers:
        return _loggers[name]

    log = logging.getLogger(name)
    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    log.setLevel(level)
    log.propagate = False

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(_ColouredFormatter())
    log.addHandler(ch)

    # File handler
    log_dir = Path(config.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"kora_{datetime.now():%Y%m%d}.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_PlainFormatter())
    log.addHandler(fh)

    _loggers[name] = log
    return log
