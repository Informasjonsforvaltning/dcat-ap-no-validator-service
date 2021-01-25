"""Resource module for liveness resources."""
import logging
import traceback

from aiohttp import ClientSession, hdrs, web
from rdflib import Graph
from rdflib.plugin import PluginException

from dcat_ap_no_validator_service.service import ValidatorService


class Validator(web.View):
    """Class representing validator resource."""

    async def post(self) -> web.Response:
        """Validate route function."""
        accept_header = self.request.headers["Accept"]
        logging.debug(f"Got following accept-headers: {accept_header}")
        # Iterate through each part of MultipartReader
        data = None
        version = None
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
                data, content_type = await get_graph_at_url(url)
                # Since we do not support text/plain, we assume turtle in this case:
                if "text/plain" in content_type:
                    content_type = "text/turtle"
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
                logging.debug(f"content of {filename}:\n{data}")
        # We have got data, now validate:
        try:
            service = ValidatorService(data, format=content_type, version=version)
            (
                conforms,
                data_graph,
                ontology_graph,
                results_graph,
            ) = await service.validate()

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
        response_graph = Graph()
        response_graph += results_graph
        response_graph += data_graph
        if False:  # Placeholder for client's choice
            response_graph += ontology_graph
        try:
            return web.Response(
                body=response_graph.serialize(format=format),
                content_type=format,
            )
        except PluginException:  # rdflib raises PluginException, in this context imples 406
            logging.error(traceback.format_exc())
            raise web.HTTPNotAcceptable()  # 406


async def get_graph_at_url(url: str) -> tuple:  # pragma: no cover
    """Get a graph to be validated at given url."""
    session = ClientSession()
    async with session.get(url) as resp:
        graph = await resp.text()
    await session.close()

    content_type = resp.headers[hdrs.CONTENT_TYPE]
    logging.debug(
        f"Got the following text from {url}/{resp.status}/{content_type}:\n {graph}"
    )
    # format is the first part of content_type:
    format = content_type.split(";")[0]

    return graph, format
