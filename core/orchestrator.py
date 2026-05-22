"""
core/orchestrator.py — Runs all bootstrap steps in order.
Each step is isolated; failures are logged and either fatal or skipped
depending on whether the service is critical.
"""

from core.logger import get_logger
from modules.docker_manager import DockerManager
from modules.redis_manager import RedisManager
from modules.pgadmin_manager import PgAdminManager
from modules.vscode_manager import VSCodeManager
from modules.backend_manager import BackendManager
from modules.frontend_manager import FrontendManager

logger = get_logger("orchestrator")


class Orchestrator:
    """Runs each bootstrap step and tracks overall success."""

    def __init__(self):
        self.docker = DockerManager()
        self.redis = RedisManager()
        self.pgadmin = PgAdminManager()
        self.vscode = VSCodeManager()
        self.backend = BackendManager()
        self.frontend = FrontendManager()

        self._results: dict[str, bool] = {}

    # ── Internal helpers ──────────────────────────────────────────────────

    def _step(self, name: str, fn, critical: bool = True) -> bool:
        """
        Execute a bootstrap step, capture result, log outcome.
        If `critical` is True and the step fails, run() will return False.
        """
        logger.info(f"── STEP: {name} ──")
        try:
            ok: bool = fn()
        except Exception as exc:
            logger.error(f"Unhandled exception in step [{name}]: {exc}", exc_info=True)
            ok = False

        self._results[name] = ok

        if ok:
            logger.info(f"[OK] {name}")
        else:
            if critical:
                logger.error(f"[FAIL] {name}  ← critical step failed")
            else:
                logger.warning(f"[SKIP] {name}  ← non-critical, continuing")
        return ok

    # ── Public entry point ────────────────────────────────────────────────

    def run(self) -> bool:
        """
        Execute all bootstrap steps in order.
        Returns True only when all critical steps succeed.
        """
        steps = [
            # (display name,          callable,               critical?)
            ("Docker Desktop",        self.docker.ensure_running,  True),
            ("Redis",                 self.redis.ensure_running,   True),
            ("pgAdmin",               self.pgadmin.ensure_running, False),
            ("VS Code",               self.vscode.ensure_running,  False),
            ("Backend (FastAPI)",     self.backend.start,          True),
            ("Frontend (Next.js)",    self.frontend.start,         True),
        ]

        for name, fn, critical in steps:
            ok = self._step(name, fn, critical)
            if not ok and critical:
                logger.error(
                    f"Critical step '{name}' failed — aborting bootstrap."
                )
                self._print_summary()
                return False

        self._print_summary()
        return all(
            ok for name, ok in self._results.items()
            if any(name == s[0] for s in steps if s[2])  # only critical
        )

    # ── Summary ───────────────────────────────────────────────────────────

    def _print_summary(self):
        logger.info("")
        logger.info("── STARTUP SUMMARY ──")
        for name, ok in self._results.items():
            status = "✓" if ok else "✗"
            logger.info(f"  {status}  {name}")
        logger.info("")
