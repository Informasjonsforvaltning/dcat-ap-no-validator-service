"""Module for validator service."""
import logging
from typing import Dict

from rdflib import Graph


class ShapeService:
    """Class representing shape service."""

    _shape_db: Dict[str, Graph] = {}

    def __init__(self) -> None:
        """Initialize service instance."""
        try:
            self._shape_db["1.1"] = Graph().parse(
                "dcat-ap_shacl_shapes_1.1.ttl", format="turtle"
            )
            self._shape_db["2"] = Graph().parse(
                "dcat-ap-no-shacl_shapes_2.00.ttl", format="turtle"
            )
        except Exception as e:
            logging.error(f"Exception: {e}")
            raise e

    async def get_all_shapes(self) -> Graph:
        """Get shapes function."""
        g = Graph()
        # TODO: make a rdf collection and add the ontologies (shape graphs)
        return g

    async def get_shape_by_id(self, id: str) -> Graph:
        """Get shapes function."""
        if id in self._shape_db:
            return self._shape_db[id]
        else:
            return Graph()
