from __future__ import annotations

from src.core.config import load_config
from src.core.logger import get_logger, initialize_logging


def main() -> int:
    """Load configuration, initialize logging, log startup, and exit cleanly."""

    load_config()
    initialize_logging()
    logger = get_logger("src.app.main")
    logger.info("Startup OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
