"""Resource module for liveness resources."""
import os

from aiohttp import web
from redis import Redis, RedisError

CONFIG = os.getenv("CONFIG", "production")


class Ready(web.View):
    """Class representing ready resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ready route function."""
        if CONFIG in {"test", "dev"}:
            pass
        else:  # pragma: no cover
            redis_host = os.getenv("REDIS_HOST", "localhost")
            r = Redis(
                redis_host, socket_connect_timeout=1
            )  # short timeout for the test
            try:
                r.ping()
            except RedisError as e:
                raise e

        return web.Response(text="OK")


class Ping(web.View):
    """Class representing ping resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ping route function."""
        return web.Response(text="OK")
