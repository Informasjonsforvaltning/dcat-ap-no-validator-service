"""Module for validator service."""
from typing import Any, Dict


class OntologiesService:
    """Class representing ontologies service."""

    _ONTOLOGIES_STORE: Dict[str, Dict] = dict(
        {
            "1": {
                "id": "1",
                "name": "The ontologies used by DCAT-AP-NO",
                "description": "This document specifies the ontology information needed by the DCAT-AP-NO validator tool.",  # noqa
                "version": "0.1",
                "url": "https://raw.githubusercontent.com/Informasjonsforvaltning/dcat-ap-no/develop/shacl/ontologies.ttl",  # noqa
                "specificationName": "DCAT-AP-NO",
                "specificationVersion": "2.0",
                "specificationUrl": "https://data.norge.no/specification/dcat-ap-no/v2",  # noqa
            },
        }
    )

    async def get_all_ontologies(self) -> dict:
        """Get all ontologies graphs function."""
        collection = dict()
        collection["ontologies"] = list(OntologiesService._ONTOLOGIES_STORE.values())
        return collection

    async def get_ontology_by_id(self, id: str) -> Any:
        """Get unique ontology graph function."""
        if id in self._ONTOLOGIES_STORE:
            return OntologiesService._ONTOLOGIES_STORE[id]
        return None
