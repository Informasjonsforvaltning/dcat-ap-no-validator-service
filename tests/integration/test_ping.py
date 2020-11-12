"""Integration test cases for the ping route."""
from typing import Any

import pytest


@pytest.mark.integration
async def test_ping(aiohttp_client: Any, loop) -> None:  # type: ignore
    """Should return OK."""
    client = await aiohttp_client()
    resp = await client.get("/ping")
    assert resp.status == 200
    text = await resp.text()
    assert "OK" in text
