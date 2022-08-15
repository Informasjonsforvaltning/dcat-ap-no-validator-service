"""Resource module for liveness resources."""
import os

from aiohttp import web
import redis.asyncio as redis

CONFIG = os.getenv("CONFIG", "production")


class Ready(web.View):
    """Class representing ready resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ready route function."""
        if CONFIG in {"test", "dev"}:
            pass
        else:  # pragma: no cover
            host = os.getenv("REDIS_HOST", "localhost")
            password = os.getenv("REDIS_PASSWORD")
            connection: redis.Redis = redis.Redis(host=host, password=password)
            await connection.ping()

            await connection.close()
        return web.Response(text="OK")


class Ping(web.View):
    """Class representing ping resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ping route function."""
        return web.Response(text="OK")
