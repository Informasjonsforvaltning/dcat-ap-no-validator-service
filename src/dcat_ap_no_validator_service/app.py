"""Package for exposing validation endpoint."""
import logging
import os

from aiohttp import web
from aiohttp_middlewares import cors_middleware, error_middleware
from dotenv import load_dotenv

from .view import Ontologies, Ontology, Ping, Ready, Shapes, ShapesCollection, Validator

load_dotenv()
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")


async def create_app() -> web.Application:
    """Create a web application."""
    app = web.Application(
        middlewares=[
            cors_middleware(allow_all=True),
            error_middleware(),  # default error handler for whole application
        ]
    )
    app.add_routes(
        [
            web.view("/ping", Ping),
            web.view("/ready", Ready),
            web.view("/validator", Validator),
            web.view("/shapes", ShapesCollection),
            web.view("/shapes/{id}", Shapes),
            web.view("/ontologies", Ontologies),
            web.view("/ontologies/{id}", Ontology),
        ]
    )

    # logging configurataion:
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(levelname)s - %(module)s:%(lineno)d: %(message)s",
        datefmt="%H:%M:%S",
        level=LOGGING_LEVEL,
    )
    logging.getLogger("chardet.charsetprober").setLevel(logging.INFO)

    return app
