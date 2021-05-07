"""Module for fetching ontology graph descriptions."""
from typing import Any, Dict, Optional

from dcat_ap_no_validator_service.model import OntologyGraphDescription

_ONTOLOGY_STORE: Dict[str, Dict] = dict(
    {
        "1": {
            "id": "1",
            "name": "The ontologies used by DCAT-AP-NO",
            "description": "This document specifies the ontology information needed by the DCAT-AP-NO validator tool.",  # noqa
            "version": "0.1",
            "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/develop/shacl/ontologies.ttl",  # noqa
            "specification_name": "DCAT-AP-NO",
            "specification_version": "2.0",
            "specification_url": "https://data.norge.no/specification/dcat-ap-no/v2",  # noqa
        },
    }
)


class OntologyGraphAdapter:
    """Class representing an ontology graph adapter.

    Implements basic fetch methods:
    - get_all
    - get_by_id
    """

    @classmethod
    async def get_all(cls: Any) -> list[OntologyGraphDescription]:
        """List all ontology graph objects in store."""
        return [OntologyGraphDescription(**x) for x in _ONTOLOGY_STORE.values()]

    @classmethod
    async def get_by_id(cls: Any, id: str) -> Optional[OntologyGraphDescription]:
        """Get ontology graph given by id if in objects in store."""
        if id in _ONTOLOGY_STORE:
            return OntologyGraphDescription(**_ONTOLOGY_STORE[id])
        return None
