"""Resource module for liveness resources."""
import logging
import traceback

from aiohttp import web
from rdflib.plugin import PluginException

from dcat_ap_no_validator_service.service import ValidatorService


class Validator(web.View):
    """Class representing validator resource."""

    async def post(self) -> web.Response:
        """Validate route function."""
        accept_header = self.request.headers["Accept"]
        logging.debug(f"Got following accept-headers: {accept_header}")
        # Iterate through each field of MultipartReader
        data = ""
        version = ""
        filename = None
        async for field in (await self.request.multipart()):
            logging.debug(f"field.name {field.name}")
            if field.name == "version":
                # Do something about token
                version = (await field.read()).decode()
                logging.debug(f"Got version: {version}")
                pass

            if field.name == "url":
                # Do something about token
                url = (await field.read()).decode()
                logging.debug(f"Got url: {url}")
                raise web.HTTPNotImplemented
                pass

            if field.name == "text":
                # Do something about key
                data = (await field.read()).decode()
                logging.debug(f"Got text: {data}")
                pass

            if field.name == "file":
                # Process any files you uploaded
                filename = field.filename
                logging.debug(f"got filename: {filename}")
                # In your example, filename should be "2C80...jpg"
                data = (await field.read()).decode()
                logging.debug(f"content of {filename}: {data}")
        # We have got data, now validate:
        try:
            service = ValidatorService(data, version)
            conforms, data_graph, results_graph, results_text = await service.validate()

        except ValueError as e:
            logging.error(traceback.format_exc())
            raise web.HTTPBadRequest(reason=str(e))

        except SyntaxError:
            logging.error(traceback.format_exc())
            raise web.HTTPBadRequest(reason="Bad syntax in input graph.")

        # Try to content-negotiate:
        format = "text/turtle"  # default
        if "*/*" in accept_header:
            pass  # use default
        elif accept_header:  # we try to serialize according to accept-header
            format = accept_header

        try:
            return web.Response(
                body=results_graph.serialize(format=format),
                content_type=format,
            )
        except PluginException:
            logging.error(traceback.format_exc())
            raise web.HTTPNotAcceptable()
