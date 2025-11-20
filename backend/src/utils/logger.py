"""Logging configuration"""

import logging
import os
from pathlib import Path
from src.config import settings

# Ensure logs directory exists
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger("uw_course_checker")
logger.setLevel(getattr(logging, settings.log_level.upper()))

# Create formatters
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler for all logs
file_handler = logging.FileHandler(logs_dir / "combined.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# File handler for errors only
error_handler = logging.FileHandler(logs_dir / "error.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)
