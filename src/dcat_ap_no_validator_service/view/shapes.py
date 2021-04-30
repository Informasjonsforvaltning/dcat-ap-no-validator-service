"""Resource module for shapes resources."""
from aiohttp import web

from dcat_ap_no_validator_service.adapter import ShapesGraphAdapter


class ShapesCollection(web.View):
    """Class representing a collecion of shapes resource."""

    async def get(self) -> web.Response:
        """Shapes route function."""
        response = dict()
        shapes = [x.__dict__ for x in await ShapesGraphAdapter.get_all()]
        response["shapes"] = shapes

        return web.json_response(response)


class Shapes(web.View):
    """Class representing a single shapes resource."""

    async def get(self) -> web.Response:
        """Shape route function."""
        id = self.request.match_info["id"]
        shape = await ShapesGraphAdapter.get_by_id(id)

        if shape:
            return web.json_response(shape.__dict__)
        raise web.HTTPNotFound
