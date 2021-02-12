"""Integration test cases for the ready route."""
from collections import namedtuple
import logging
from typing import Any

from aiohttp import hdrs, MultipartWriter
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from pytest_mock import MockFixture
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic


@pytest.fixture(scope="function")
def mocked_response(mocker: MockFixture) -> Any:
    """Patch the call to requests.get."""
    # Set up the mock
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.remote_graph_adapter.requests.get",
        side_effect=_mock_response,
    )


@pytest.mark.integration
async def test_validator_file_no_config(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK."""
    filename = "tests/files/valid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()
    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_empty_config(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK."""
    filename = "tests/files/valid_catalog.ttl"
    config: dict = {}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_full_config_with_default_values(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK."""
    filename = "tests/files/valid_catalog.ttl"
    config: dict = {
        "shapeId": "2",
        "expand": "true",
        "includeExpandedTriples": "false",
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_full_config_all_true(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK."""
    filename = "tests/files/valid_catalog.ttl"
    config: dict = {"shapeId": "2", "expand": "true", "includeExpandedTriples": "true"}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    g1 = Graph().parse(filename, format="text/turtle")
    g2 = Graph().parse(data=body, format="text/turtle")
    assert len(g2) > len(g1)


@pytest.mark.integration
async def test_validator_file_full_config_all_false(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    filename = "tests/files/valid_catalog.ttl"
    config: dict = {
        "shapeId": "2",
        "expand": "false",
        "includeExpandedTriples": "false",
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_unsuccessful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_content_negotiation_json_ld(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK."""
    filename = "tests/files/valid_catalog.ttl"
    accept = "application/ld+json"
    headers = {"Accept": accept}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )

    resp = await client.post("/validator", headers=headers, data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == accept

    body = await resp.text()

    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type=accept
    )


@pytest.mark.integration
async def test_validator_file_content_type_json_ld(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK and successful validation."""
    filename = "tests/files/valid_catalog.json"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(
            open(filename, "rb"), {"CONTENT-TYPE": "application/ld+json"}
        )
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="application/ld+json", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_content_encoding(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK."""
    filename = "tests/files/valid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p.headers[hdrs.CONTENT_ENCODING] = "gzip"

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_url(client: _TestClient, mocked_response: Any) -> None:
    """Should return status 200 and successful validation."""
    url_to_graph = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/valid_catalog.ttl"  # noqa: B950
    filename = "tests/files/valid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url_to_graph)
        p.set_content_disposition("inline", name="data-graph-url")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    # need to get the text from url, which actually is content of file:
    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_url_to_json_ld_file(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status 200 and successful validation."""
    url_to_graph = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/valid_catalog.json"  # noqa: B950
    filename = "tests/files/valid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url_to_graph)
        p.set_content_disposition("inline", name="data-graph-url")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    # need to get the text from url, which actually is content of file:
    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_text(client: _TestClient, mocked_response: Any) -> None:
    """Should return status 200 and turtle body."""
    with open("tests/files/valid_catalog.ttl", "r") as file:
        text = file.read()

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(text, {"CONTENT-TYPE": "text/turtle"})
        p.set_content_disposition("inline", name="data-graph-text")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_text_format_json_ld(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status 200 and turtle body."""
    with open("tests/files/valid_catalog.json", "r") as file:
        text = file.read()

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(text, {"CONTENT-TYPE": "application/ld+json"})
        p.set_content_disposition("inline", name="data-graph-text")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    await _assess_response_body_successful(
        data=text, format="application/ld+json", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_text_supported_content_unsupported_content_type(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status 200."""
    with open("tests/files/valid_catalog.json", "r") as file:
        text = file.read()

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(text, {"CONTENT-TYPE": "unsupported/content+type"})
        p.set_content_disposition("inline", name="data-graph-text")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    await _assess_response_body_successful(
        data=text, format="application/ld+json", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_text_no_content_type(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status 200."""
    with open("tests/files/valid_catalog.json", "r") as file:
        text = file.read()

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(text)
        p.set_content_disposition("inline", name="data-graph-text")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    await _assess_response_body_successful(
        data=text, format="application/ld+json", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_and_shacl(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK."""
    graph = "tests/files/valid_catalog.ttl"
    shacl = "dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(graph, "rb"))
        p.set_content_disposition("attachment", name="data-graph-file", filename=graph)
        p = mpwriter.append(open(shacl, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shacl
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()
    with open("tests/files/valid_catalog.ttl", "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_graph_references_non_parsable_graph(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    filename = "tests/files/valid_catalog_references_non_parsable_graph.ttl"
    config: dict = {
        "shapeId": "2",
        "expand": "true",
        "includeExpandedTriples": "false",
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_unsuccessful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_graph_references_no_response_graph(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    filename = "tests/files/valid_catalog_references_no_graph.ttl"
    config: dict = {
        "shapeId": "2",
        "expand": "true",
        "includeExpandedTriples": "false",
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(filename, "r") as file:
        text = file.read()
    await _assess_response_body_unsuccessful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


# -- Bad cases
@pytest.mark.integration
async def test_validator_url_and_file(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status 400."""
    filename = "tests/files/valid_catalog.ttl"
    url_to_graph = "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no-validator-service/main/tests/files/valid_catalog.ttl"  # noqa: B950

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url_to_graph)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400


@pytest.mark.integration
async def test_validator_file_accept_header_not_valid(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status_code 406."""
    filename = "tests/files/valid_catalog.ttl"
    content_type = "not_valid"
    headers = {"Accept": content_type}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )

    resp = await client.post("/validator", headers=headers, data=mpwriter)
    assert resp.status == 406


@pytest.mark.integration
async def test_validator_file_not_existing_shacl(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status_code 406."""
    filename = "tests/files/valid_catalog.ttl"
    config: dict = {"shapeId": "not_existing"}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400


@pytest.mark.integration
async def test_validator_bad_syntax_valid_content_type(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status 400."""
    data = "Bad syntax. No turtle here."

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data, {"CONTENT-TYPE": "text/turtle"})
        p.set_content_disposition("attachment", name="data-graph-text")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400


@pytest.mark.integration
async def test_validator_file_bad_syntax_no_content_type(
    client: _TestClient, mocked_response: Any
) -> None:
    """Should return status 415."""
    filename = "tests/files/invalid_rdf.txt"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=filename
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 415


@pytest.mark.integration
async def test_validator_empty(client: _TestClient, mocked_response: Any) -> None:
    """Should return status 400."""
    data = ""

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data, {"CONTENT-TYPE": "text/turtle"})
        p.set_content_disposition("attachment", name="data-graph-text")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400


# -- Helper methods


async def _assess_response_body_successful(
    data: str, format: str, body: str, content_type: Any = "text/turtle"
) -> None:

    # body (validation report) should be isomorphic to the following:
    src = """
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    [] a sh:ValidationReport ;
         sh:conforms true
         .
    """
    g0 = Graph().parse(data=data, format=format)
    g1 = g0 + Graph().parse(data=src, format="turtle")
    g2 = Graph().parse(data=body, format=content_type)

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "result_graph is not correct"


async def _assess_response_body_unsuccessful(
    data: str, format: str, body: str, content_type: Any = "text/turtle"
) -> None:

    # body (validation report) should be isomorphic to the following:
    src = """
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    [] a sh:ValidationReport ;
         sh:conforms true
         .
    """
    g0 = Graph().parse(data=data, format=format)
    g1 = g0 + Graph().parse(data=src, format="turtle")
    g2 = Graph().parse(data=body, format=content_type)

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert not _isomorphic, "result_graph is not correct"


# ------------------ #
# Mocks


def _mock_response(url: str, headers: dict) -> tuple:
    """Return mocked response depending on input url."""
    t = namedtuple("t", ("text", "status_code", "headers"))
    text = ""
    status_code = 200
    content_type = None
    # breakpoint()
    logging.debug(f"Got request for url {url}")
    if (
        str(url)
        == "https://organization-catalogue.fellesdatakatalog.digdir.no/organizations/961181399"
    ):
        with open("tests/files/mock_organization_catalogue_961181399.ttl", "r") as file:
            text = file.read()
        content_type = "text/turtle"
    elif (
        str(url)
        == "https://organization-catalogue.fellesdatakatalog.digdir.no/organizations/991825827"
    ):
        with open("tests/files/mock_organization_catalogue_991825827.ttl", "r") as file:
            text = file.read()
        content_type = "text/turtle"
    elif str(url) == "http://publications.europa.eu/resource/authority/data-theme/GOVE":
        with open("tests/files/mock_data_theme_GOVE.xml", "r") as file:
            text = file.read()
        content_type = "application/rdf+xml"
    elif str(url) == "https://psi.norge.no/los/tema/barnehage":
        with open("tests/files/mock_los_tema_barnehage.xml", "r") as file:
            text = file.read()
        content_type = "application/rdf+xml"
    elif str(url) == "https://www.w3.org/ns/regorg":
        with open("tests/files/mock_regorg.ttl", "r") as file:
            text = file.read()
        content_type = "text/turtle"
    elif str(url) == "https://www.w3.org/ns/org":
        with open("tests/files/mock_org.ttl", "r") as file:
            text = file.read()
        content_type = "text/turtle"
    elif str(url) == "https://data.brreg.no/enhetsregisteret/api/enheter/961181399":
        with open("tests/files/mock_enhetsregisteret_961181399.json", "r") as file:
            text = file.read()
        content_type = "application/json"
    elif str(url) == "https://data.brreg.no/enhetsregisteret/api/enheter/991825827":
        with open("tests/files/mock_enhetsregisteret_991825827.json", "r") as file:
            text = file.read()
        content_type = "application/json"
    elif str(url) == "https://example.com/nograph":
        status_code = 406
    elif str(url) == "https://example.com/non_parsable_graph":
        with open("tests/files/invalid_rdf.txt", "r") as file:
            text = file.read()
        status_code = 200
        content_type = "text/plain"
    else:
        raise Exception(f"Not able to return mock response for url {url}")
    return t(text=text, status_code=status_code, headers={"content-type": content_type})


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
