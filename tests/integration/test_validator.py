"""Integration test cases for the ready route."""
from collections import namedtuple
import json
import logging
from typing import Any, Dict

from aiohttp import hdrs, MultipartWriter
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from pytest_mock import MockFixture
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
from requests.exceptions import RequestException

from dcat_ap_no_validator_service.service import ShapesService

_MOCK_SHAPES_DB: Dict[str, Dict] = dict(
    {
        "1": {"id": "1", "name": "DCAT-AP-NO", "version": "1.1"},
        "2": {"id": "2", "name": "DCAT-AP-NO", "version": "2.0"},
    }
)


@pytest.fixture(scope="function")
def mocks(mocker: MockFixture) -> Any:
    """Patch the call to requests.get."""
    # Set up the mocks
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.remote_graph_adapter.requests.get",
        side_effect=_mock_response,
    )
    mocker.patch.object(ShapesService, "_SHAPES_DB", _MOCK_SHAPES_DB)


@pytest.mark.integration
async def test_validator_file_no_config(client: _TestClient, mocks: Any) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()
    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_empty_config(client: _TestClient, mocks: Any) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    config: dict = {}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_full_config_with_default_values(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    config: dict = {
        "expand": True,
        "includeExpandedTriples": False,
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_full_config_all_true(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    config: dict = {"expand": True, "includeExpandedTriples": False}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    g1 = Graph().parse(data_graph_file, format="text/turtle")
    g2 = Graph().parse(data=body, format="text/turtle")
    assert len(g2) > len(g1)


@pytest.mark.integration
async def test_validator_file_full_config_all_false(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    config: dict = {
        "expand": False,
        "includeExpandedTriples": False,
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_unsuccessful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_full_config_from_json_str(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and successful validation."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    config = """
    {
        "expand": true,
        "includeExpandedTriples": false
    }
    """

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append_json(json.loads(config))
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_content_negotiation_json_ld(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    accept = "application/ld+json"
    headers = {"Accept": accept}

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", headers=headers, data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == accept

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type=accept
    )


@pytest.mark.integration
async def test_validator_file_content_type_json_ld(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and successful validation."""
    data_graph_file = "tests/files/valid_catalog.json"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

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

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="application/ld+json", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_file_content_encoding(client: _TestClient, mocks: Any) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

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
        p.headers[hdrs.CONTENT_ENCODING] = "gzip"

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_data_graph_url(client: _TestClient, mocks: Any) -> None:
    """Should return status 200 and successful validation."""
    data_graph_url = "https://example.com/datagraphs/valid_catalog.ttl"
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    # need to get the text from url, which actually is content of file:
    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_url_to_json_ld_file(client: _TestClient, mocks: Any) -> None:
    """Should return status 200 and successful validation."""
    data_graph_url = "https://example.com/datagraphs/valid_catalog.json"
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"
    body = await resp.text()

    # need to get the text from url, which actually is content of file:
    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_successful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_graph_references_non_parsable_graph(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    data_graph_file = "tests/files/valid_catalog_references_non_parsable_graph.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    config: dict = {
        "expand": "true",
        "includeExpandedTriples": "false",
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_unsuccessful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_graph_references_no_response_graph(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    data_graph_file = "tests/files/valid_catalog_references_no_graph.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    config: dict = {
        "expand": "true",
        "includeExpandedTriples": "false",
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_unsuccessful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


@pytest.mark.integration
async def test_validator_graph_references_not_found_graph(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    data_graph_file = "tests/files/valid_catalog_references_not_found_graph.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    config: dict = {
        "expand": "true",
        "includeExpandedTriples": "false",
    }

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append_json(config)
        p.set_content_disposition("inline", name="config")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    assert resp.headers[hdrs.CONTENT_TYPE] == "text/turtle"

    body = await resp.text()

    with open(data_graph_file, "r") as file:
        text = file.read()
    await _assess_response_body_unsuccessful(
        data=text, format="text/turtle", body=body, content_type="text/turtle"
    )


# -- Bad cases
@pytest.mark.integration
async def test_validator_data_graph_url_and_file(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Multiple data graphs in input.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    data_graph_url = "http://example.com/graphs/1"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Multiple data graphs in input." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_shapes_graph_url_and_file(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Multiple shapes graphs in input.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_url = "http://example.com/graphs/1"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(shapes_graph_url)
        p.set_content_disposition("inline", name="shapes-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Multiple shapes graphs in input." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_no_shapes_graph(client: _TestClient, mocks: Any) -> None:
    r"""Should return status 400 and message \"No shapes graph in input.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "No shapes graph in input." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_no_data_graph(client: _TestClient, mocks: Any) -> None:
    r"""Should return status 400 and message \"No data graph in input.\"."""
    shapes_graph_file = "tests/files/valid_catalog.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "No data graph in input." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_empty_multipart(client: _TestClient, mocks: Any) -> None:
    r"""Should return status 400 and message \"No input.\"."""
    with MultipartWriter("mixed") as mpwriter:
        pass

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "No input." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_no_input(client: _TestClient, mocks: Any) -> None:
    r"""Should return status 415 and message \"multipart/* content type expected, got Content-Type\"."""
    resp = await client.post("/validator")
    assert resp.status == 415, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert (
        "multipart/* content type expected, got Content-Type" in body["detail"]
    ), "Wrong message."


@pytest.mark.integration
async def test_validator_file_accept_header_not_valid(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 406 and message \"Not Acceptable\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    content_type = "not_valid"
    headers = {"Accept": content_type}
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", headers=headers, data=mpwriter)
    assert resp.status == 406, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Not Acceptable" in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_data_graph_url_does_not_exist(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Data graph cannot be empty.\"."""
    data_graph_url = "https://example.com/graphs/not_found_graph"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Data graph cannot be empty." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_shapes_graph_url_does_not_exist(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Shapes graph cannot be empty.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_url = "https://example.com/graphs/not_found_graph"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(shapes_graph_url)
        p.set_content_disposition("inline", name="shapes-graph-url")
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Shapes graph cannot be empty." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_file_bad_syntax(client: _TestClient, mocks: Any) -> None:
    r"""Should return status 400 and message \"Multiple shapes graphs in input.\"."""
    data_graph_file = "tests/files/invalid_rdf.txt"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Bad syntax in input graph." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_data_graph_empty(client: _TestClient, mocks: Any) -> None:
    r"""Should return status 400 and message \"Data graph cannot be empty.\"."""
    data = ""
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data, {"CONTENT-TYPE": "text/turtle"})
        p.set_content_disposition("attachment", name="data-graph-file")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Data graph cannot be empty." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_connection_error_caused_by_bad_url(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Could not connect to http://slfkjasdf\"."""
    data_graph_url = "http://slfkjasdf"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Could not connect to http://slfkjasdf" in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_data_graph_url_references_not_found_url(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Data graph cannot be empty.\"."""
    data_graph_url = "https://example.com/graphs/not_found_graph"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(data_graph_url)
        p.set_content_disposition("inline", name="data-graph-url")
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Data graph cannot be empty." in body["detail"], "Wrong message."


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
    content_type = "text/plain"
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
        raise RequestException(f"Failure in name resolution for {url}")
    elif str(url) == "https://example.com/graphs/not_found_graph":
        status_code = 404
        content_type = "text/plain"
    elif str(url) == "https://example.com/non_parsable_graph":
        with open("tests/files/invalid_rdf.txt", "r") as file:
            text = file.read()
        status_code = 200
        content_type = "text/plain"
    elif str(url) == "https://example.com/datagraphs/valid_catalog.ttl":
        with open("tests/files/valid_catalog.ttl", "r") as file:
            text = file.read()
        status_code = 200
        content_type = "text/turtle"
    elif str(url) == "https://example.com/datagraphs/valid_catalog.json":
        with open("tests/files/valid_catalog.json", "r") as file:
            text = file.read()
        status_code = 200
        content_type = "application/ld+json"
    elif str(url) == "http://slfkjasdf":
        raise RequestException(f"Failure in name resolution for {url}")
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
