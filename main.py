"""
Kora Local Dev Bootstrap Agent - MVP V1
Entry point: run `python main.py` or configure as `start-kora`
"""

import sys
import time
from core.orchestrator import Orchestrator
from core.logger import get_logger

logger = get_logger("main")


def main():
    logger.info("=" * 60)
    logger.info("  KORA DEV ENVIRONMENT BOOTSTRAP AGENT  ")
    logger.info("=" * 60)

    try:
        orchestrator = Orchestrator()
        success = orchestrator.run()

        if success:
            logger.info("=" * 60)
            logger.info("  ALL SERVICES STARTED SUCCESSFULLY  ")
            logger.info("  Kora dev environment is ready.     ")
            logger.info("=" * 60)
            sys.exit(0)
        else:
            logger.error("Bootstrap completed with errors. Check logs above.")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Bootstrap interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
