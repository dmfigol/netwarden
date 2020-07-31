LOGGING_DICT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std": {
            "format": "[%(asctime)s] %(levelname)-8s {%(name)s:%(filename)s:%(lineno)d} %(message)s"
        },
        # "std": {
        #     "format": "[%(asctime)s] %(levelname)-8s {%(filename)s:%(lineno)d} %(message)s"
        # }
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "std",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "std",
        },
    },
    "loggers": {
        "scrapli": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "asyncssh": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        # "netmiko": {
        #     "handlers": ["console-module", "file-module"],
        #     "level": "WARNING",
        #     "propagate": False,
        # },
        # "paramiko": {
        #     "handlers": ["console-module", "file-module"],
        #     "level": "WARNING",
        #     "propagate": False,
        # },
        # "": {
        #     "handlers": ["console", "default"],
        #     "level": "DEBUG",
        #     "propagate": False
        # }
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}
