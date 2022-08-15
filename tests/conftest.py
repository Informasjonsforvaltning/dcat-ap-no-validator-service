"""Conftest module."""
import asyncio
import os
from os import environ as env
import time
from typing import Any

from aiohttp.test_utils import TestClient as _TestClient
from aiohttp_client_cache import CachedSession
from aiohttp_client_cache.backends.redis import RedisBackend
from dotenv import load_dotenv
import pytest
import requests
from requests.exceptions import ConnectionError

from dcat_ap_no_validator_service import create_app
from dcat_ap_no_validator_service.app import REDIS_HOST, REDIS_PASSWORD

load_dotenv()
HOST_PORT = int(env.get("HOST_PORT", "8080"))
REDIS_PORT = int(env.get("REDIS_PORT", "6379"))


@pytest.mark.integration
@pytest.fixture
async def client(aiohttp_client: Any) -> _TestClient:
    """Instantiate server and start it."""
    app = await create_app()
    return await aiohttp_client(app)


def is_responsive(url: Any) -> Any:
    """Return true if response from service is 200."""
    url = f"{url}/ready"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            time.sleep(2)  # sleep extra 2 sec
            return True
    except ConnectionError:
        return False


@pytest.mark.contract
@pytest.fixture(scope="session")
def http_service(docker_ip: Any, docker_services: Any, redis_service: Any) -> Any:
    """Ensure that HTTP service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("dcat-ap-no-validator-service", HOST_PORT)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope="session")
def event_loop() -> Any:
    """Must create a session scoped event loop."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.mark.contract
@pytest.fixture(scope="session")
async def redis_service(docker_ip: Any, docker_services: Any) -> Any:
    """Ensure that redis service is up and responsive."""
    error = None
    for _ in range(30):
        try:
            cache = RedisBackend(
                "aiohttp-cache",
                address=f"redis://{docker_ip}",
                port=docker_services.port_for(REDIS_HOST, REDIS_PORT),
                password=REDIS_PASSWORD,
                timeout=5,
            )
            async with CachedSession(cache=cache) as session:
                await session.get("https://digdir.no")
            return
        except BaseException as e:
            error = e
            time.sleep(2)
            pass
    raise ConnectionError(f"Unable to connect to redis cache: {error}") from error


@pytest.mark.contract
@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: Any) -> Any:
    """Override default location of docker-compose.yml file."""
    return os.path.join(str(pytestconfig.rootdir), "./", "docker-compose.yml")


@pytest.mark.contract
@pytest.fixture(scope="session")
def docker_cleanup(pytestconfig: Any) -> Any:
    """Override cleanup: do not remove containsers in order to inspect logs."""
    return "stop"
