"""Package for exposing validation endpoint."""
import logging
import os

from aiohttp import web
from aiohttp_middlewares import cors_middleware
from dotenv import load_dotenv

from .view import Ping, Ready, Shape, Shapes, Validator

load_dotenv()
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# CORS configuration
CORS_ALLOW_ORIGINS = ["https://staging.fellesdatakatalog.digdir.no"]


async def create_app() -> web.Application:
    """Create an web application."""
    app = web.Application(
        middlewares=[
            cors_middleware(origins=CORS_ALLOW_ORIGINS, allow_credentials=True)
        ]
    )
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
