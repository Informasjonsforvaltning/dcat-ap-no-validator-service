"""Package for exposing validation endpoint."""
from datetime import timedelta
import logging
import os
from typing import Any

from aiohttp import web
from aiohttp_client_cache.backends.redis import RedisBackend
from aiohttp_middlewares import cors_middleware, error_middleware
from dotenv import load_dotenv

from .view import Ontologies, Ontology, Ping, Ready, Shapes, ShapesCollection, Validator

load_dotenv()
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
CONFIG = os.getenv("CONFIG", "production")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


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

    async def redis_context(app: Any) -> Any:
        # Enable cache in all other cases than test:
        if CONFIG in {"test", "dev"}:
            cache = None
        else:  # pragma: no cover
            cache = RedisBackend(
                "aiohttp-cache",
                address=f"redis://{REDIS_HOST}",
                password=REDIS_PASSWORD,
                timeout=5,
                expire_after=timedelta(days=1),
            )
            logging.debug(f"Cache enabled: {cache}")
            await cache.clear()
            logging.debug(f"Cache cleared: {cache}")
        app["cache"] = cache

        yield

        if cache:  # pragma: no cover
            await cache.close()

    app.cleanup_ctx.append(redis_context)

    return app
