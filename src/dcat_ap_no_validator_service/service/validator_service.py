"""Module for validator service."""
import logging
from typing import Tuple

from pyshacl import validate
from rdflib import Graph

from dcat_ap_no_validator_service.service import ShapeService


class ValidatorService:
    """Class representing validator service."""

    def __init__(self, graph: str, version: str = "2") -> None:
        """Initialize service instance."""
        logging.debug(f"Got request for version: {version}")
        self._g = Graph().parse(data=graph, format="turtle")
        self._version = version

    async def validate(self) -> Tuple[bool, Graph, Graph, str]:
        """Validate function."""
        if len(self._g) == 0:  # No need to validate empty graph
            raise ValueError("Input graph cannot be empty.")
        # get the shape graph:
        _sg = await ShapeService().get_shape_by_id(self._version)
        # inference in {"none", "rdfs", "owlrl", "both"}
        conforms, results_graph, results_text = validate(
            self._g, shacl_graph=_sg, inference="rdfs", inplace=True
        )
        return (conforms, self._g, results_graph, results_text)
