"""Module for validator service."""
from __future__ import annotations


from dataclasses import dataclass
import logging
import traceback
from typing import Any, Tuple

from pyshacl import validate
from rdflib import Graph, OWL, RDF, URIRef


from dcat_ap_no_validator_service.adapter import fetch_graph, FetchError, parse_text

SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


@dataclass
class Config:
    """Class for keeping track of config item."""

    expand: bool = True
    include_expanded_triples: bool = False


class ValidatorService(object):
    """Class representing validator service."""

    __slots__ = (
        "data_graph",
        "data_graph_url",
        "shapes_graph",
        "shapes_graph_url",
        "ontology_graph",
        "ontology_graph_url",
        "config",
    )

    # Instance variables:
    data_graph: Any
    data_graph_url: str
    shapes_graph: Any
    shapes_graph_url: str
    ontology_graph: Any
    ontology_graph_url: str
    config: Config

    @classmethod
    async def create(
        cls: Any,
        data_graph_url: Any,
        data_graph: Any,
        shapes_graph: Any,
        shapes_graph_url: Any,
        ontology_graph_url: Any,
        ontology_graph: Any,
        config: Config = None,
    ) -> ValidatorService:
        """Initialize service instance."""
        self = ValidatorService()
        # Process data graph:
        self.data_graph_url = data_graph_url
        self.data_graph = (
            await fetch_graph(data_graph_url, use_cache=False)
            if self.data_graph_url
            else parse_text(data_graph)
        )
        # Process shapes graph:
        self.shapes_graph_url = shapes_graph_url
        self.shapes_graph = (
            await fetch_graph(shapes_graph_url, use_cache=False)
            if self.shapes_graph_url
            else parse_text(shapes_graph)
        )
        # Process ontology graph if given:
        if ontology_graph_url:
            self.ontology_graph = await fetch_graph(ontology_graph_url, use_cache=False)
        elif ontology_graph:
            self.ontology_graph = parse_text(ontology_graph)
        else:
            self.ontology_graph = Graph()
        # Config:
        if config is None:
            self.config = Config()
        else:
            self.config = config
        return self

    async def validate(self) -> Tuple[bool, Graph, Graph, Graph]:
        """Validate function."""
        # Do some sanity checks on preconditions:
        # No need to validate when empty data graph:
        if self.data_graph is None or len(self.data_graph) == 0:
            raise ValueError("Data graph cannot be empty.")
        # No need to validate when empty shapes graph:
        if self.shapes_graph is None or len(self.shapes_graph) == 0:
            raise ValueError("Shapes graph cannot be empty.")
        # If user has given an ontology graph, we check for and do imports:
        if self.ontology_graph and len(self.ontology_graph) > 0:
            await self._import_ontologies()

        logging.debug(f"Validating with following config: {self.config}.")
        # Add triples from remote predicates if user has asked for that:
        if self.config.expand is True:
            await self._expand_objects_triples()

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
            do_owl_imports=False,  # owl_imports in pyshacl represent performance penalty
            advanced=False,
        )
        return (conforms, self.data_graph, self.ontology_graph, results_graph)

    async def _expand_objects_triples(self) -> None:
        """Get triples of objects and add to ontology graph."""
        # TODO: this loop should be parallellized
        for p, o in self.data_graph.predicate_objects(subject=None):
            # logging.debug(f"{p} a {type(p)}, {o} a {type(o)}.")
            if p == RDF.type:
                pass
            elif type(o) is URIRef:
                if (o, None, None) not in self.data_graph:
                    if (o, None, None) not in self.ontology_graph:
                        logging.debug(f"Trying to fetch remote triples about {o}.")
                        try:
                            g = await fetch_graph(o)
                            if g:
                                self.ontology_graph += g
                        except FetchError:
                            logging.debug(traceback.format_exc())
                            pass
                        except SyntaxError:
                            logging.debug(traceback.format_exc())
                            pass

    async def _import_ontologies(self) -> None:
        """Import relevant ontologies into ontology graph.

        Interpret the owl import statements. Essentially, recursively merge with all the objects in the owl import
        statement, and remove the corresponding triples from the graph.

        Based on https://owl-rl.readthedocs.io/en/latest/_modules/owlrl.html#interpret_owl_imports
        """
        while True:
            # 1. collect the import statements:
            all_imports = [
                t for t in self.ontology_graph.triples((None, OWL.imports, None))
            ]
            if len(all_imports) == 0:
                # no import statement whatsoever, we can go on...
                return
            # 2. remove all the import statements from the graph
            for t in all_imports:
                self.ontology_graph.remove(t)
            # 3. get all the imported vocabularies and import them
            for (_s, _p, uri) in all_imports:
                if (uri, None, None) not in self.data_graph:
                    if (uri, None, None) not in self.ontology_graph:
                        logging.debug(f"Trying to fetch remote triples about {uri}.")
                        try:
                            _g = await fetch_graph(uri)
                            if _g:
                                self.ontology_graph += _g
                        except FetchError:
                            logging.debug(traceback.format_exc())
                            pass
            # 4. start all over again to see if import statements have been imported
