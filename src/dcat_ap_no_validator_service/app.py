"""Package for exposing validation endpoint."""
import logging
import os

from aiohttp import web
from dotenv import load_dotenv

from .view import Ping, Ready, Shape, Shapes, Validator

load_dotenv()
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")


async def create_app() -> web.Application:
    """Create an web application."""
    app = web.Application()
    app.add_routes(
        [
            web.view("/ping", Ping),
            web.view("/ready", Ready),
            web.view("/validator", Validator),
            web.view("/shapes", Shapes),
            web.view("/shapes/{id}", Shape),
        ]
    )
    # logging configurataion:
    logging.basicConfig(level=LOGGING_LEVEL)
    return app
