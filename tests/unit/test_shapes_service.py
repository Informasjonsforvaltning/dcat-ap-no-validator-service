"""Integration test cases for the graph_adapter."""
from typing import Dict

import pytest
from pytest_mock import MockFixture

from dcat_ap_no_validator_service.service import ShapesService

_MOCK_SHAPES_STORE: Dict[str, Dict] = dict(
    {
        "1": {"id": "1", "name": "DCAT-AP-NO", "version": "1.1"},
        "2": {"id": "2", "name": "DCAT-AP-NO", "version": "2.0"},
    }
)


@pytest.mark.unit
async def test_get_shapes(mocker: MockFixture) -> None:
    """Should return a non-empyt graph."""
    mocker.patch.object(ShapesService, "_SHAPES_STORE", _MOCK_SHAPES_STORE)
    shapes_collection = await ShapesService().get_all_shapes()
    assert type(shapes_collection) == list
    assert len(shapes_collection) == 2
    for s in shapes_collection:
        assert s == _MOCK_SHAPES_STORE[s["id"]]


@pytest.mark.unit
async def test_get_shapes_by_id(mocker: MockFixture) -> None:
    """Should return a non-empyt graph."""
    mocker.patch.object(ShapesService, "_SHAPES_STORE", _MOCK_SHAPES_STORE)
    shapes = await ShapesService().get_shapes_by_id("1")
    assert type(shapes) == dict
    assert shapes == _MOCK_SHAPES_STORE["1"]
