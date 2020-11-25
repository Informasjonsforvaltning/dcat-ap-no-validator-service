"""Package for exposing validation endpoint."""
import logging

from aiohttp import web

from .view import Ping, Ready, Shape, Shapes, Validator


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
    # TODO: get level from environment and set default to INFO
    logging.basicConfig(level=logging.DEBUG)
    return app
