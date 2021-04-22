"""Contract test cases for ping."""
from typing import Any

from aiohttp import ClientSession
import pytest


@pytest.mark.contract
@pytest.mark.asyncio
async def test_ping(http_service: Any) -> None:
    """Should return OK."""
    url = f"{http_service}/ping"

    session = ClientSession()
    async with session.get(url) as response:
        text = await response.text()
    await session.close()

    assert response.status == 200
    assert text == "OK"
