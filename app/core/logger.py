import logging
import os
from logging.handlers import RotatingFileHandler


def _get_log_level() -> int:
    """Resolve log level from env var LOG_LEVEL (default INFO)."""
    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_str, logging.INFO)


def setup_logger(name: str = "open_insurance_agent") -> logging.Logger:
    """
    Create a production-friendly logger.

    - Level controlled by LOG_LEVEL (default: INFO)
    - Optional file rotation via LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT
    - Console handler always enabled
    - No propagation to root (prevents duplicate logs with Uvicorn/Gunicorn)
    - Configurable format via LOG_FORMAT and LOG_DATEFMT
    """
    logger = logging.getLogger(name)

    # Prevent adding handlers twice (e.g., app reloads)
    if logger.handlers:
        return logger

    log_level = _get_log_level()
    logger.setLevel(log_level)

    fmt = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s %(levelname)s [%(name)s:%(module)s:%(lineno)d] %(message)s",
    )
    datefmt = os.getenv("LOG_DATEFMT", "%Y-%m-%d %H:%M:%S")
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optional: rotating file handler
    log_file = os.getenv("LOG_FILE")
    if log_file:
        max_bytes = int(os.getenv("LOG_MAX_BYTES", "5242880"))  # 5 MB
        backup_count = int(os.getenv("LOG_BACKUP_COUNT", "3"))
        fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # Avoid duplicate logs when parent/root also has handlers (e.g., Uvicorn)
    logger.propagate = False
    return logger


# Shared application logger
logger = setup_logger()
