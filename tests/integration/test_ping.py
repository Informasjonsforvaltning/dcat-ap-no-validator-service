"""Integration test cases for the ping route."""
from aiohttp.test_utils import TestClient as _TestClient
import pytest


@pytest.mark.integration
async def test_ready(client: _TestClient) -> None:
    """Should return OK."""
    resp = await client.get("/ping")
    assert resp.status == 200
    text = await resp.text()
    assert "OK" in text
