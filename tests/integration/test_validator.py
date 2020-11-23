"""Integration test cases for the ready route."""
from aiohttp import ClientResponse, hdrs, MultipartReader, MultipartWriter
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic


@pytest.mark.integration
async def test_validator_file(client: _TestClient) -> None:
    """Should return OK."""
    filename = "tests/files/catalog_1.ttl"
    version = "2"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition("attachment", name="file", filename=filename)
        p = mpwriter.append(version)
        p.set_content_disposition("inline", name="version")

    resp = await client.post("/validator", data=mpwriter)
    await _assess_response(resp)


@pytest.mark.integration
async def test_validator_url(client: _TestClient) -> None:
    """Should return status 501."""
    url = "http://example.com/"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url)
        p.set_content_disposition("inline", name="url")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 501


@pytest.mark.integration
async def test_validator_text(client: _TestClient) -> None:
    """Should return status 501."""
    with open("tests/files/catalog_1.ttl", "r") as file:
        text = file.read()

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(text)
        p.set_content_disposition("inline", name="text")

    resp = await client.post("/validator", data=mpwriter)
    await _assess_response(resp)


async def _assess_response(resp: ClientResponse) -> None:
    assert resp.status == 200

    data = ""
    data_graph = ""
    results_text = ""
    results_graph = ""
    reader = MultipartReader.from_response(resp)
    while True:
        part = await reader.next()  # noqa: B305
        if part is None:
            break
        if part is None:
            break
        if part.name == "data":
            assert part.headers[hdrs.CONTENT_TYPE] == "text/plain; charset=utf-8"
            data = await part.text()
            continue
        if part.name == "data_graph":
            assert part.headers[hdrs.CONTENT_TYPE] == "text/turtle"
            data_graph = await part.text()
            continue
        if part.name == "results_text":
            assert part.headers[hdrs.CONTENT_TYPE] == "text/plain; charset=utf-8"
            results_text = await part.text()
            continue
        if part.name == "results_graph":
            assert part.headers[hdrs.CONTENT_TYPE] == "text/turtle"
            results_graph = await part.text()
            continue

    # We have all of the parts in the response. Lets test:
    # data should be equal to input:
    with open("tests/files/catalog_1.ttl", "r") as file:
        data_in = file.read()
    assert data == data_in

    # data_graph should in this case be equal to the data + inferred triples:
    g1 = Graph().parse(data=data_graph, format="turtle")
    g2 = Graph().parse("tests/files/data_graph.ttl", format="turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "data_graph is not equal to the input data"

    # results_text should contain "Conforms: True":
    assert "Conforms: True" in results_text

    # results_graph (validation report) should be isomorphic to the following:
    src = """
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    [] a sh:ValidationReport ;
         sh:conforms true
         .
    """
    g2 = Graph().parse(data=src, format="turtle")
    g1 = Graph().parse(data=results_graph, format="turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


# -- Bad cases


@pytest.mark.integration
async def test_validator_bad_syntax(client: _TestClient) -> None:
    """Should return status 400."""
    data = "Bad syntax. No turtle here."

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data)
        p.set_content_disposition("attachment", name="data")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400


@pytest.mark.integration
async def test_validator_empty(client: _TestClient) -> None:
    """Should return status 400."""
    data = "Bad syntax. No turtle here."

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data)
        p.set_content_disposition("attachment", name="data")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400


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
