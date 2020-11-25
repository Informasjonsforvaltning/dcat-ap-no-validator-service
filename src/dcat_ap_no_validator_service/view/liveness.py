"""Resource module for liveness resources."""
from aiohttp import web


class Ready(web.View):
    """Class representing ready resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ready route function."""
        return web.Response(text="OK")


class Ping(web.View):
    """Class representing ping resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ping route function."""
        return web.Response(text="OK")
