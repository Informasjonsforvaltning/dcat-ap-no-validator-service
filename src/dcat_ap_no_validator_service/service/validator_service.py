"""Module for validator service."""
import logging
import traceback
from typing import Any, Tuple

from pyshacl import validate
from rdflib import Graph, RDF, URIRef

from dcat_ap_no_validator_service.service import ShapeService

DEFAULT_SHACL_VERSION = "2"


class ValidatorService:
    """Class representing validator service."""

    def __init__(
        self,
        graph: Any,
        format: str = "text/turtle",
        version: Any = DEFAULT_SHACL_VERSION,
    ) -> None:
        """Initialize service instance."""
        logging.debug(f"Got request for version: {version}")
        self._g = Graph().parse(data=graph, format=format)
        if version is None:
            self._version = DEFAULT_SHACL_VERSION
        elif version == "":
            self._version = DEFAULT_SHACL_VERSION
        else:
            self._version = version
        self.ograph = Graph()

    async def validate(self) -> Tuple[bool, Graph, Graph, str]:
        """Validate function."""
        if len(self._g) == 0:  # No need to validate empty graph
            raise ValueError("Input graph cannot be empty.")
        # get the shape graph:
        _sg = await ShapeService().get_shape_by_id(self._version)
        logging.debug(f"Validating according to version: {self._version}")
        # add triples from remote predicates:
        self._expand_objects_triples()
        self._load_ontologies()
        s = self._g.serialize(format="turtle")
        logging.debug(f"Ready to validate graph:\n{s.decode()}")
        # inference in {"none", "rdfs", "owlrl", "both"}
        conforms, results_graph, results_text = validate(
            data_graph=self._g,
            ont_graph=self.ograph,
            shacl_graph=_sg,
            inference="rdfs",
            inplace=False,
            meta_shacl=False,
            debug=False,
        )
        return (conforms, self._g, results_graph, results_text)

    def _expand_objects_triples(self) -> None:
        """Get triples of objects and add to _g."""
        # Todo this loop should be parallellized
        for p, o in self._g.predicate_objects(subject=None):
            logging.debug(f"{p} a {type(p)}, {o} a {type(o)}")
            if p == RDF.type:
                pass
            elif type(o) is URIRef:
                if (o, None, None) not in self._g:
                    if (o, None, None) not in self.ograph:
                        logging.debug(f"trying to fetch triples about {o}")
                        try:
                            t = Graph().parse(o)
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
                self.ograph += Graph().parse(o)
        logging.debug(self.ograph.serialize(format="turtle").decode())
