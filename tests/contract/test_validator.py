"""Contract test cases for ready."""
from typing import Any

from aiohttp import ClientSession, hdrs, MultipartReader, MultipartWriter
import pytest
from rdflib import Graph


@pytest.mark.asyncio
@pytest.mark.contract
async def test_validator(http_service: Any) -> None:
    """Should return OK."""
    url = f"{http_service}/validator"
    filename = "tests/files/catalog_1_plus.ttl"

    with MultipartWriter("mixed") as mpwriter:
        p = mpwriter.append(open(filename, "rb"))
        p.set_content_disposition("attachment", name="file", filename=filename)

    session = ClientSession()
    async with session.post(url, data=mpwriter) as resp:
        # ...
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
    await session.close()
