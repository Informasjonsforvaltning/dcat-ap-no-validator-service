"""Resource module for liveness resources."""
import logging

from aiohttp import hdrs, web
from rdflib.plugin import PluginException

from dcat_ap_no_validator_service.service import ShapeService


class Shapes(web.View):
    """Class representing a collecion of shapes resource."""

    async def get(self) -> web.Response:
        """Shapes route function."""
        try:
            shapes = await ShapeService().get_all_shapes()
        except Exception as e:
            logging.error(f"Exception: {e}")
            raise web.HTTPInternalServerError

        logging.debug(f"accept header: {self.request.headers[hdrs.ACCEPT]}")
        accept_header = self.request.headers[hdrs.ACCEPT]
        # If no accept-header or if accept-header contains */*, we default to turtle:
        if hdrs.ACCEPT not in self.request.headers or "*/*" in accept_header:
            accept_header = "text/turtle"

        try:
            return web.Response(
                body=shapes.serialize(format=accept_header), content_type=accept_header
            )
        except PluginException:
            raise web.HTTPNotAcceptable


class Shape(web.View):
    """Class representing a single shape resource."""

    async def get(self) -> web.Response:
        """Shape route function."""
        id = self.request.match_info["id"]
        try:
            shape = await ShapeService().get_shape_by_id(id)
        except Exception as e:
            logging.error(f"Exception: {e}")
            raise web.HTTPInternalServerError

        if len(shape) == 0:
            raise web.HTTPNotFound

        logging.debug(f"accept header: {self.request.headers[hdrs.ACCEPT]}")
        accept_header = self.request.headers[hdrs.ACCEPT]
        # If no accept-header or if accept-header contains */*, we default to turtle:
        if hdrs.ACCEPT not in self.request.headers or "*/*" in accept_header:
            accept_header = "text/turtle"

        try:
            return web.Response(
                body=shape.serialize(format=accept_header), content_type=accept_header
            )
        except PluginException:
            raise web.HTTPNotAcceptable
