"""Module for validator service."""
import logging
from typing import Any, Tuple

from pyshacl import validate
from rdflib import Graph

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
        else:
            self._version = version

    async def validate(self) -> Tuple[bool, Graph, Graph, str]:
        """Validate function."""
        if len(self._g) == 0:  # No need to validate empty graph
            raise ValueError("Input graph cannot be empty.")
        # get the shape graph:
        _sg = await ShapeService().get_shape_by_id(self._version)
        # inference in {"none", "rdfs", "owlrl", "both"}
        logging.debug(f"Validating according to version: {self._version}")
        conforms, results_graph, results_text = validate(
            self._g, shacl_graph=_sg, inference="rdfs", inplace=True
        )
        return (conforms, self._g, results_graph, results_text)
