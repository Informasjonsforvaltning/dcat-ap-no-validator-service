"""Contract test cases for ready."""
from typing import Any

from aiohttp import ClientSession, hdrs, MultipartWriter
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_with_file(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    filename = "tests/files/catalog_1.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition("attachment", name="file", filename=filename)

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        # ...
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
    g1 = Graph().parse(data=body, format="text/turtle")
    g2 = Graph().parse(data=src, format="text/turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_with_text(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    with open("tests/files/catalog_1.ttl", "r") as file:
        text = file.read()

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(text)
        p.set_content_disposition("inline", name="text")

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        # ...
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
    g1 = Graph().parse(data=body, format="text/turtle")
    g2 = Graph().parse(data=src, format="text/turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_json_ld(http_service: Any) -> None:
    """Should return OK and successful validation and content-type should be json-ld."""
    url = f"{http_service}/validator"
    filename = "tests/files/catalog_1.ttl"
    headers = {"Accept": "application/ld+json"}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition("attachment", name="file", filename=filename)

    session = ClientSession()
    async with session.post(url, headers=headers, data=mpwriter) as resp:
        # ...
        body = await resp.text()
    await session.close()

    assert resp.status == 200
    assert "application/ld+json" in resp.headers[hdrs.CONTENT_TYPE]

    # results_graph (validation report) should be isomorphic to the following:
    src = """
    [
      {
        "@type": [
          "http://www.w3.org/ns/shacl#ValidationReport"
        ],
        "http://www.w3.org/ns/shacl#conforms": [
          {
            "@value": true
          }
        ]
      },
      {
        "@id": "http://www.w3.org/ns/shacl#ValidationReport"
      }
    ]
    """
    g1 = Graph().parse(data=body, format="application/ld+json")
    g2 = Graph().parse(data=src, format="application/ld+json")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_url(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"

    url_to_graph = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/catalog_1.ttl"  # noqa: B950
    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url_to_graph)
        p.set_content_disposition("inline", name="url")

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        # ...
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

    g1 = Graph().parse(data=body, format="text/turtle")
    g2 = Graph().parse(data=src, format="text/turtle")

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
            print(_l.decode())
