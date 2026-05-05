"""Structured logging configuration."""

import logging
import sys

from app.config import settings


def setup_logging() -> logging.Logger:
    """Configure structured logging for the application."""
    logger = logging.getLogger("idx_trading")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add handler if not already present
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


logger = setup_logging()
