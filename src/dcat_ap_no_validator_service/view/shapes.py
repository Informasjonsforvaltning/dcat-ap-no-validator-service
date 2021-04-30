"""Resource module for shapes resources."""

from aiohttp import web

from dcat_ap_no_validator_service.service import ShapesService


class ShapesCollection(web.View):
    """Class representing a collecion of shapes resource."""

    async def get(self) -> web.Response:
        """Shapes route function."""
        shapes = await ShapesService().get_all_shapes()
        return web.json_response(shapes)


class Shapes(web.View):
    """Class representing a single shapes resource."""

    async def get(self) -> web.Response:
        """Shape route function."""
        id = self.request.match_info["id"]
        shape = await ShapesService().get_shapes_by_id(id)

        if shape:
            return web.json_response(shape)
        raise web.HTTPNotFound
