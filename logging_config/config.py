# logging_config/config.py

import sys
import io
import logging

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": logging.INFO,
            "stream": io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace"),
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "app/app.log",
            "encoding": "utf-8",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 3,
            "level": logging.INFO,
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["console", "file"], "level": "INFO"},
        "fastapi": {"handlers": ["console", "file"], "level": "INFO"},
        "app": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
    },
    "root": {
        "handlers": ["console", "file"],
        "level": logging.INFO,
    },
}

