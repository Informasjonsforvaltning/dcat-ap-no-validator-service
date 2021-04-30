"""Integration test cases for the ontologies service."""
from typing import Dict

import pytest
from pytest_mock import MockFixture

from dcat_ap_no_validator_service.service import OntologiesService

_MOCK_ONTOLOGIES_STORE: Dict[str, Dict] = dict(
    {
        "1": {"id": "1", "name": "DCAT-AP-NO", "version": "1.1"},
        "2": {"id": "2", "name": "DCAT-AP-NO", "version": "2.0"},
    }
)


@pytest.mark.unit
async def test_get_ontologies(mocker: MockFixture) -> None:
    """Should return a non-empyt graph."""
    mocker.patch.object(OntologiesService, "_ONTOLOGIES_STORE", _MOCK_ONTOLOGIES_STORE)
    ontologies_collection = await OntologiesService().get_all_ontologies()
    assert type(ontologies_collection) == dict
    assert "ontologies" in ontologies_collection
    assert type(ontologies_collection["ontologies"]) == list
    assert len(ontologies_collection["ontologies"]) == len(_MOCK_ONTOLOGIES_STORE)
    for s in ontologies_collection["ontologies"]:
        assert s == _MOCK_ONTOLOGIES_STORE[s["id"]]


@pytest.mark.unit
async def test_get_ontology_by_id(mocker: MockFixture) -> None:
    """Should return a non-empyt graph."""
    mocker.patch.object(OntologiesService, "_ONTOLOGIES_STORE", _MOCK_ONTOLOGIES_STORE)
    ontology = await OntologiesService().get_ontology_by_id("1")
    assert type(ontology) == dict
    assert ontology == _MOCK_ONTOLOGIES_STORE["1"]
