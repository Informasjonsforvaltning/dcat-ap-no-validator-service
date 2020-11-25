"""Contract test cases for ready."""
from typing import Any

from aiohttp import ClientSession, hdrs
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff  # , isomorphic


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_all_shapes(http_service: Any) -> None:
    """Should return OK and a graph with a list of shapes."""
    url = f"{http_service}/shapes"

    session = ClientSession()
    async with session.get(url) as resp:
        pass
    await session.close()

    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    print(f"resp.text: {resp.text}")


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
