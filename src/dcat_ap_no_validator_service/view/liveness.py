"""Resource module for liveness resources."""
import os

from aiohttp import web
from aioredis import create_redis_pool, Redis

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
            redis_password = os.getenv("REDIS_PASSWORD")
            pool = await create_redis_pool(
                f"redis://{redis_host}", password=redis_password
            )
            r = Redis(pool)
            try:
                await r.ping()
            except OSError as e:
                raise e

        return web.Response(text="OK")


class Ping(web.View):
    """Class representing ping resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ping route function."""
        return web.Response(text="OK")
