"""Contract test cases for ready."""
import json
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
    filename = "tests/files/valid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
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
    with open("tests/files/valid_catalog.ttl", "r") as file:
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


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_accept_json_ld(http_service: Any) -> None:
    """Should return OK and successful validation and content-type should be json-ld."""
    url = f"{http_service}/validator"
    filename = "tests/files/valid_catalog.ttl"
    headers = {"Accept": "application/ld+json"}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )

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
    with open(filename, "r") as file:
        text = file.read()

    g0 = Graph().parse(data=text, format="text/turtle")
    g1 = g0 + Graph().parse(data=src, format="application/ld+json")
    g2 = Graph().parse(data=body, format="application/ld+json")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_file_content_type_json_ld(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    filename = "tests/files/valid_catalog.json"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(
            open(filename, "rb"), {"CONTENT-TYPE": "application/ld+json"}
        )
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
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
    with open(filename, "r") as file:
        text = file.read()

    g0 = Graph().parse(data=text, format="application/ld+json")
    g1 = g0 + Graph().parse(data=src, format="text/turtle")
    g2 = Graph().parse(data=body, format="text/turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_file_content_type_rdf_xml(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    filename = "tests/files/valid_catalog.xml"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(
            open(filename, "rb"), {"CONTENT-TYPE": "application/rdf+xml"}
        )
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
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
    with open(filename, "r") as file:
        text = file.read()

    g0 = Graph().parse(data=text, format="application/rdf+xml")
    g1 = g0 + Graph().parse(data=src, format="text/turtle")
    g2 = Graph().parse(data=body, format="text/turtle")

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

    url_to_graph = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/valid_catalog.ttl"  # noqa: B950
    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url_to_graph)
        p.set_content_disposition("inline", name="data-graph-url")

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
    session = ClientSession()
    async with session.get(url_to_graph) as resp:
        text = await resp.text()
    await session.close()

    g0 = Graph().parse(data=text, format="text/turtle")
    g1 = g0 + Graph().parse(data=src, format="text/turtle")
    g2 = Graph().parse(data=body, format="text/turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_with_file_content_encoding(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    filename = "tests/files/valid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p.headers[hdrs.CONTENT_ENCODING] = "gzip"

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
    with open(filename, "r") as file:
        text = file.read()

    g0 = Graph().parse(data=text, format="text/turtle")
    g1 = g0 + Graph().parse(data=src, format="text/turtle")
    g2 = Graph().parse(data=body, format="text/turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_with_default_config(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    filename = "tests/files/valid_catalog.ttl"

    config = {"shapesId": "2", "expand": True, "includeExpandedTriples": False}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p.headers[hdrs.CONTENT_ENCODING] = "gzip"
        p = mpwriter.append(json.dumps(config))
        p.set_content_disposition("inline", name="config")

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
    with open(filename, "r") as file:
        text = file.read()

    g0 = Graph().parse(data=text, format="text/turtle")
    g1 = g0 + Graph().parse(data=src, format="text/turtle")
    g2 = Graph().parse(data=body, format="text/turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_with_file_and_shacl(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    graph = "tests/files/valid_catalog.ttl"
    shacl = "dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(graph, "rb"))
        p.set_content_disposition("attachment", name="data-graph-file", filename=graph)
        p = mpwriter.append(open(shacl, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shacl
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
    with open("tests/files/valid_catalog.ttl", "r") as file:
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


# --- bad cases ---
@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_with_not_valid_file(http_service: Any) -> None:
    """Should return OK and unsuccessful validation."""
    url = f"{http_service}/validator"
    filename = "tests/files/invalid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
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
        sh:conforms false ;
        sh:result [ a sh:ValidationResult ;
                sh:focusNode <http://dataset-publisher:8080/datasets/1> ;
                sh:resultMessage "Less than 1 values on <http://dataset-publisher:8080/datasets/1>->dcat:theme" ;
                sh:resultPath <http://www.w3.org/ns/dcat#theme> ;
                sh:resultSeverity sh:Violation ;
                sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
                sh:sourceShape [ sh:class <http://www.w3.org/2004/02/skos/core#Concept> ;
                        sh:minCount 1 ;
                        sh:path <http://www.w3.org/ns/dcat#theme> ;
                        sh:severity sh:Violation ] ],
            [ a sh:ValidationResult ;
                sh:focusNode <http://dataset-publisher:8080/datasets/1> ;
                sh:resultMessage "Less than 1 values on <http://dataset-publisher:8080/datasets/1>->dct:description" ;
                sh:resultPath <http://purl.org/dc/terms/description> ;
                sh:resultSeverity sh:Violation ;
                sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
                sh:sourceShape [ sh:minCount 1 ;
                        sh:nodeKind sh:Literal ;
                        sh:path <http://purl.org/dc/terms/description> ;
                        sh:severity sh:Violation ] ]
    .
    """
    with open(filename, "r") as file:
        text = file.read()

    g0 = Graph().parse(data=text, format="text/turtle")
    g1 = g0 + Graph().parse(data=src, format="text/turtle")
    g2 = Graph().parse(data=body, format="text/turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "results_graph is incorrect"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_notexisting_url(http_service: Any) -> None:
    """Should return 400."""
    url = f"{http_service}/validator"

    url_to_graph = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/does_not_exist.ttl"  # noqa: B950
    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url_to_graph)
        p.set_content_disposition("inline", name="data-graph-url")

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        _ = await resp.text()
    await session.close()

    assert resp.status == 400


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_illformed_url(http_service: Any) -> None:
    """Should return 400."""
    url = f"{http_service}/validator"

    url_to_graph = "http://slfkjasdf"  # noqa: B950
    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url_to_graph)
        p.set_content_disposition("inline", name="data-graph-url")

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        _ = await resp.text()
    await session.close()

    assert resp.status == 400


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_url_to_invalid_rdf(http_service: Any) -> None:
    """Should return 400."""
    url = f"{http_service}/validator"

    url_to_graph = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/invalid_rdf.txt"  # noqa: B950
    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url_to_graph)
        p.set_content_disposition("inline", name="data-graph-url")

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        _ = await resp.text()
    await session.close()

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
    for _l in g.serialize(format="text/turtle").splitlines():
        if _l:
            print(_l.decode())
