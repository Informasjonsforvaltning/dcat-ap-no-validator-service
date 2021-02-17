"""Integration test cases for the graph_adapter."""
from collections import namedtuple

import pytest
from pytest_mock import MockFixture
from rdflib import Graph
from rdflib.compare import graph_diff

from dcat_ap_no_validator_service.adapter import fetch_graph


@pytest.mark.unit
async def test_fetch_graph_that_has_rdf_content_type(mocker: MockFixture) -> None:
    """Should return a non-empyt graph."""
    # Set up the mock
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.remote_graph_adapter.requests.get",
        return_value=_mock_rdf_response(),
    )
    url = "https://www.w3.org/ns/regorg"
    o = fetch_graph(url)
    assert type(o) == Graph
    assert len(o) > 0


@pytest.mark.unit
async def test_fetch_graph_that_does_not_have_rdf_content_type(
    mocker: MockFixture,
) -> None:
    """Should return a non-empty graph."""
    # Set up the mock
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.remote_graph_adapter.requests.get",
        return_value=_mock_rdf_with_non_standard_content_type_response(),
    )
    url = "https://data.norge.no/vocabulary/modelldcatno/modelldcatno.ttl"
    o = fetch_graph(url)
    assert type(o) == Graph
    assert len(o) > 0


@pytest.mark.unit
async def test_fetch_graph_that_is_not_parsable_as_rdf(mocker: MockFixture) -> None:
    """Should return an empty graph."""
    # Set up the mock
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.remote_graph_adapter.requests.get",
        return_value=_mock_no_response(),
    )
    url = "https://data.brreg.no/enhetsregisteret/api/enheter/961181399"
    o = fetch_graph(url)
    assert type(o) == Graph
    assert len(o) == 0


@pytest.mark.unit
async def test_fetch_graph_that_gives_unsuccessful_response(
    mocker: MockFixture,
) -> None:
    """Should return an empty graph."""
    # Set up the mock
    mocker.patch(
        "dcat_ap_no_validator_service.adapter.remote_graph_adapter.requests.get",
        return_value=_mock_non_parsable_response(),
    )
    url = "https://data.brreg.no/enhetsregisteret/api/enheter/961181399"
    o = fetch_graph(url)
    assert type(o) == Graph
    assert len(o) == 0


# --- mocks
def _mock_rdf_response() -> tuple:
    t = namedtuple("t", ("text", "status_code", "headers"))
    with open("tests/files/valid_catalog.ttl", "r") as file:
        text = file.read()
    return t(text=text, status_code=200, headers={"content-type": "text/turtle"})


def _mock_rdf_with_non_standard_content_type_response() -> tuple:
    t = namedtuple("t", ("text", "status_code", "headers"))
    with open("tests/files/valid_catalog.ttl", "r") as file:
        text = file.read()
    return t(text=text, status_code=200, headers={"content-type": "text/plain"})


def _mock_non_parsable_response() -> tuple:
    t = namedtuple("t", ("text", "status_code", "headers"))
    with open("tests/files/invalid_rdf.txt", "r") as file:
        text = file.read()
    return t(text=text, status_code=200, headers={"content-type": "application/json"})


def _mock_no_response() -> tuple:
    t = namedtuple("t", ("text", "status_code", "headers"))
    return t(text=None, status_code=406, headers=None)


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
