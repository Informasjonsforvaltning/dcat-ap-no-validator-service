"""Contract test cases for ready."""

from typing import Any

from aiohttp import ClientSession, hdrs
import pytest

# TODO find a way to automatically test openAPI spec


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_all_shapes(http_service: Any) -> None:
    """Should return 200 and a list of shapes."""
    url = f"{http_service}/shapes"

    session = ClientSession()
    async with session.get(url) as resp:
        body = await resp.json()
    await session.close()

    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    assert type(body) is dict
    assert "shapes" in body
    assert len(body["shapes"]) == 4
    for s in body["shapes"]:
        assert "id" in s, "No id property in shapes graph object"
        assert "name" in s, "No name property in shapes graph object"
        assert "description" in s, "No description property in shapes graph object"
        assert "version" in s, "No version property in shapes graph object"
        assert "url" in s, "No url property in shapes graph object"
        assert (
            "specificationName" in s
        ), "No specificationName property in shapes graph object"
        assert (
            "specificationVersion" in s
        ), "No specificationVersion property in shapes graph object"
        assert (
            "specificationUrl" in s
        ), "No specificationUrl property in shapes graph object"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_shape_by_id(http_service: Any) -> None:
    """Should return 200 and a shape description."""
    shape_id = 1
    url = f"{http_service}/shapes/{shape_id}"

    session = ClientSession()
    async with session.get(url) as resp:
        shape = await resp.json()
    await session.close()

    assert resp.status == 200
    assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
    assert type(shape) is dict
    assert "id" in shape, "No id property in shapes graph object"
    assert "name" in shape, "No name property in shapes graph object"
    assert "description" in shape, "No description property in shapes graph object"
    assert "version" in shape, "No version property in shapes graph object"
    assert "url" in shape, "No url property in shapes graph object"
    assert (
        "specificationName" in shape
    ), "No specificationName property in shapes graph object"
    assert (
        "specificationVersion" in shape
    ), "No specificationVersion property in shapes graph object"
    assert (
        "specificationUrl" in shape
    ), "No specificationUrl property in shapes graph object"
