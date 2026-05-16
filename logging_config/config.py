# logging_config/config.py

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
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "app/app.log",  
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

