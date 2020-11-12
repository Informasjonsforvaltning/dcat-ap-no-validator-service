"""Integration test cases for the ready route."""
from aiohttp.test_utils import TestClient as _TestClient
import pytest


@pytest.mark.integration
async def test_ready(client: _TestClient) -> None:
    """Should return OK."""
    resp = await client.get("/ready")
    assert resp.status == 200
    text = await resp.text()
    assert "OK" in text
