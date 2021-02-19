"""Module for validator service."""
from typing import Any, Dict


class ShapesService:
    """Class representing shapes service."""

    _SHAPES_DB: Dict[str, Dict] = dict(
        {
            "1": {
                "id": "1",
                "name": "The constraints of DCAT-AP-NO",
                "description": "This document specifies the constraints on properties and classes expressed by DCAT-AP-NO in SHACL.",  # noqa
                "version": "0.1",
                "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/v1.1/shacl/dcat-ap_shacl_shapes_1.1.ttl",  # noqa
                "specificationName": "DCAT-AP-NO",
                "specificationVersion": "1.1",
                "specificationUrl": "https://data.norge.no/specification/dcat-ap-no/v1.1",  # noqa
            },
            "2": {
                "id": "2",
                "name": "DCAT-AP-NO",
                "description": "This document specifies the constraints on properties and classes expressed by DCAT-AP-NO in SHACL.",  # noqa
                "version": "0.1",
                "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/v2/shacl/DCAT-AP-NO-shacl_shapes_2.00.ttl",  # noqa
                "specificationName": "DCAT-AP-NO",
                "specificationVersion": "2.0",
                "specificationUrl": "https://data.norge.no/specification/dcat-ap-no/",
            },
        }
    )

    async def get_all_shapes(self) -> list:
        """Get all shapes graphs function."""
        return list(ShapesService._SHAPES_DB.values())

    async def get_shapes_by_id(self, id: str) -> Any:
        """Get unique shapes graph function."""
        if id in self._SHAPES_DB:
            return ShapesService._SHAPES_DB[id]
        return None
