"""Integration test cases for the shapes graph adapter."""
from typing import Any, Dict

import pytest
from pytest_mock import MockFixture

from dcat_ap_no_validator_service.adapter import ShapesGraphAdapter
from dcat_ap_no_validator_service.model import ShapesGraphDescription

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


@pytest.mark.unit
async def test_get_all(mocker: MockFixture) -> None:
    """Should return a non-empty graph collection."""
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.shapes_graph_adapter._SHAPES_STORE",
        _MOCK_SHAPES_STORE,
    )
    shapes_collection = await ShapesGraphAdapter.get_all()
    assert isinstance(shapes_collection, list)
    assert len(shapes_collection) == 2
    for s in shapes_collection:
        assert isinstance(s, ShapesGraphDescription)
    assert identical_content(s, _MOCK_SHAPES_STORE[s.id])


@pytest.mark.unit
async def test_get_by_id(mocker: MockFixture) -> None:
    """Should return a non-empty graph."""
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.shapes_graph_adapter._SHAPES_STORE",
        _MOCK_SHAPES_STORE,
    )
    shapes = await ShapesGraphAdapter.get_by_id("1")
    assert isinstance(shapes, ShapesGraphDescription)
    assert identical_content(shapes, _MOCK_SHAPES_STORE["1"])


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
