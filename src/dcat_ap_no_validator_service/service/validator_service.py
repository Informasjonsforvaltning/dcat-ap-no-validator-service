"""Module for validator service."""
from dataclasses import dataclass
import logging
from typing import Any, Tuple

from pyshacl import validate
from rdflib import Graph, RDF, URIRef


from dcat_ap_no_validator_service.adapter import fetch_graph, parse_text
from dcat_ap_no_validator_service.service import ShapesService

DEFAULT_SHAPE_GRAPH = "2"
SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


@dataclass
class Config:
    """Class for keeping track of config item."""

    shapes_id: str = DEFAULT_SHAPE_GRAPH
    expand: bool = True
    include_expanded_triples: bool = False


class ValidatorService:
    """Class representing validator service."""

    __slots__ = (
        "url",
        "data",
        "shapes",
        "config",
        "ontology",
    )

    def __init__(
        self,
        url: Any,
        data: Any,
        shapes: Any,
        config: Config = None,
    ) -> None:
        """Initialize service instance."""
        self.url = url
        if self.url is not None:
            self.data = fetch_graph(url)
        else:
            self.data = parse_text(data)
        if config is None:
            self.config = Config()
        else:
            self.config = config
        self.ontology = Graph()
        self.shapes = shapes
        if self.shapes is not None:
            logging.debug("Got user supplied shapes")
            self.shapes = parse_text(shapes)

    async def validate(self) -> Tuple[bool, Graph, Graph, Graph]:
        """Validate function."""
        # Do some sanity checks on preconditions:
        if len(self.data) == 0:  # No need to validate empty graph
            raise ValueError("Input graph cannot be empty.")
        logging.debug(f"Validating with following config: {self.config}")
        if not self.shapes:
            self.shapes = await ShapesService().get_shapes_by_id(self.config.shapes_id)
        if len(self.shapes) == 0:  # No need to validate when empty shapes shapes
            raise ValueError("SHACL graph cannot be empty.")
        # Add triples from remote predicates if user has asked for that:
        if self.config.expand is True:
            self._expand_objects_triples()
            self._load_ontologies()

        # Validate!
        # `inference` should be set to one of the followoing {"none", "rdfs", "owlrl", "both"}
        conforms, results_graph, _ = validate(
            data_graph=self.data,
            ont_graph=self.ontology,
            shacl_graph=self.shapes,
            inference="rdfs",
            inplace=False,
            meta_shacl=False,
            debug=False,
        )
        return (conforms, self.data, self.ontology, results_graph)

    def _expand_objects_triples(self) -> None:  # pragma: no cover
        """Get triples of objects and add to graph."""
        # TODO: this loop should be parallellized
        for p, o in self.data.predicate_objects(subject=None):
            # logging.debug(f"{p} a {type(p)}, {o} a {type(o)}")
            if p == RDF.type:
                pass
            elif type(o) is URIRef:
                if (o, None, None) not in self.data:
                    if (o, None, None) not in self.ontology:
                        logging.debug(f"Trying to fetch remote triples about {o}")
                        g = fetch_graph(o)
                        self.ontology += g

    def _load_ontologies(self) -> None:
        """Load relevant ontologies into ontology."""
        # TODO: this loop should be parallellized
        # TODO: discover relevant ontologies dynamically, should be cached
        ontologies = ["https://www.w3.org/ns/regorg", "https://www.w3.org/ns/org"]
        for o in ontologies:
            if (o, None, None) not in self.ontology:
                logging.debug(f"Trying to add remote ontology {o}")
                self.ontology += fetch_graph(o)
