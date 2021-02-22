"""Resource module for liveness resources."""
from enum import Enum
import logging
import traceback

from aiohttp import hdrs, web
from rdflib import Graph
from rdflib.plugin import PluginException

from dcat_ap_no_validator_service.adapter import FetchError
from dcat_ap_no_validator_service.service import Config, ValidatorService


class Part(str, Enum):
    """Enum representing different valid part names."""

    CONFIG = "config"
    DATA_GRAPH_URL = "data-graph-url"
    DATA_GRAPH_FILE = "data-graph-file"
    SHAPES_GRAPH_FILE = "shapes-graph-file"
    SHAPES_GRAPH_URL = "shapes-graph-url"


class Validator(web.View):
    """Class representing validator resource."""

    async def post(self) -> web.Response:
        """Validate route function."""
        logging.debug(
            f"Got following content-type-headers: {self.request.headers[hdrs.CONTENT_TYPE]}"
        )
        if "multipart/" not in self.request.headers[hdrs.CONTENT_TYPE].lower():
            raise web.HTTPUnsupportedMediaType(
                reason=f"multipart/* content type expected, got {hdrs.CONTENT_TYPE}"
            )

        # Iterate through each part of MultipartReader
        data_graph_url = None
        data_graph = None
        shapes_graph = None
        shapes_graph_url = None
        config = None
        data_graph_matrix = dict()
        shapes_graph_matrix = dict()
        async for part in (await self.request.multipart()):
            logging.debug(f"part.name {part.name}")
            if Part(part.name) is Part.CONFIG:
                # Get config:
                config_json = await part.json()
                logging.debug(f"Got config: {config_json}")
                config = _create_config(config_json)
                pass

            if Part(part.name) is Part.DATA_GRAPH_URL:
                # Get data graph from url:
                data_graph_url = (await part.read()).decode()
                logging.debug(f"Got reference to data graph with url: {data_graph_url}")
                data_graph_matrix[part.name] = data_graph_url
                pass

            if Part(part.name) is Part.DATA_GRAPH_FILE:
                # Process any files you uploaded
                logging.debug(f"Got input data graph with filename: {part.filename}")
                data_graph = (await part.read()).decode()
                # logging.debug(f"Content of {part.filename}:\n{data_graph}")
                data_graph_matrix[part.name] = part.filename
                pass

            if Part(part.name) is Part.SHAPES_GRAPH_URL:
                # Get data graph from url:
                shapes_graph_url = (await part.read()).decode()
                logging.debug(
                    f"Got reference to shapes graph with url: {shapes_graph_url}"
                )
                shapes_graph_matrix[part.name] = shapes_graph_url
                pass

            if Part(part.name) is Part.SHAPES_GRAPH_FILE:
                # Process any files you uploaded
                logging.debug(f"Got input shapes graph with filename: {part.filename}")
                shapes_graph = (await part.read()).decode()
                # logging.debug(f"Content of {part.filename}:\n{shapes_graph}")
                shapes_graph_matrix[part.name] = part.filename
                pass

        # check if we got any input:
        # validate data-graph input:
        if len(data_graph_matrix) == 0:
            raise web.HTTPBadRequest(reason="No data graph in input.")
        elif len(data_graph_matrix) > 1:
            logging.debug(f"Ambigious user input: {data_graph_matrix}")
            raise web.HTTPBadRequest(reason="Multiple data graphs in input.")
        # validate shape-graph input:
        if len(shapes_graph_matrix) == 0:
            raise web.HTTPBadRequest(reason="No shapes graph in input.")
        elif len(shapes_graph_matrix) > 1:
            logging.debug(f"Ambigious user input: {shapes_graph_matrix}")
            raise web.HTTPBadRequest(reason="Multiple shapes graphs in input.")

        # We have got data, now validate:
        try:
            # instantiate validator service:
            service = ValidatorService(
                data_graph_url=data_graph_url,
                data_graph=data_graph,
                shapes_graph_url=shapes_graph_url,
                shapes_graph=shapes_graph,
                config=config,
            )
        except FetchError as e:
            logging.debug(traceback.format_exc())
            raise web.HTTPBadRequest(reason=str(e))
        except SyntaxError:
            logging.debug(traceback.format_exc())
            raise web.HTTPBadRequest(reason="Bad syntax in input graph.")

        try:
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

        # Try to content-negotiate:
        logging.debug(
            f"Got following accept-headers: {self.request.headers[hdrs.ACCEPT]}"
        )
        content_type = "text/turtle"  # default
        if "*/*" in self.request.headers[hdrs.ACCEPT]:
            pass  # use default
        elif self.request.headers[
            hdrs.ACCEPT
        ]:  # we try to serialize according to accept-header
            content_type = self.request.headers[hdrs.ACCEPT]
        response_graph = Graph()
        response_graph += results_graph
        response_graph += data_graph
        if config and config.include_expanded_triples is True:
            response_graph += ontology_graph
        try:
            return web.Response(
                body=response_graph.serialize(format=content_type),
                content_type=content_type,
            )
        except PluginException:  # rdflib raises PluginException, in this context imples 406
            logging.debug(traceback.format_exc())
            raise web.HTTPNotAcceptable()  # 406


def _create_config(config: dict) -> Config:
    c = Config()
    if "expand" in config:
        if config["expand"]:
            c.expand = True
        else:
            c.expand = False
    if "includeExpandedTriples" in config:
        if config["includeExpandedTriples"]:
            c.include_expanded_triples = True
        else:
            c.include_expanded_triples = False
    return c
