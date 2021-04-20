"""Contract test cases for ready."""
from typing import Any

from aiohttp import ClientSession
import pytest


@pytest.mark.contract
@pytest.mark.asyncio
async def test_ready(http_service: Any) -> None:
    """Should return OK."""
    url = f"{http_service}/ready"

    session = ClientSession()
    async with session.get(url) as response:
        text = await response.text()
    await session.close()

    assert response.status == 200
    assert text == "OK"
