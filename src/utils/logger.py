"""
Logging module for Face Mouse Pro.
Provides structured logging with console output and rotating file handlers.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(
    name: str = "FaceMousePro", log_dir: str | None = None, log_level: int = logging.INFO
) -> logging.Logger:
    """
    Configures and returns a logger instance with console and file output.

    :param name: Logger name.
    :param log_dir: Target directory for log files. Defaults to 'logs' in the project root.
    :param log_level: Logging level (e.g. logging.INFO, logging.DEBUG).
    :return: Configured logging.Logger.
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(module)s:%(lineno)d] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_dir is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        log_dir = os.path.join(project_root, "logs")

    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "facemouse.log")

    try:
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as err:
        logger.warning(f"Failed to initialize file logger at {log_file_path}: {err}")

    return logger
