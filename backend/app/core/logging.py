"""
Logging configuration for the application
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   If None, uses LOG_LEVEL from settings
        log_file: Path to log file. If None, uses LOG_FILE from settings or defaults to logs/app.log
    """
    # Get log level from parameter or settings
    level = log_level or getattr(settings, "LOG_LEVEL", "INFO")
    log_level_num = getattr(logging, level.upper(), logging.INFO)

    # Get log file path
    if log_file is None:
        log_file = getattr(settings, "LOG_FILE", "logs/app.log")

    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(log_level_num)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (always add)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_num)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file is specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level_num)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Log that logging is configured
    logger.info(f"Logging configured with level: {level}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
