"""Module for validator service."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
import traceback
from typing import Any, Tuple

from aiohttp_client_cache import CachedSession
from pyshacl import validate
from rdflib import Graph, OWL, RDF, URIRef


from dcat_ap_no_validator_service.adapter import fetch_graph, FetchError, parse_text

SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


class GraphType(str, Enum):
    """Enum representing different graph types."""

    DATA_GRAPH = "data_graph"
    SHAPES_GRAPH = "shapes_graph"
    ONTOLOGY_GRAPH = "ontology_graph"


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
        "session",
    )

    # Instance variables:
    data_graph: Any
    shapes_graph: Any
    ontology_graph: Any
    config: Config
    session: CachedSession

    @classmethod
    async def create(
        cls: Any,
        cache: Any,
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
        async with CachedSession(cache=cache) as session:
            all_graph_urls = dict()
            # Process data graph:
            self.data_graph = (
                all_graph_urls.update({GraphType.DATA_GRAPH: data_graph_url})
                if data_graph_url
                else parse_text(data_graph)
            )
            # Process shapes graph:
            self.shapes_graph = (
                all_graph_urls.update({GraphType.SHAPES_GRAPH: shapes_graph_url})
                if shapes_graph_url
                else parse_text(shapes_graph)
            )
            # Process ontology graph if given:
            if ontology_graph_url:
                all_graph_urls.update({GraphType.ONTOLOGY_GRAPH: ontology_graph_url})
            elif ontology_graph:
                self.ontology_graph = parse_text(ontology_graph)
            else:
                self.ontology_graph = Graph()
            # Process all_graph_urls:
            logging.debug(f"all_graph_urls len: {len(all_graph_urls)}")
            results = await asyncio.gather(
                *[
                    fetch_graph(session, url, use_cache=False)
                    for url in all_graph_urls.values()
                ]
            )
            # Store the resulting graphs:
            # The order of result values corresponds to the order of awaitables in all_graph_urls.
            # Ref: https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently
            for key, g in zip(all_graph_urls.keys(), results):
                # Did not find any other solution than this brute force chain of ifs
                if key == GraphType.DATA_GRAPH:
                    self.data_graph = g
                elif key == GraphType.SHAPES_GRAPH:
                    self.shapes_graph = g
                elif key == GraphType.ONTOLOGY_GRAPH:
                    self.ontology_graph = g
            # Config:
            if config is None:
                self.config = Config()
            else:
                self.config = config
            return self

    async def validate(self, cache: Any) -> Tuple[bool, Graph, Graph, Graph]:
        """Validate function."""
        async with CachedSession(cache=cache) as session:

            # Do some sanity checks on preconditions:
            # If user has given an ontology graph, we check for and do imports:
            if self.ontology_graph and len(self.ontology_graph) > 0:
                await self._import_ontologies(session)

            logging.debug(f"Validating with following config: {self.config}.")
            # Add triples from remote predicates if user has asked for that:
            if self.config.expand is True:
                await self._expand_objects_triples(session)

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

    async def _expand_objects_triples(self, session: CachedSession) -> None:
        """Get triples of objects and add to ontology graph.

        Search and collect all objects _o_ that is an URI, ignoring
        - objects of the property RDF.type,
        - objects that points to a triple already in the given data_graph.

        Add all _o_'s to a set, which implies that only unique _o_'s are in the resulting set.
        Iterate over the set, and fetch the triples _t_ that _o_ is reffering to.
        The triple _t_ is finally added to the ontology_graph.
        """
        all_remote_triples = set()
        # 1. Collect all relevant remote triples:
        for p, o in self.data_graph.predicate_objects(subject=None):
            if p == RDF.type:
                pass
            elif type(o) is URIRef:
                if (o, None, None) not in self.data_graph:
                    all_remote_triples.add(o)
        if len(all_remote_triples) == 0:
            # no remote_triples whatsoever, we can go on...
            return
        # 2.Get all remote triples:
        logging.debug(f"Trying to expand {len(all_remote_triples)} triples .")
        await asyncio.gather(
            *[self.add_triples(uri, session) for uri in all_remote_triples],
            return_exceptions=True,
        )

    async def _import_ontologies(self, session: CachedSession) -> None:
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
            logging.debug(f"Trying to import {len(all_imports)} ontologies.")
            await asyncio.gather(
                *[self.add_triples(uri, session) for (_s, _p, uri) in all_imports],
                return_exceptions=True,
            )
            # 4. start all over again to see if import statements have been imported

    async def add_triples(self, uri: str, session: CachedSession) -> None:
        """Fetch remote triples and add them to the ontology_graph.

        Only triples that are not allready in the data_graph and/or ontology_graph are added.
        """
        if (uri, None, None) not in self.data_graph:
            if (uri, None, None) not in self.ontology_graph:
                logging.debug(f"Trying to fetch remote triples {uri}.")
                try:
                    _g = await fetch_graph(session, uri)
                    if _g:
                        self.ontology_graph += _g
                except FetchError:
                    logging.debug(traceback.format_exc())
                    pass
                except SyntaxError:
                    logging.debug(traceback.format_exc())
                    pass
