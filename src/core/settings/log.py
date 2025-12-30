# *_*coding:utf-8 *_*
# @File   : log.py
# @Author : Reggie
# @Time   : 2025/08/28 12:38

from ..const import PROJECT_DIR

# 日志路径
LOG_PATH = PROJECT_DIR.joinpath("logs")
LOG_PATH.mkdir(exist_ok=True, parents=True)
LOG_LEVEL = "INFO"

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s -- %(name)s -- %(threadName)s -- %(levelname)s -- %(message)s -- (%(funcName)s in %(filename)s):%(lineno)d"
        },
        "minimal": {
            "format": "%(message)s"
        },
        "robot": {
            "format": "%(asctime)s -- %(name)s -- %(username)s -- %(levelname)s -- %(message)s -- (%(funcName)s in %(filename)s):%(lineno)d"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 50,
            "backupCount": 3,
            "formatter": "detailed",
            "filename": LOG_PATH / "app.log",
            "encoding": "utf-8",
        },
        "alembic-file": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 50,
            "backupCount": 3,
            "formatter": "detailed",
            "filename": LOG_PATH / "alembic.log",
            "encoding": "utf-8",
        },
        "sqlalchemy-file": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 50,
            "backupCount": 3,
            "formatter": "detailed",
            "filename": LOG_PATH / "sqlalchemy.log",
            "encoding": "utf-8",
        },
        "robot-console": {
            "class": "logging.StreamHandler",
            "formatter": "robot",
        },
    },
    "loggers": {
        "app": {
            "level": LOG_LEVEL,
            'handlers': ["console", "file"],
        },
        "alembic": {
            "level": LOG_LEVEL,
            'handlers': ["alembic-file"],
        },
        "sqlalchemy": {
            "level": LOG_LEVEL,
            'handlers': ["sqlalchemy-file"],
        },
    },
}
