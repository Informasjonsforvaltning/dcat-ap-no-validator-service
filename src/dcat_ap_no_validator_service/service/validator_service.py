"""Module for validator service."""
from typing import Any

from pyshacl import validate
from rdflib import Graph


class ValidatorService:
    """Class representing validator service."""

    def __init__(self, graph: str) -> None:
        """Initialize service instance."""
        self._g = Graph().parse(data=graph, format="turtle")
        self._sg = Graph().parse("BRegDCAT-AP-shacl_shapes_2.00.ttl", format="turtle")

    async def validate(self) -> Any:
        """Validate function."""
        if len(self._g) == 0:  # No need to validate empty graph
            raise Exception
        # inference in {"none", "rdfs", "owlrl", "both"}
        r = validate(self._g, shacl_graph=self._sg, inference="rdfs")
        return r
