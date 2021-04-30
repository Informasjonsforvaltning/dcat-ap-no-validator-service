"""Contract test cases for ontologies resource."""
from typing import Any

from aiohttp import ClientSession, hdrs
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff  # , isomorphic

# TODO find a way to automatically test openAPI spec


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_all_ontologies(http_service: Any) -> None:
    """Should return 200 and a list of ontologies."""
    url = f"{http_service}/ontologies"

    session = ClientSession()
    async with session.get(url) as resp:
        body = await resp.json()
    await session.close()

    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    assert type(body) is dict
    assert "ontologies" in body
    assert len(body["ontologies"]) == 1
    for s in body["ontologies"]:
        assert "id" in s, "No id property in ontology graph object"
        assert "name" in s, "No name property in ontology graph object"
        assert "description" in s, "No description property in ontology graph object"
        assert "version" in s, "No version property in ontology graph object"
        assert "url" in s, "No url property in ontology graph object"
        assert (
            "specification_name" in s
        ), "No specification_name property in ontology graph object"
        assert (
            "specification_version" in s
        ), "No specification_version property in ontology graph object"
        assert (
            "specification_url" in s
        ), "No specification_url property in ontology graph object"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_ontology_by_id(http_service: Any) -> None:
    """Should return 200 and a ontology description."""
    ontology_id = 1
    url = f"{http_service}/ontologies/{ontology_id}"

    session = ClientSession()
    async with session.get(url) as resp:
        ontology = await resp.json()
    await session.close()

    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    assert type(ontology) is dict
    assert "id" in ontology, "No id property in ontology graph object"
    assert "name" in ontology, "No name property in ontology graph object"
    assert "description" in ontology, "No description property in ontology graph object"
    assert "version" in ontology, "No version property in ontology graph object"
    assert "url" in ontology, "No url property in ontology graph object"
    assert (
        "specification_name" in ontology
    ), "No ontology specification_name property in ontology graph object"
    assert (
        "specification_version" in ontology
    ), "No specification_version property in ontology graph object"
    assert (
        "specification_url" in ontology
    ), "No specification_url property in ontology graph object"


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
