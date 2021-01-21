"""Package for exposing validation endpoint."""
import logging
import os

from aiohttp import web
from aiohttp_middlewares import cors_middleware, error_middleware
from dotenv import load_dotenv

from .view import Ping, Ready, Shape, Shapes, Validator

load_dotenv()
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# CORS configuration:
# Allow CORS requests from following urls:
CORS_ALLOW_ORIGINS = ["*"]


async def create_app() -> web.Application:
    """Create a web application."""
    app = web.Application(
        middlewares=[
            cors_middleware(origins=CORS_ALLOW_ORIGINS, allow_credentials=False),
            error_middleware(),  # default error handler for whole application
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
