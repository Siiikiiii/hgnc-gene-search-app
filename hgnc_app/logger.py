# logger.py
"""
Applies the logging configuration defined in settings.LOGGING_CONFIG.

Configuration is applied by calling setup_logging() from create_app()
rather than when this module is imported, so importing hgnc_app modules
does not change logging set-up as a side effect; it happens only when an
application is actually built.
"""

import logging.config

from hgnc_app.settings import LOGGING_CONFIG


# --------------------------------------------------
# LOGGING ACTIVATION FUNCTION
# --------------------------------------------------
def setup_logging():
    """
    Apply the logging configuration.

    Call once at application start-up. Python's logging is process-wide,
    so after this call every module can simply use
    logging.getLogger(__name__): loggers named "hgnc_app.*" pick up the
    "hgnc_app" settings and handlers, and all others fall back to the root
    logger.
    """

    logging.config.dictConfig(LOGGING_CONFIG)