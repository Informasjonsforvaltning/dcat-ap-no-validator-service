"""Module for validator service."""
import logging
import traceback
from typing import Any, Tuple

from pyshacl import validate
from rdflib import Graph, RDF, URIRef
import requests

from dcat_ap_no_validator_service.service import ShapeService

DEFAULT_SHACL_VERSION = "2"


class ValidatorService:
    """Class representing validator service."""

    __slots__ = (
        "graph",
        "format",
        "version",
        "ograph",
        "shacl",
    )

    def __init__(
        self,
        graph: Any,
        format: str = "text/turtle",
        version: Any = DEFAULT_SHACL_VERSION,
        shacl: Any = None,
    ) -> None:
        """Initialize service instance."""
        logging.debug(f"Got request for version: {version}")
        self.graph = Graph().parse(data=graph, format=format)
        self.format = format
        if version is None:
            self.version = DEFAULT_SHACL_VERSION
        elif version == "":
            self.version = DEFAULT_SHACL_VERSION
        else:
            self.version = version
        self.ograph = Graph()
        # set the shape graph:
        logging.debug(f"Got input shacl: {shacl}")
        self.shacl = shacl

    async def validate(self) -> Tuple[bool, Graph, Graph, str]:
        """Validate function."""
        if len(self.graph) == 0:  # No need to validate empty graph
            raise ValueError("Input graph cannot be empty.")
        logging.debug(f"Validating according to version: {self.version}")
        if not self.shacl:
            self.shacl = await ShapeService().get_shape_by_id(self.version)
        # add triples from remote predicates:
        self._expand_objects_triples()
        self._load_ontologies()
        s = self.graph.serialize(format="turtle")
        logging.debug(f"Ready to validate graph:\n{s.decode()}")
        # inference in {"none", "rdfs", "owlrl", "both"}
        conforms, results_graph, results_text = validate(
            data_graph=self.graph,
            ont_graph=self.ograph,
            shacl_graph=self.shacl,
            inference="rdfs",
            inplace=False,
            meta_shacl=False,
            debug=False,
        )
        return (conforms, self.graph, results_graph, results_text)

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
                                t = Graph().parse(data=resp.text, format=format)
                                self.ograph += t
                        except Exception:  # pragma: no cover
                            logging.warning(
                                f"failed when trying to fetch triples about {o}"
                            )
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
                    self.ograph += t
                    # logging.debug(self.ograph.serialize(format="turtle").decode())
                except Exception:  # pragma: no cover
                    logging.warning(f"failed when trying to load remote ontolgy {o}")
                    logging.debug(traceback.format_exc())
                    pass
