"""Module for validator service."""
from dataclasses import dataclass
import logging
import traceback
from typing import Any, Tuple

from pyshacl import validate
from rdflib import Graph, RDF, URIRef


from dcat_ap_no_validator_service.adapter import fetch_graph, FetchError, parse_text

SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


@dataclass
class Config:
    """Class for keeping track of config item."""

    expand: bool = True
    include_expanded_triples: bool = False


class ValidatorService:
    """Class representing validator service."""

    __slots__ = (
        "data_graph",
        "data_graph_url",
        "shapes_graph",
        "shapes_graph_url",
        "config",
        "ontology_graph",
    )

    def __init__(
        self,
        data_graph_url: Any,
        data_graph: Any,
        shapes_graph: Any,
        shapes_graph_url: Any,
        config: Config = None,
    ) -> None:
        """Initialize service instance."""
        self.data_graph_url = data_graph_url
        self.data_graph = (
            fetch_graph(data_graph_url)
            if self.data_graph_url
            else parse_text(data_graph)
        )
        self.shapes_graph_url = shapes_graph_url
        self.shapes_graph = (
            fetch_graph(shapes_graph_url)
            if self.shapes_graph_url
            else parse_text(shapes_graph)
        )
        if config is None:
            self.config = Config()
        else:
            self.config = config
        self.ontology_graph = Graph()

    async def validate(self) -> Tuple[bool, Graph, Graph, Graph]:
        """Validate function."""
        # Do some sanity checks on preconditions:
        # No need to validate when empty data graph:
        if self.data_graph is None or len(self.data_graph) == 0:
            raise ValueError("Data graph cannot be empty.")
        # No need to validate when empty shapes graph:
        if self.shapes_graph is None or len(self.shapes_graph) == 0:
            raise ValueError("Shapes graph cannot be empty.")

        logging.debug(f"Validating with following config: {self.config}")
        # Add triples from remote predicates if user has asked for that:
        if self.config.expand is True:
            self._load_ontologies()
            self._expand_objects_triples()

        # Validate!
        # `inference` should be set to one of the followoing {"none", "rdfs", "owlrl", "both"}
        conforms, results_graph, _ = validate(
            data_graph=self.data_graph,
            ont_graph=self.ontology_graph,
            shacl_graph=self.shapes_graph,
            inference="rdfs",
            inplace=False,
            meta_shacl=False,
            debug=False,
        )
        return (conforms, self.data_graph, self.ontology_graph, results_graph)

    def _expand_objects_triples(self) -> None:
        """Get triples of objects and add to ontology graph."""
        # TODO: this loop should be parallellized
        for p, o in self.data_graph.predicate_objects(subject=None):
            # logging.debug(f"{p} a {type(p)}, {o} a {type(o)}")
            if p == RDF.type:
                pass
            elif type(o) is URIRef:
                if (o, None, None) not in self.data_graph:
                    if (o, None, None) not in self.ontology_graph:
                        logging.debug(f"Trying to fetch remote triples about {o}")
                        try:
                            g = fetch_graph(o)
                            if g:
                                self.ontology_graph += g
                        except FetchError:
                            logging.debug(traceback.format_exc())
                            pass

    def _load_ontologies(self) -> None:  # pragma: no cover
        """Load relevant ontologies into ontology graph."""
        # TODO: this loop should be parallellized
        # TODO: discover relevant ontologies dynamically, should be cached
        # TODO: cover with proper tests
        ontologies = [
            "https://www.w3.org/ns/regorg",
            "https://www.w3.org/ns/org",
            "https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalogue/master/src/main/resources/ontology/org-status.ttl",  # noqa
            "http://publications.europa.eu/resource/authority/licence",
        ]
        for o in ontologies:
            if (o, None, None) not in self.ontology_graph:
                logging.debug(f"Trying to add remote ontology {o}")
                try:
                    g = fetch_graph(o)
                    if g:
                        self.ontology_graph += g
                except FetchError:
                    logging.debug(traceback.format_exc())
                    pass
