"""Integration test cases for the ready route."""
from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from pytest_mock import MockFixture
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic


@pytest.mark.integration
async def test_get_all_shapes(client: _TestClient) -> None:
    """Should return OK."""
    resp = await client.get("/shapes")
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()
    assert len(body) > 0


@pytest.mark.integration
async def test_get_shapes_by_id(client: _TestClient) -> None:
    """Should return OK."""
    resp = await client.get("/shapes/1.1")
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    g1 = Graph().parse(data=body, format="turtle")
    g2 = Graph().parse("dcat-ap_shacl_shapes_1.1.ttl", format="turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "data_graph is not equal to the input data"


# --- Bad cases ---
@pytest.mark.integration
async def test_get_shapes_by_id_not_found(client: _TestClient) -> None:
    """Should return OK."""
    resp = await client.get("/shapes/doesnotexist")
    assert resp.status == 404
    body = await resp.text()
    assert "Not Found" in body


@pytest.mark.integration
async def test_get_all_shapes_accept_header_not_supported(
    client: _TestClient,
) -> None:
    """Should return 406."""
    headers = {hdrs.ACCEPT: "doesnotexist"}
    resp = await client.get("/shapes", headers=headers)
    assert resp.status == 406
    body = await resp.text()
    assert "Not Acceptable" in body


@pytest.mark.integration
async def test_get_shapes_by_id_accept_header_not_supported(
    client: _TestClient,
) -> None:
    """Should return 406."""
    headers = {hdrs.ACCEPT: "doesnotexist"}
    resp = await client.get("/shapes/1.1", headers=headers)
    assert resp.status == 406
    body = await resp.text()
    assert "Not Acceptable" in body


@pytest.mark.integration
async def test_get_all_shapes_fails(client: _TestClient, mocker: MockFixture) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "rdflib.Graph.parse",
        side_effect=Exception,
    )
    resp = await client.get("/shapes")
    assert resp.status == 500
    body = await resp.text()
    assert "Internal Server Error" in body


@pytest.mark.integration
async def test_get_shapes_by_id_fails(client: _TestClient, mocker: MockFixture) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "rdflib.Graph.parse",
        side_effect=Exception,
    )
    resp = await client.get("/shapes/1.1")
    assert resp.status == 500
    body = await resp.text()
    assert "Internal Server Error" in body


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
