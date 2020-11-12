"""Resource module for liveness resources."""
from typing import Any

from aiohttp import web
from rdflib import Graph


class Validator(web.View):
    """Class representing validator resource."""

    async def post(self) -> Any:
        """Ready route function."""
        data = await self.request.text()
        _ = Graph().parse(data=data, format="turtle")
        return web.Response(text="OK")
