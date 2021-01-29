"""Resource module for liveness resources."""
import logging
import traceback

from aiohttp import ClientConnectorError, ClientSession, hdrs, web
from multidict import MultiDict
from rdflib import Graph
from rdflib.plugin import PluginException

from dcat_ap_no_validator_service.service import Config, ValidatorService


class Validator(web.View):
    """Class representing validator resource."""

    async def post(self) -> web.Response:
        """Validate route function."""
        accept_header = self.request.headers["Accept"]
        logging.debug(f"Got following accept-headers: {accept_header}")
        # Iterate through each part of MultipartReader
        data = None
        config = None
        filename = None
        content_type = None
        shacl = None
        input_matrix = dict()
        async for part in (await self.request.multipart()):
            logging.debug(f"part.name {part.name}")
            if part.name == "config":
                # Get config:
                config_json = await part.json()
                logging.debug(f"Got config: {config_json}")
                config = _create_config(config_json)
                pass

            if part.name == "url":
                # Get data from url:
                url = (await part.read()).decode()
                logging.debug(f"Got reference to input graph with url: {url}")
                data, content_type = await get_graph_at_url(url)
                input_matrix[part.name] = url
                pass

            if part.name == "text":
                # Get data from text input:
                if part.headers[hdrs.CONTENT_TYPE]:
                    content_type = part.headers[hdrs.CONTENT_TYPE]
                    logging.debug(f"content_type of {content_type}")
                data = (await part.read()).decode()
                logging.debug(f"Got ingput graph as text: {data}")
                input_matrix[part.name] = "text"
                pass

            if part.name == "file":
                # Process any files you uploaded
                filename = part.filename
                logging.debug(f"got input graph as file with filename: {filename}")
                if part.headers[hdrs.CONTENT_TYPE]:
                    content_type = part.headers[hdrs.CONTENT_TYPE]
                    logging.debug(f"content_type of {content_type}")
                data = (await part.read()).decode()
                logging.debug(f"content of {filename}:\n{data}")
                input_matrix[part.name] = filename

            if part.name == "shacl-file":
                # Process any files you uploaded
                filename = part.filename
                logging.debug(f"got shacl from user with filename: {filename}")
                if part.headers[hdrs.CONTENT_TYPE]:
                    content_type = part.headers[hdrs.CONTENT_TYPE]
                    logging.debug(f"content_type of {content_type}")
                shacl = (await part.read()).decode()
                logging.debug(f"content of {filename}:\n{data}")

        if len(input_matrix) != 1:
            logging.debug(f"Ambigious user input: {input_matrix}")
            raise web.HTTPBadRequest(reason="Multiple inputs for validation.")

        # We have got data, now validate:
        try:
            # instantiate validator service:
            service = ValidatorService(
                graph=data, shacl=shacl, format=content_type, config=config
            )
            # validate:
            (
                conforms,
                data_graph,
                ontology_graph,
                results_graph,
            ) = await service.validate()

        except ValueError as e:
            logging.debug(traceback.format_exc())
            raise web.HTTPBadRequest(reason=str(e))

        except SyntaxError:
            logging.debug(traceback.format_exc())
            raise web.HTTPBadRequest(reason="Bad syntax in input graph.")

        except PluginException:
            logging.debug(traceback.format_exc())
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
        if config and config.include_expanded_triples is True:
            response_graph += ontology_graph
        try:
            return web.Response(
                body=response_graph.serialize(format=format),
                content_type=format,
            )
        except PluginException:  # rdflib raises PluginException, in this context imples 406
            logging.debug(traceback.format_exc())
            raise web.HTTPNotAcceptable()  # 406


async def get_graph_at_url(url: str) -> tuple:  # pragma: no cover
    """Get a graph to be validated at given url."""
    headers = MultiDict(
        [
            ("Accept", "text/turtle"),
            ("Accept", "application/rdf+xml"),
            ("Accept", "application/ld+json"),
        ]
    )
    session = ClientSession()
    try:
        async with session.get(url, headers=headers) as resp:
            graph = await resp.text()
        await session.close()
    except ClientConnectorError:
        logging.debug(traceback.format_exc())
        raise web.HTTPBadRequest(reason=f"Could not connect to url {url}")

    if resp.status != 200:
        raise web.HTTPBadRequest(
            reason=f'Got unsuccesful status code when requesting "{url}": {resp.status}'
        )

    content_type = resp.headers[hdrs.CONTENT_TYPE]
    logging.debug(
        f"Got the following text from {url}/{resp.status}/{content_type}:\n {graph}"
    )
    # format is the first part of content_type:
    format = content_type.split(";")[0]

    return graph, format


def _create_config(config: dict) -> Config:
    c = Config()
    if "shapeId" in config:
        c.shape_id = config["shapeId"]
    if "expand" in config:
        if config["expand"] == "true":
            c.expand = True
        else:
            c.expand = False
    if "includeExpandedTriples" in config:
        if config["includeExpandedTriples"] == "true":
            c.include_expanded_triples = True
        else:
            c.include_expanded_triples = False
    return c
