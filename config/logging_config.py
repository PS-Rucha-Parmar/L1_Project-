"""
config/logging_config.py
------------------------
Centralised logging configuration for the DocAi RAG system.

Purpose       : Configure Python's standard logging so every module shares the
                same structured format, outputs to both the console and a
                rotating log file, and respects the log level set in .env.
Dependencies  : logging (stdlib), config.settings
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: Path | None = None, log_level: str = "INFO") -> None:
    """
    Configure root logger with console + rotating file handlers.

    Args:
        log_dir   : Directory where ``app.log`` will be written.
                    Defaults to the value from settings if None.
        log_level : Logging verbosity as a string (e.g. ``"DEBUG"``).
    """
    # ------------------------------------------------------------------ paths
    if log_dir is None:
        # Lazy import avoids circular-import issues during startup
        from config.settings import settings  # noqa: PLC0415

        log_dir = settings.log_dir

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file: Path = log_dir / "app.log"

    # ------------------------------------------------------------------ level
    numeric_level: int = getattr(logging, log_level.upper(), logging.INFO)

    # ------------------------------------------------------------------ format
    fmt = (
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    )
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=date_fmt)

    # ------------------------------------------------------------------ handlers
    # Console handler – colourised level prefix when writing to a TTY
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Rotating file handler – 5 MB per file, keep 5 backups
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)

    # ------------------------------------------------------------------ root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Avoid duplicate handlers on repeated calls (e.g. during testing)
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
    else:
        # Replace existing handlers with fresh ones
        root_logger.handlers.clear()
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    # Silence noisy third-party loggers
    for noisy in ("urllib3", "httpx", "httpcore", "chromadb", "sentence_transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialised - level=%s, log_file=%s", log_level, log_file
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.  Call ``setup_logging()`` once at application
    startup; every module then calls this helper to get its own logger.

    Args:
        name : Usually ``__name__`` of the calling module.

    Returns:
        logging.Logger: A pre-configured logger instance.
    """
    return logging.getLogger(name)
