import logging
from logging import config
import typing as t
import os


def log_cfg(log_file: str) -> t.Dict[str, t.Any]:
    return {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "simple": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "info_file_handler": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": log_file,
                "when": "D",
                "backupCount": 3,
                "encoding": "utf8",
            },
        },
        "root": {"level": "INFO", "handlers": ["console", "info_file_handler"]},
    }


def create_logger() -> logging.Logger:
    if not os.path.exists('log'):
        os.mkdir('log')
    config.dictConfig(log_cfg('log/main.log'))
    return logging.getLogger('main')


logger = create_logger()
