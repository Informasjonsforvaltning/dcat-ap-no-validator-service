"""Integration test cases for the ready route."""
from typing import Any, Dict

from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from pytest_mock import MockFixture

from dcat_ap_no_validator_service.service import OntologiesService


_MOCK_ONTOLOGIES_STORE: Dict[str, Dict] = dict(
    {
        "1": {"id": "1", "name": "DCAT-AP-NO", "version": "1.1"},
        "2": {"id": "2", "name": "DCAT-AP-NO", "version": "2.0"},
    }
)


@pytest.fixture(scope="function")
def mocked_response(mocker: MockFixture) -> Any:
    """Patch the in memory ontologies db."""
    # Set up the mock
    mocker.patch.object(OntologiesService, "_ONTOLOGIES_STORE", _MOCK_ONTOLOGIES_STORE)


@pytest.mark.integration
async def test_get_all_ontologies(client: _TestClient, mocker: MockFixture) -> None:
    """Should return OK."""
    resp = await client.get("/ontologies")
    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    body = await resp.json()
    assert len(body) > 0


@pytest.mark.integration
async def test_get_ontology_by_id(client: _TestClient, mocker: MockFixture) -> None:
    """Should return OK."""
    resp = await client.get("/ontologies/1")
    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    body = await resp.json()
    assert len(body) > 0


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
