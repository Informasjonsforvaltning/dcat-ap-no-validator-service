"""Gunicorn module for mapping a catalog to rdf."""
import logging
import multiprocessing
from os import environ as env
from typing import Any

from dotenv import load_dotenv
from gunicorn import glogging

load_dotenv()

HOST_PORT = env.get("HOST_PORT", "8080")
DEBUG_MODE = env.get("DEBUG_MODE", False)
LOG_LEVEL = env.get("LOG_LEVEL", "info")

# Gunicorn config
bind = ":" + HOST_PORT
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2 * multiprocessing.cpu_count()
loglevel = str(LOG_LEVEL)
accesslog = "-"

# Need to override the logger to remove healthcheck (ping) form accesslog


class CustomGunicornLogger(glogging.Logger):
    """Custom Gunicorn Logger class."""

    def setup(self, cfg: Any) -> None:
        """Set up function."""
        super().setup(cfg)

        # Add filters to Gunicorn logger
        logger = logging.getLogger("gunicorn.access")
        logger.addFilter(PingFilter())
        logger.addFilter(ReadyFilter())


class PingFilter(logging.Filter):
    """Custom Ping Filter class."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter function."""
        return "GET /ping" not in record.getMessage()


class ReadyFilter(logging.Filter):
    """Custom Ready Filter class."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter function."""
        return "GET /ready" not in record.getMessage()


logger_class = CustomGunicornLogger
