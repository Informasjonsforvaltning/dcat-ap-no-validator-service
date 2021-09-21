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
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

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
    data_graph_file = "tests/files/valid_catalog.ttl"
    headers = {"Accept": "application/ld+json"}
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

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
    with open(data_graph_file, "r") as file:
        text = file.read()

    g0 = Graph().parse(data=text, format="text/turtle")
    g1 = g0 + Graph().parse(data=src, format="json-ld")
    g2 = Graph().parse(data=body, format="json-ld")

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
    data_graph_file = "tests/files/valid_catalog.json"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(
            open(data_graph_file, "rb"), {"CONTENT-TYPE": "application/ld+json"}
        )
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
    with open(data_graph_file, "r") as file:
        text = file.read()

    g0 = Graph().parse(data=text, format="json-ld")
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
    data_graph_file = "tests/files/valid_catalog.xml"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(
            open(data_graph_file, "rb"), {"CONTENT-TYPE": "application/rdf+xml"}
        )
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
    with open(data_graph_file, "r") as file:
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

    data_graph_url = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/valid_catalog.ttl"  # noqa: B950
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
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
    session = ClientSession()
    async with session.get(data_graph_url) as resp:
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
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p.headers[hdrs.CONTENT_ENCODING] = "gzip"
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
    with open(data_graph_file, "r") as file:
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
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

    config = {"expand": True, "includeExpandedTriples": False}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p.headers[hdrs.CONTENT_ENCODING] = "gzip"
        p = mpwriter.append(json.dumps(config))
        p.set_content_disposition("inline", name="config")
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
    with open(data_graph_file, "r") as file:
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
async def test_validator_with_file_and_shapes_graph_file(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

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
    data_graph_file = "tests/files/invalid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"

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
                        sh:severity sh:Violation ] ],
            [ a sh:ValidationResult ;
                sh:focusNode <http://dataset-publisher:8080/datasets/1> ;
                sh:resultMessage "Data-themes fra EU skal brukes for dcat:theme"@nb ;
                sh:resultPath <http://www.w3.org/ns/dcat#theme> ;
                sh:resultSeverity sh:Warning ;
                sh:sourceConstraintComponent sh:QualifiedMinCountConstraintComponent ;
                sh:sourceShape [ sh:message "Data-themes fra EU skal brukes for dcat:theme"@nb ;
                        sh:path <http://www.w3.org/ns/dcat#theme> ;
                        sh:qualifiedMinCount 1 ;
                        sh:qualifiedValueShape [ sh:node <https://data.norge.no/specification/dcat-ap-no/#DataThemeRestriction> ] ;
                        sh:severity sh:Warning ] ]
    .
    """
    with open(data_graph_file, "r") as file:
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

    data_graph_url = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/does_not_exist.ttl"  # noqa: B950
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

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

    data_graph_url = "http://slfkjasdf"  # noqa: B950
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

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

    data_graph_url = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/invalid_rdf.txt"  # noqa: B950
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        _ = await resp.text()
    await session.close()

    assert resp.status == 400


@pytest.mark.contract
@pytest.mark.asyncio
async def test_validator_with_skos_ap_no(http_service: Any) -> None:
    """Should return OK and successful validation."""
    url = f"{http_service}/validator"
    data_graph_file = "tests/files/valid_collection.ttl"
    shapes_graph_file = "tests/files/mock_skos-ap-no-shacl_shapes.ttl"
    ontology_graph_file = "tests/files/skos_ontologies.ttl"

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
    with open("tests/files/valid_collection.ttl", "r") as file:
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
