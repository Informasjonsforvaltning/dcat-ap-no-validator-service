"""Integration test cases for the ready route."""
from aiohttp import hdrs, MultipartReader, MultipartWriter
from aiohttp.test_utils import TestClient as _TestClient
import pytest
from rdflib import Graph


@pytest.mark.integration
async def test_validator(client: _TestClient) -> None:
    """Should return OK."""
    filename = "tests/files/catalog_1_plus.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition("attachment", name="file", filename=filename)

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    reader = MultipartReader.from_response(resp)
    while True:
        part = await reader.next()  # noqa: B305
        if part is None:
            break
        if part.name == "file_content":
            assert part.filename == filename
            assert part.headers[hdrs.CONTENT_TYPE] == "application/octet-stream"
            continue
        if part.name == "results_text":
            assert part.headers[hdrs.CONTENT_TYPE] == "text/plain; charset=utf-8"
            results_text = await part.text()
            assert "Conforms: True" in results_text
            continue
        if part.name == "results_graph":
            assert part.headers[hdrs.CONTENT_TYPE] == "text/turtle"
            results_graph = await part.text()
            print(results_graph)
            g = Graph().parse(data=results_graph, format="turtle")
            assert len(g) == 2
            continue


@pytest.mark.integration
async def test_validator_url(client: _TestClient) -> None:
    """Should return status 501."""
    url = "http://example.com/"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(url)
        p.set_content_disposition("attachment", name="url")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 501


@pytest.mark.integration
async def test_validator_text(client: _TestClient) -> None:
    """Should return status 501."""
    with open("tests/files/catalog_1_plus.ttl", "r") as file:
        text = file.read()

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(text)
        p.set_content_disposition("attachment", name="text")

    resp = await client.post("/validator", data=mpwriter)
    assert resp.status == 200
    reader = MultipartReader.from_response(resp)
    while True:
        part = await reader.next()  # noqa: B305
        if part is None:
            break
        if part.name == "results_text":
            assert part.headers[hdrs.CONTENT_TYPE] == "text/plain; charset=utf-8"
            results_text = await part.text()
            assert "Conforms: True" in results_text
            continue
        if part.name == "results_graph":
            assert part.headers[hdrs.CONTENT_TYPE] == "text/turtle"
            results_graph = await part.text()
            print(results_graph)
            g = Graph().parse(data=results_graph, format="turtle")
            assert len(g) == 2
            continue


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
