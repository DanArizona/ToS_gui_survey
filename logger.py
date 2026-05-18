# logger.py

import logging
from datetime import datetime
import os

def setup_logger(name: str = "widget_monitor") -> logging.Logger:
    """
    Set up and return a logger with a date-based log file name.
    Appends to the log if it already exists.

    Example log filename: scan_2025-07-15.log
    """
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"logs/scan_{today_str}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(log_filename, encoding="utf-8", mode="a")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
