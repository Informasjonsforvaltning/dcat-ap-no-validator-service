"""Resource module for liveness resources."""
import logging
import os
import traceback

from aiohttp import web
from aioredis import create_redis

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
            address = f"redis://{redis_host}"
            try:
                redis = await create_redis(address, timeout=1, password=redis_password)
                await redis.ping()

                redis.close()
                await redis.wait_closed()
            except OSError:
                logging.error(traceback.format_exc())
                raise web.HTTPInternalServerError(
                    reason=f"Redis cache not available at {address}."
                )
        return web.Response(text="OK")


class Ping(web.View):
    """Class representing ping resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ping route function."""
        return web.Response(text="OK")
