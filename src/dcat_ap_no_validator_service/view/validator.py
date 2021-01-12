"""Resource module for liveness resources."""
import logging
import traceback

from aiohttp import ClientSession, hdrs, web
from rdflib.plugin import PluginException

from dcat_ap_no_validator_service.service import ValidatorService


class Validator(web.View):
    """Class representing validator resource."""

    async def post(self) -> web.Response:
        """Validate route function."""
        accept_header = self.request.headers["Accept"]
        logging.debug(f"Got following accept-headers: {accept_header}")
        # Iterate through each part of MultipartReader
        data = ""
        version = ""
        filename = None
        content_type = "text/turtle"  # default content
        async for part in (await self.request.multipart()):
            logging.debug(f"part.name {part.name}")
            if part.name == "version":
                # Get version of input from version:
                version = (await part.read()).decode()
                logging.debug(f"Got version: {version}")
                pass

            if part.name == "url":
                # Get data from url:
                url = (await part.read()).decode()
                logging.debug(f"Got url: {url}")
                data = await get_graph_at_url(url)
                pass

            if part.name == "text":
                # Get data from text input:
                if part.headers[hdrs.CONTENT_TYPE]:
                    content_type = part.headers[hdrs.CONTENT_TYPE]
                    logging.debug(f"content_type of {content_type}")
                data = (await part.read()).decode()
                logging.debug(f"Got text: {data}")
                pass

            if part.name == "file":
                # Process any files you uploaded
                filename = part.filename
                logging.debug(f"got filename: {filename}")
                if part.headers[hdrs.CONTENT_TYPE]:
                    content_type = part.headers[hdrs.CONTENT_TYPE]
                    logging.debug(f"content_type of {content_type}")
                data = (await part.read()).decode()
                logging.debug(f"content_type of {filename}: {data}")
        # We have got data, now validate:
        try:
            service = ValidatorService(data, format=content_type, version=version)
            conforms, data_graph, results_graph, results_text = await service.validate()

        except ValueError as e:
            logging.error(traceback.format_exc())
            raise web.HTTPBadRequest(reason=str(e))

        except SyntaxError:
            logging.error(traceback.format_exc())
            raise web.HTTPBadRequest(reason="Bad syntax in input graph.")

        except PluginException:
            logging.error(traceback.format_exc())
            raise web.HTTPUnsupportedMediaType(
                reason=f"Input graph format not supported: {content_type}"
            )

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
        except PluginException:  # rdflib raises PluginException, in this context imples 406
            logging.error(traceback.format_exc())
            raise web.HTTPNotAcceptable()  # 406


async def get_graph_at_url(url: str) -> str:
    """Get a graph to be validated at given url."""
    session = ClientSession()
    async with session.get(url) as resp:
        graph = await resp.text()
    await session.close()

    logging.debug(f"Got the following text from {url}/{resp.status}:\n {graph}")

    return graph
