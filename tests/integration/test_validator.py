"""Integration test cases for the ready route."""
import json
from typing import Any, Dict


from aiohttp import ClientError, hdrs, MultipartWriter
from aiohttp.test_utils import TestClient as _TestClient
from aioresponses import aioresponses
import pytest
from pytest_mock import MockFixture
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic

from dcat_ap_no_validator_service.service import ShapesService

_MOCK_SHAPES_STORE: Dict[str, Dict] = dict(
    {
        "1": {"id": "1", "name": "DCAT-AP-NO", "version": "1.1"},
        "2": {"id": "2", "name": "DCAT-AP-NO", "version": "2.0"},
    }
)


@pytest.fixture
def mock_aioresponse() -> Any:
    """Set up aioresponses as fixture."""
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        yield m


@pytest.fixture(scope="function")
def mocks(mock_aioresponse: Any, mocker: MockFixture) -> Any:
    """Patch the calls to aiohttp.Client.get."""
    # Set up the mocks
    with open("tests/files/mock_organization_catalogue_961181399.ttl", "r") as file:
        org_961181399 = file.read()
    mock_aioresponse.get(
        "https://organization-catalogue.fellesdatakatalog.digdir.no/organizations/961181399",
        body=org_961181399,
    )
    with open("tests/files/mock_los_tema_barnehage.xml", "r") as file:
        los = file.read()
    mock_aioresponse.get(
        "https://psi.norge.no/los/tema/barnehage",
        body=los,
    )
    with open("tests/files/mock_data_theme_GOVE.xml", "r") as file:
        theme = file.read()
    mock_aioresponse.get(
        "http://publications.europa.eu/resource/authority/data-theme/GOVE",
        body=theme,
    )
    with open("tests/files/mock_organization_catalogue_991825827.ttl", "r") as file:
        org_991825827 = file.read()
    mock_aioresponse.get(
        "https://organization-catalogue.fellesdatakatalog.digdir.no/organizations/991825827",
        body=org_991825827,
    )
    with open("tests/files/mock_regorg.ttl", "r") as file:
        regorg = file.read()
    mock_aioresponse.get(
        "https://www.w3.org/ns/regorg",
        body=regorg,
    )
    with open("tests/files/mock_org.ttl", "r") as file:
        org = file.read()
    mock_aioresponse.get(
        "https://www.w3.org/ns/org",
        body=org,
    )
    mock_aioresponse.get(
        "https://example.com/graphs/not_found_graph",
        status=404,
    )
    mock_aioresponse.get(
        "http://slfkjasdf",
        exception=ClientError("Failure in name resolution for http://slfkjasdf"),
    )
    mock_aioresponse.get(
        "https://example.com/nograph",
        exception=ClientError(
            "Failure in name resolution for https://example.com/nograph"
        ),
    )
    with open("tests/files/invalid_rdf.txt", "r") as file:
        invalid_rdf = file.read()
    mock_aioresponse.get(
        "https://example.com/non_parsable_graph",
        body=invalid_rdf,
    )
    with open("tests/files/valid_catalog.json", "r") as file:
        valid_catalog_json = file.read()
    mock_aioresponse.get(
        "https://example.com/datagraphs/valid_catalog.json",
        body=valid_catalog_json,
    )
    with open("tests/files/valid_catalog.ttl", "r") as file:
        valid_catalog = file.read()
    mock_aioresponse.get(
        "https://example.com/datagraphs/valid_catalog.ttl",
        body=valid_catalog,
    )
    with open("tests/files/mock_org-status.ttl", "r") as file:
        valid_catalog = file.read()
    mock_aioresponse.get(
        "https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalogue/master/src/main/resources/ontology/org-status.ttl",  # noqa
        body=valid_catalog,
    )
    with open(
        "tests/files/mock_publications_europa_eu_resource_authority_licence.xml", "r"
    ) as file:
        valid_catalog = file.read()
    mock_aioresponse.get(
        "http://publications.europa.eu/resource/authority/licence",  # noqa
        body=valid_catalog,
    )
    mock_aioresponse.get(
        "http://example.com/accessURL",
        status=404,
    )
    mock_aioresponse.get(
        "http://publications.europa.eu/ontology/euvoc",
        status=404,
    )
    # Patch the Shapes graph store:
    mocker.patch.object(ShapesService, "_SHAPES_STORE", _MOCK_SHAPES_STORE)


@pytest.mark.integration
async def test_validator_file_no_config(client: _TestClient, mocks: Any) -> None:
    """Should return OK."""
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
    ontology_graph_file = "tests/files/ontologies.ttl"
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
        p = mpwriter.append(open(ontology_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="ontology-graph-file", filename=ontology_graph_file
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
async def test_validator_file_full_config_with_default_values(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"
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
        p = mpwriter.append(open(ontology_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="ontology-graph-file", filename=ontology_graph_file
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
async def test_validator_file_full_config_all_true(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"
    config: dict = {"expand": True, "includeExpandedTriples": True}

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
        p = mpwriter.append(open(ontology_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="ontology-graph-file", filename=ontology_graph_file
        )

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
    ontology_graph_file = "tests/files/ontologies.ttl"
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
        p = mpwriter.append(open(ontology_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="ontology-graph-file", filename=ontology_graph_file
        )

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
    ontology_graph_file = "tests/files/ontologies.ttl"
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
        p = mpwriter.append(open(ontology_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="ontology-graph-file", filename=ontology_graph_file
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
async def test_validator_file_content_negotiation_json_ld(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontologies.ttl"
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
        p = mpwriter.append(open(ontology_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="ontology-graph-file", filename=ontology_graph_file
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
        p.headers[hdrs.CONTENT_ENCODING] = "gzip"
        p = mpwriter.append(open(ontology_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="ontology-graph-file", filename=ontology_graph_file
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
async def test_validator_data_graph_url(client: _TestClient, mocks: Any) -> None:
    """Should return status 200 and successful validation."""
    data_graph_url = "https://example.com/datagraphs/valid_catalog.ttl"
    data_graph_file = "tests/files/valid_catalog.ttl"
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
async def test_validator_data_graph_references_non_parsable_graph(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    data_graph_file = "tests/files/valid_catalog_references_non_parsable_graph.ttl"
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
async def test_validator_graph_contains_distribution_with_eu_licence(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and successful validation."""
    data_graph_file = "tests/files/valid_catalog_with_distribution.ttl"
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
async def test_validator_ontology_graph_imports_non_reachable_ontology(
    client: _TestClient, mocks: Any
) -> None:
    """Should return OK and unsuccessful validation."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/ontology_imports_non_reachable_ontology.ttl"

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
    r"""Should return status 400 and message \"Could not fetch remote graph from {url}\"."""
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
    assert (
        f"Could not fetch remote graph from {data_graph_url}." in body["detail"]
    ), "Wrong message."


@pytest.mark.integration
async def test_validator_shapes_graph_url_does_not_exist(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Could not fetch remote graph from {url}.\"."""
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
    assert (
        f"Could not fetch remote graph from {shapes_graph_url}." in body["detail"]
    ), "Wrong message."


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
async def test_validator_data_graph_url_bad_syntax(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Bad syntax in graph {url}.\"."""
    data_graph_url = "https://example.com/non_parsable_graph"
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
    assert f"Bad syntax in graph {data_graph_url}." in body["detail"], "Wrong message."


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
async def test_validator_shapes_graph_empty(client: _TestClient, mocks: Any) -> None:
    r"""Should return status 400 and message \"Shapes graph cannot be empty.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph = ""

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(shapes_graph, {"CONTENT-TYPE": "text/turtle"})
        p.set_content_disposition("attachment", name="shapes-graph-file")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Shapes graph cannot be empty." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_connection_error_caused_by_bad_url(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Could not fetch remote graph from http://slfkjasdf\"."""
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
    assert (
        f"Could not fetch remote graph from {data_graph_url}." in body["detail"]
    ), "Wrong message."


@pytest.mark.integration
async def test_validator_data_graph_file_file_not_readable(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Data graph file is not readable.\"."""
    data_graph_file = "tests/files/not_readable_file.pdf"
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
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Data graph file is not readable." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_shapes_graph_file_file_not_readable(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Shapes graph file is not readable.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/not_readable_file.pdf"

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
    assert "Shapes graph file is not readable." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_ontology_graph_url_bad_syntax(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Bad syntax in graph {url}.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_url = "https://example.com/non_parsable_graph"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append(ontology_graph_url)
        p.set_content_disposition("inline", name="ontology-graph-url")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert (
        f"Bad syntax in graph {ontology_graph_url}." in body["detail"]
    ), "Wrong message."


@pytest.mark.integration
async def test_validator_ontology_graph_file_not_readable(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Ontology graph file is not readable.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_file = "tests/files/not_readable_file.pdf"

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

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert "Ontology graph file is not readable." in body["detail"], "Wrong message."


@pytest.mark.integration
async def test_validator_ontology_graph_url_references_no_response_graph(
    client: _TestClient, mocks: Any
) -> None:
    r"""Should return status 400 and message \"Could not fetch remote graph from {url}.\"."""
    data_graph_file = "tests/files/valid_catalog.ttl"
    shapes_graph_file = "tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl"
    ontology_graph_url = "http://slfkjasdf"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(data_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="data-graph-file", filename=data_graph_file
        )
        p = mpwriter.append(open(shapes_graph_file, "rb"))
        p.set_content_disposition(
            "attachment", name="shapes-graph-file", filename=shapes_graph_file
        )
        p = mpwriter.append(ontology_graph_url)
        p.set_content_disposition("inline", name="ontology-graph-url")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 400, "Wrong status code."
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE], "Wrong content-type."

    body = await resp.json()
    assert (
        f"Could not fetch remote graph from {ontology_graph_url}." in body["detail"]
    ), "Wrong message."


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
