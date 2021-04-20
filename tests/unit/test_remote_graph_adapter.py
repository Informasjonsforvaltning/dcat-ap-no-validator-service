"""Integration test cases for the graph_adapter."""
from typing import Any

from aioresponses import aioresponses
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff

from dcat_ap_no_validator_service.adapter import fetch_graph, FetchError


@pytest.fixture
def mock_aioresponse() -> Any:
    """Set up aioresponses as fixture."""
    with aioresponses() as m:
        yield m


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_graph_that_has_rdf_content_type(mock_aioresponse: Any) -> None:
    """Should return a non-empyt graph."""
    url = "https://www.w3.org/ns/regorg"
    # Set up the mock
    mock_aioresponse.get(url, status=200, body=_mock_rdf_response())

    o = await fetch_graph(url)
    assert type(o) == Graph
    assert len(o) > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_graph_that_does_not_have_rdf_content_type(
    mock_aioresponse: Any,
) -> None:
    """Should return a non-empty graph."""
    url = "https://data.norge.no/vocabulary/modelldcatno/modelldcatno.ttl"
    # Set up the mock
    mock_aioresponse.get(
        url, status=200, body=_mock_rdf_with_non_standard_content_type_response()
    )

    o = await fetch_graph(url)
    assert type(o) == Graph
    assert len(o) > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_graph_that_is_not_parsable_as_rdf(mock_aioresponse: Any) -> None:
    """Should return None."""
    url = "https://data.brreg.no/enhetsregisteret/api/enheter/961181399"
    # Set up the mock
    mock_aioresponse.get(url, status=200, body=_mock_non_parsable_response())
    with pytest.raises(SyntaxError):
        _ = await fetch_graph(url)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_graph_that_gives_unsuccessful_response(
    mock_aioresponse: Any,
) -> None:
    """Should return None."""
    url = "https://data.brreg.no/enhetsregisteret/api/enheter/961181399"
    # Set up the mock
    mock_aioresponse.get(url, status=406)
    with pytest.raises(FetchError):
        _ = await fetch_graph(url)


# --- mocks
def _mock_rdf_response() -> str:
    with open("tests/files/valid_catalog.ttl", "r") as file:
        text = file.read()
    return text


def _mock_rdf_with_non_standard_content_type_response() -> str:
    with open("tests/files/valid_catalog.ttl", "r") as file:
        text = file.read()
    return text


def _mock_non_parsable_response() -> str:
    with open("tests/files/invalid_rdf.txt", "r") as file:
        text = file.read()
    return text


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
