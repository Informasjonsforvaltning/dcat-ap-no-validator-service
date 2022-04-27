"""Contract test cases for ready."""
from typing import Any

from aiohttp import ClientSession, hdrs, MultipartWriter
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_with_cpsv_ap_no(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    data_graph_file = "tests/files/valid_catalog_cpsv-ap-no.ttl"
    shapes_graph_file = "tests/files/mock_cpsv-ap-no_shacl_shapes_0.9.ttl"
    ontology_graph_file = "tests/files/cpsv-ap-no_ontologies.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append(open(ontology_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="ontology-graph-file", filename=ontology_graph_file
        )

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        body = await resp.text()
    await session.close()

    assert resp.status == 200
    assert "text/turtle" in resp.headers[hdrs.CONTENT_TYPE]

    # results_graph (validation report) should be isomorphic to the following:
    src = """
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    [] a sh:ValidationReport ;
         sh:conforms true
         .
    """
    with open("tests/files/valid_catalog_cpsv-ap-no.ttl", "r") as file:
        text = file.read()

    # body is graph of both the input data and the validation report
    g0 = Graph().parse(data=text, format="text/turtle")
    g1 = g0 + Graph().parse(data=src, format="turtle")
    g2 = Graph().parse(data=body, format="text/turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


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
    for _l in g.serialize(format="text/turtle").splitlines():
        if _l:
            print(_l)
