"""Integration test cases for the ontologies route."""

from typing import Dict

from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from pytest_mock import MockFixture


_MOCK_ONTOLOGY_STORE: Dict[str, Dict] = dict(
    {
        "1": {
            "id": "1",
            "name": "The ontologies used by DCAT-AP-NO",
            "version": "0.1",
            "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/develop/shacl/ontologies.ttl",  # noqa
        },
    }
)


@pytest.mark.integration
async def test_get_all_ontologies(client: _TestClient, mocker: MockFixture) -> None:
    """Should return OK."""
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.ontology_graph_adapter._ONTOLOGY_STORE",
        _MOCK_ONTOLOGY_STORE,
    )

    resp = await client.get("/ontologies")
    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    body = await resp.json()
    assert len(body) > 0


@pytest.mark.integration
async def test_get_ontology_by_id(client: _TestClient, mocker: MockFixture) -> None:
    """Should return OK."""
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.ontology_graph_adapter._ONTOLOGY_STORE",
        _MOCK_ONTOLOGY_STORE,
    )

    resp = await client.get("/ontologies/1")
    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    body = await resp.json()
    assert len(body) > 0
    assert identical_content(body, _MOCK_ONTOLOGY_STORE["1"])


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
async def test_get_ontology_by_id_not_found(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return OK."""
    resp = await client.get("/ontologies/doesnotexist")
    assert resp.status == 404


# ---------------------------------------------------------------------- #
# Utils for displaying debug information
