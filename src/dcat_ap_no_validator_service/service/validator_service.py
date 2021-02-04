"""Module for validator service."""
from dataclasses import dataclass
import logging
from typing import Any, Tuple

from pyshacl import validate
from rdflib import Graph, RDF, URIRef


from dcat_ap_no_validator_service.adapter import fetch_graph, parse_text
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
        self.graph = parse_text(graph, format)
        if config is None:
            self.config = Config()
        else:
            self.config = config
        self.ograph = Graph()
        self.shacl = shacl
        if self.shacl is not None:
            logging.debug("Got user supplied shacl")
            self.shacl = parse_text(shacl)

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
        format = "turtle"
        logging.debug(
            f"Ready to validate graph:\n{self.graph.serialize(format=format).decode()}"
        )
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

    def _expand_objects_triples(self) -> None:  # pragma: no cover
        """Get triples of objects and add to graph."""
        # TODO: this loop should be parallellized
        for p, o in self.graph.predicate_objects(subject=None):
            # logging.debug(f"{p} a {type(p)}, {o} a {type(o)}")
            if p == RDF.type:
                pass
            elif type(o) is URIRef:
                if (o, None, None) not in self.graph:
                    if (o, None, None) not in self.ograph:
                        logging.debug(f"Trying to fetch remote triples about {o}")
                        g = fetch_graph(o)
                        self.ograph += g

    def _load_ontologies(self) -> None:
        """Load relevant ontologies into ograph."""
        # TODO: this loop should be parallellized
        # TODO: discover relevant ontologies dynamically, should be cached
        ontologies = ["https://www.w3.org/ns/regorg", "https://www.w3.org/ns/org"]
        for o in ontologies:
            if (o, None, None) not in self.ograph:
                logging.debug(f"Trying to add remote ontology {o}")
                g = fetch_graph(o)
                self.ograph += g
