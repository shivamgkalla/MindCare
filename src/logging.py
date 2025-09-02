import logging
from logging.handlers import RotatingFileHandler
from enum import StrEnum
import os


# ANSI Color Codes (for better visibility in the temrinal)
COLORS = {
    "DEBUG": "\033[36m",   # Cyan
    "INFO": "\033[32m",   # Green
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",   # Red
    "RESET": "\033[0m"      # Reset
}


LOG_FORMAT_DEBUG = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(lineno)d - %(message)s"
LOG_FORMAT_SIMPLE = "%(asctime)s - %(levelname)s - %(message)s"

LOG_FILE_PATH = os.path.join("logs", "app.log")


class LogLevels(StrEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


class ColorFormatter(logging.Formatter):

    """ Custom formatter to add color to the logs in the terminal """

    def format(self, record):
        log_fmt = LOG_FORMAT_DEBUG if record.levelno == logging.DEBUG else LOG_FORMAT_SIMPLE
        formatter = logging.Formatter(log_fmt)

        log_msg = formatter.format(record)
        level_name = record.levelname

        color = COLORS.get(level_name, COLORS["RESET"])
        reset = COLORS["RESET"]

        return f"{color}{log_msg}{reset}"



def configure_logging(log_level: str = LogLevels.error):
    os.makedirs("logs", exist_ok=True)


    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevels]

    if log_level not in log_levels:
        log_level = LogLevels.error


    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)


    # Clear old handlers
    if logger.hasHandlers():
        logger.handlers.clear()


    # Console handler (colorized)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(ColorFormatter())


    log_format = LOG_FORMAT_DEBUG if log_level == LogLevels.debug else LOG_FORMAT_SIMPLE

    # Rotating file handler (max 50MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=5_00_00_000, backupCount=5)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))


    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


    logger.info(f"Logging configured. Level: {log_level}")