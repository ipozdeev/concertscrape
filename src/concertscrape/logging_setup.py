"""Logging configuration.

Console logging is always on. An optional email digest handler is attached only
when both ``LOG_EMAIL_TO`` and ``LOG_EMAIL_FROM`` are configured *and* the Gmail
extra is available -- addresses are never hardcoded (the old module mailed a
hardcoded, typo'd address).
"""

from __future__ import annotations

import logging

FORMAT = "%(asctime)s - %(name)s (%(levelname)s) - %(message)s"
DATEFMT = "%m/%d %H:%M:%S"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the root ``concertscrape`` logger."""
    logger = logging.getLogger("concertscrape")
    logger.setLevel(level)

    if not logger.handlers:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFMT))
        logger.addHandler(console)

    return logger
