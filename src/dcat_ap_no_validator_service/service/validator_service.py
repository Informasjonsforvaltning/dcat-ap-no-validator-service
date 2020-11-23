"""Module for validator service."""
import logging
from typing import Tuple

from pyshacl import validate
from rdflib import Graph


class ValidatorService:
    """Class representing validator service."""

    def __init__(self, graph: str, version: str) -> None:
        """Initialize service instance."""
        self._g = Graph().parse(data=graph, format="turtle")
        # TODO get version from user and map to correct shacl shape:
        logging.debug(f"Got request for version: {version}")
        self._sg = Graph().parse("BRegDCAT-AP-shacl_shapes_2.00.ttl", format="turtle")

    async def validate(self) -> Tuple[bool, Graph, Graph, str]:
        """Validate function."""
        if len(self._g) == 0:  # No need to validate empty graph
            raise Exception
        # inference in {"none", "rdfs", "owlrl", "both"}
        conforms, results_graph, results_text = validate(
            self._g, shacl_graph=self._sg, inference="rdfs"
        )
        return (conforms, self._g, results_graph, results_text)
