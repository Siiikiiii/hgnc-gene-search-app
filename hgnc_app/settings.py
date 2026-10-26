# settings.py
"""
Central configuration for the HGNC gene search application: where logs are
written, how logging is set up, and which HGNC data file is loaded.

The logging configuration follows the dictionary schema described in the
Python documentation:
https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
"""

import os
from pathlib import Path

# --------------------------------------------------
# Log file location
# --------------------------------------------------
# Logs go to a hidden file in the user's home directory so the app can
# always write them, wherever it is launched from and even when the
# package is installed somewhere read-only (e.g. site-packages).
home_dir = os.path.expanduser("~")
DEFAULT_LOG = os.path.join(home_dir, ".hgnc_app.log")

LOG_FILE = DEFAULT_LOG


# --------------------------------------------------
# Normalise the path
# --------------------------------------------------
# No effect on the default above (already absolute), but keeps LOG_FILE
# valid if it is changed to a relative or "~" path.
LOG_FILE = os.path.abspath(os.path.expanduser(LOG_FILE))


# --------------------------------------------------
# Ensure the log directory exists
# --------------------------------------------------
# logging.FileHandler does not create missing directories, and would
# otherwise fail when the logging configuration is applied at start-up.
log_dir = os.path.dirname(LOG_FILE)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------
# The console shows INFO and above (start-up, genes found / not found) so
# the terminal stays readable; the log file also keeps DEBUG messages
# (e.g. every search term received) for troubleshooting afterwards.
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    # --------------------------------------------------
    # FORMATTERS
    # --------------------------------------------------
    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s | %(levelname)s | %(name)s | "
                "%(filename)s:%(lineno)d | %(message)s"
            )
        }
    },

    # --------------------------------------------------
    # HANDLERS
    # --------------------------------------------------
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": LOG_FILE,
        },
    },

    # The app's own loggers (hgnc_app.*) write directly to both handlers.
    # propagate=False stops each message also reaching the root logger,
    # which has the same handlers and would log it a second time.
    "loggers": {
        "hgnc_app": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        },
    },

    # --------------------------------------------------
    # ROOT LOGGER
    # --------------------------------------------------
    # Catches messages from third-party libraries such as Flask and
    # Werkzeug (e.g. the request log), so they appear alongside the app's
    # own messages.
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    }
}

# Data directory, resolved relative to this file rather than the current
# working directory so the app finds the data wherever it is launched from.
# This assumes the editable install described in the README
# (pip install -e .): in a regular install this path would point inside
# site-packages, where data/ does not exist.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Setup data file
DATA_FILE = DATA_DIR / "hgnc_complete_set.txt"