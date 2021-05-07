"""Integration test cases for the ontology graph adapter."""
from typing import Any, Dict

import pytest
from pytest_mock import MockFixture

from dcat_ap_no_validator_service.adapter import OntologyGraphAdapter
from dcat_ap_no_validator_service.model import OntologyGraphDescription

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


@pytest.mark.unit
async def test_get_all(mocker: MockFixture) -> None:
    """Should return a non-empty graph collection."""
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.ontology_graph_adapter._ONTOLOGY_STORE",
        _MOCK_ONTOLOGY_STORE,
    )
    ontology_collection = await OntologyGraphAdapter.get_all()
    assert type(ontology_collection) == list
    assert len(ontology_collection) == 1
    for s in ontology_collection:
        assert type(s) == OntologyGraphDescription
    assert identical_content(s, _MOCK_ONTOLOGY_STORE[s.id])


@pytest.mark.unit
async def test_get_by_id(mocker: MockFixture) -> None:
    """Should return a non-empty graph."""
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.ontology_graph_adapter._ONTOLOGY_STORE",
        _MOCK_ONTOLOGY_STORE,
    )
    ontology = await OntologyGraphAdapter.get_by_id("1")
    assert type(ontology) == OntologyGraphDescription
    assert identical_content(ontology, _MOCK_ONTOLOGY_STORE["1"])


def identical_content(s: Any, d: dict) -> bool:
    """Check for equal content."""
    return (
        s.id == d["id"]
        and s.name == d["name"]
        and s.version == d["version"]
        and s.url == d["url"]
        and s.description is None
        and s.specification_name is None
        and s.specification_version is None
        and s.specification_url is None
    )
