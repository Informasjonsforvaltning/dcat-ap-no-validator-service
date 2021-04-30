"""Contract test cases for ready."""
from typing import Any

from aiohttp import ClientSession, hdrs
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff  # , isomorphic

# TODO find a way to automatically test openAPI spec


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_all_shapes(http_service: Any) -> None:
    """Should return 200 and a list of shapes."""
    url = f"{http_service}/shapes"

    session = ClientSession()
    async with session.get(url) as resp:
        body = await resp.json()
    await session.close()

    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    assert type(body) is dict
    assert "shapes" in body
    assert len(body["shapes"]) == 2
    for s in body["shapes"]:
        assert "id" in s, "No id property in shapes graph object"
        assert "name" in s, "No name property in shapes graph object"
        assert "description" in s, "No description property in shapes graph object"
        assert "version" in s, "No version property in shapes graph object"
        assert "url" in s, "No url property in shapes graph object"
        assert (
            "specification_name" in s
        ), "No specification_name property in shapes graph object"
        assert (
            "specification_version" in s
        ), "No specification_version property in shapes graph object"
        assert (
            "specification_url" in s
        ), "No specification_url property in shapes graph object"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_shape_by_id(http_service: Any) -> None:
    """Should return 200 and a shape description."""
    shape_id = 1
    url = f"{http_service}/shapes/{shape_id}"

    session = ClientSession()
    async with session.get(url) as resp:
        shape = await resp.json()
    await session.close()

    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    assert type(shape) is dict
    assert "id" in shape, "No id property in shapes graph object"
    assert "name" in shape, "No name property in shapes graph object"
    assert "description" in shape, "No description property in shapes graph object"
    assert "version" in shape, "No version property in shapes graph object"
    assert "url" in shape, "No url property in shapes graph object"
    assert (
        "specification_name" in shape
    ), "No specification_name property in shapes graph object"
    assert (
        "specification_version" in shape
    ), "No specification_version property in shapes graph object"
    assert (
        "specification_url" in shape
    ), "No specification_url property in shapes graph object"


# ---------------------------------------------------------------------- #
# Utils for displaying debug information


def _dump_diff(g1: Graph, g2: Graph) -> None:
    in_both, in_first, in_second = graph_diff(g1, g2)
    print("\nin both:")
    _dump_turtle(in_both)
    print("\nin first:")
    _dump_turtle(in_first)
    print("\nin second:")
    _dump_turtle(in_second)


def _dump_turtle(g: Graph) -> None:
    for _l in g.serialize(format="turtle").splitlines():
        if _l:
            print(_l.decode())
