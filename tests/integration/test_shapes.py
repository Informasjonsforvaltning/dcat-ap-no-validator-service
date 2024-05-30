"""Integration test cases for the shapes route."""

from typing import Dict

from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from pytest_mock import MockFixture


_MOCK_SHAPES_STORE: Dict[str, Dict] = dict(
    {
        "1": {
            "id": "1",
            "name": "DCAT-AP-NO",
            "version": "1.1",
            "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/v1.1/shacl/dcat-ap_shacl_shapes_1.1.ttl",
        },
        "2": {
            "id": "2",
            "name": "DCAT-AP-NO",
            "version": "2.0",
            "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/v2/shacl/DCAT-AP-NO-shacl_shapes_2.00.ttl",  # noqa
        },
    }
)


@pytest.mark.integration
async def test_get_all_shapes(client: _TestClient, mocker: MockFixture) -> None:
    """Should return OK."""
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.shapes_graph_adapter._SHAPES_STORE",
        _MOCK_SHAPES_STORE,
    )

    resp = await client.get("/shapes")
    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    body = await resp.json()
    assert len(body) > 0


@pytest.mark.integration
async def test_get_shapes_by_id(client: _TestClient, mocker: MockFixture) -> None:
    """Should return OK."""
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.shapes_graph_adapter._SHAPES_STORE",
        _MOCK_SHAPES_STORE,
    )

    resp = await client.get("/shapes/1")
    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    body = await resp.json()
    assert len(body) > 0
    assert identical_content(body, _MOCK_SHAPES_STORE["1"])


def identical_content(s: dict, d: dict) -> bool:
    """Check for equal content."""
    return (
        s["id"] == d["id"]
        and s["name"] == d["name"]
        and s["version"] == d["version"]
        and s["url"] == d["url"]
        and s["description"] is None
        and s["specificationName"] is None
        and s["specificationVersion"] is None
        and s["specificationUrl"] is None
    )


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
