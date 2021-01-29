"""Module for validator service."""
from dataclasses import dataclass
import logging
import traceback
from typing import Any, Tuple

from pyshacl import validate
from rdflib import Graph, RDF, URIRef
from rdflib.plugin import PluginException
import requests

from dcat_ap_no_validator_service.service import ShapeService

DEFAULT_SHACL_VERSION = "2"
SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


@dataclass
class Config:
    """Class for keeping track of config item."""

    shape_id: str = DEFAULT_SHACL_VERSION
    expand: bool = True
    include_expanded_triples: bool = False


class ValidatorService:
    """Class representing validator service."""

    __slots__ = (
        "graph",
        "format",
        "config",
        "ograph",
        "shacl",
    )

    def __init__(
        self,
        graph: Any,
        format: Any = None,
        config: Config = None,
        shacl: Any = None,
    ) -> None:
        """Initialize service instance."""
        self.format = format
        self.graph = parse_input_graph(graph, format)
        if config is None:
            self.config = Config()
        else:
            self.config = config
        self.ograph = Graph()
        self.shacl = shacl
        if self.shacl is not None:
            logging.debug("Got user supplied shacl")
            self.shacl = parse_input_graph(shacl)

    async def validate(self) -> Tuple[bool, Graph, Graph, Graph]:
        """Validate function."""
        # Do some sanity checks on preconditions:
        if len(self.graph) == 0:  # No need to validate empty graph
            raise ValueError("Input graph cannot be empty.")
        logging.debug(f"Validating with following config: {self.config}")
        if not self.shacl:
            self.shacl = await ShapeService().get_shape_by_id(self.config.shape_id)
        if len(self.shacl) == 0:  # No need to validate when empty shacl shapes
            raise ValueError("SHACL graph cannot be empty.")
        # Add triples from remote predicates if user has asked for that:
        if self.config.expand is True:
            self._expand_objects_triples()
            self._load_ontologies()
        # Validate!
        # `inference` should be set to one of the followoing {"none", "rdfs", "owlrl", "both"}
        conforms, results_graph, _ = validate(
            data_graph=self.graph,
            ont_graph=self.ograph,
            shacl_graph=self.shacl,
            inference="rdfs",
            inplace=False,
            meta_shacl=False,
            debug=False,
        )
        return (conforms, self.graph, self.ograph, results_graph)

    def _expand_objects_triples(self) -> None:
        """Get triples of objects and add to graph."""
        # TODO: this loop should be parallellized
        for p, o in self.graph.predicate_objects(subject=None):
            # logging.debug(f"{p} a {type(p)}, {o} a {type(o)}")
            if p == RDF.type:
                pass
            elif type(o) is URIRef:
                if (o, None, None) not in self.graph:
                    if (o, None, None) not in self.ograph:
                        logging.debug(f"trying to fetch triples about {o}")
                        try:
                            # Workaround to accomodate wrong content-type in responses:
                            # Should use Graph().parse(o) directly, but this approach
                            # breaks down when trying to fetch EU-triples:
                            headers = {"Accept": "text/turtle"}
                            resp = requests.get(o, headers=headers)
                            if resp.status_code == 200:
                                format = resp.headers["content-type"].split(";")[0]
                                if "text/xml" in format:
                                    format = "application/rdf+xml"
                                if "application/xml" in format:
                                    format = "application/rdf+xml"
                                t = Graph().parse(data=resp.text, format=format)
                                # Add the triples to the ontology graph:
                                self.ograph += t
                        except Exception:  # pragma: no cover
                            logging.debug(traceback.format_exc())
                            pass

    def _load_ontologies(self) -> None:
        """Load relevant ontologies into ograph."""
        # TODO: this loop should be parallellized
        # TODO: discover relevant ontologies dynamically, should be cached
        ontologies = ["https://www.w3.org/ns/regorg", "https://www.w3.org/ns/org"]
        for o in ontologies:
            if (o, None, None) not in self.ograph:
                logging.debug(f"Loading remote ontology {o}")
                try:
                    t = Graph().parse(o)
                    # Add the triples to the ontology graph:
                    self.ograph += t
                except Exception:  # pragma: no cover
                    logging.debug(traceback.format_exc())
                    pass


def parse_input_graph(input_graph: Any, format: Any = None) -> Graph:
    """Try to parse input_graph."""
    # If format is valid, we go ahead with parsing:
    if format and format.lower() in SUPPORTED_FORMATS:
        return Graph().parse(data=input_graph, format=format)
    # Else we try the valid format one after the other:
    else:
        for _format in SUPPORTED_FORMATS:
            # the following is flagged by S110 Try, Except, Pass. But there is
            # no easy way to catch specific errors from the parse function.
            # TODO: find a way to solve this without ignoring S110
            try:
                return Graph().parse(data=input_graph, format=_format)
            except Exception:
                pass
        # If we reached this point, we did not succeed with parsing:
        raise PluginException(f"Format not supported: {format}")
