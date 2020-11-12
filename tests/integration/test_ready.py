"""Integration test cases for the ready route."""
from typing import Any

import pytest

from dcat_ap_no_validator_service import create_app


@pytest.mark.integration
async def test_ready(aiohttp_client: Any, loop) -> None:
    """Should return OK."""
    client = await aiohttp_client(create_app)
    resp = await client.get("/ready")
    assert resp.status == 200
    text = await resp.text()
    assert "OK" in text
