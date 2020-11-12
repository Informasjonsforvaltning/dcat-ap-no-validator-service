"""Integration test cases for the ready route."""
from aiohttp.test_utils import TestClient as _TestClient
import pytest


@pytest.mark.integration
async def test_validator(client: _TestClient) -> None:
    """Should return OK."""
    with open("./tests/files/catalog_1.ttl") as ttl_file:
        data = ttl_file.read()
    headers = {
        "Content-Type": "text/turtle",
    }
    resp = await client.post("/validator", headers=headers, data=data)
    assert resp.status == 200
    text = await resp.text()
    assert text == "OK"
