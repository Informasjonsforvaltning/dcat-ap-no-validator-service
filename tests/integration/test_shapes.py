"""Integration test cases for the ready route."""
from typing import Any, Dict

from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from pytest_mock import MockFixture

from dcat_ap_no_validator_service.service import ShapesService


_MOCK_SHAPES_DB: Dict[str, Dict] = dict(
    {
        "1": {"id": "1", "name": "DCAT-AP-NO", "version": "1.1"},
        "2": {"id": "2", "name": "DCAT-AP-NO", "version": "2.0"},
    }
)


@pytest.fixture(scope="function")
def mocked_response(mocker: MockFixture) -> Any:
    """Patch the in memory shapes db."""
    # Set up the mock
    mocker.patch.object(ShapesService, "_SHAPES_DB", _MOCK_SHAPES_DB)


@pytest.mark.integration
async def test_get_all_shapes(client: _TestClient, mocker: MockFixture) -> None:
    """Should return OK."""
    resp = await client.get("/shapes")
    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    body = await resp.json()
    assert len(body) > 0


@pytest.mark.integration
async def test_get_shapes_by_id(client: _TestClient, mocker: MockFixture) -> None:
    """Should return OK."""
    resp = await client.get("/shapes/1")
    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    body = await resp.json()
    assert len(body) > 0


# --- Bad cases ---
@pytest.mark.integration
async def test_get_shapes_by_id_not_found(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return OK."""
    resp = await client.get("/shapes/doesnotexist")
    assert resp.status == 404


# ---------------------------------------------------------------------- #
# Utils for displaying debug information
