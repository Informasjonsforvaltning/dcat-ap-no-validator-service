"""Package for exposing validation endpoint."""
from typing import Any

from aiohttp import web

from .view import Ping, Ready


async def create_app() -> web.Application:
    """Create an web application."""
    app = web.Application()
    app.add_routes([web.get("/ping", Ping), web.get("/ready", Ready)])
    return app
