"""Module for fetching shapes graph descriptions."""

from typing import Any, Dict, List, Optional

from dcat_ap_no_validator_service.model import ShapesGraphDescription

_SHAPES_STORE: Dict[str, Dict] = dict(
    {
        "1": {
            "id": "1",
            "name": "The constraints of DCAT-AP-NO",
            "description": "This document specifies the constraints on properties and classes expressed by DCAT-AP-NO in SHACL.",  # noqa
            "version": "0.1",
            "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/v1.1/shacl/dcat-ap_shacl_shapes_1.1.ttl",  # noqa
            "specification_name": "DCAT-AP-NO",
            "specification_version": "1.1",
            "specification_url": "https://data.norge.no/specification/dcat-ap-no/v1.1",  # noqa
        },
        "2": {
            "id": "2",
            "name": "The constraints of DCAT-AP-NO",
            "description": "This document specifies the constraints on properties and classes expressed by DCAT-AP-NO in SHACL.",  # noqa
            "version": "0.1",
            "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/v2/shacl/DCAT-AP-NO-shacl_shapes_2.00.ttl",  # noqa
            "specification_name": "DCAT-AP-NO",
            "specification_version": "2.0",
            "specification_url": "https://data.norge.no/specification/dcat-ap-no/",
        },
        "3": {
            "id": "3",
            "name": "The constraints of SKOS-AP-NO-Begrep",
            "description": "This document specifies the constraints on properties and classes expressed by SKOS-AP-NO-Begrep in SHACL.",  # noqa
            "version": "0.1",
            "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/skos-ap-no-begrep/develop/shacl/SKOS-AP-NO-Begrep-shape_shape_v1.ttl",  # noqa
            "specification_name": "SKOS-AP-NO-Begrep",
            "specification_version": "1.0",
            "specification_url": "https://data.norge.no/specification/skos-ap-no-begrep/",
        },
        "4": {
            "id": "4",
            "name": "SHACL-rules for CPSV-AP-NO",
            "description": "This document specifies the constraints on properties and classes in CPSV-AP-NO, expressed in SHACL.",  # noqa
            "version": "0.9.04",
            "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/cpsv-ap-no/develop/shacl/CPSV-AP-NO_shacl_shapes_v09xx.ttl",  # noqa
            "specification_name": "CPSV-AP-NO",
            "specification_version": "0.9",
            "specification_url": "https://informasjonsforvaltning.github.io/cpsv-ap-no/",
        },
    }
)


class ShapesGraphAdapter:
    """Class representing a shapes graph adapter.

    Implements basic fetch methods:
    - get_all
    - get_by_id
    """

    @classmethod
    async def get_all(cls: Any) -> List[ShapesGraphDescription]:
        """List all shapes graph objects in store."""
        return [ShapesGraphDescription(**x) for x in _SHAPES_STORE.values()]

    @classmethod
    async def get_by_id(cls: Any, id: str) -> Optional[ShapesGraphDescription]:
        """Get shapes graph given by id if in objects in store."""
        if id in _SHAPES_STORE:
            return ShapesGraphDescription(**_SHAPES_STORE[id])
        return None
