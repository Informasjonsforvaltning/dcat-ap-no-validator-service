"""GraphDescription details data class."""
from abc import ABC
from dataclasses import dataclass, fields
from typing import Any, Optional


@dataclass
class GraphDescription(ABC):
    """Abstract data class with details regarding a graph."""

    id: str
    name: str
    description: Optional[str]
    version: str
    url: str
    specification_name: Optional[str]
    specification_version: Optional[str]
    specification_url: Optional[str]

    def __init__(self, **kwargs: Any) -> None:
        """Create instance and set default values."""
        names = set([f.name for f in fields(GraphDescription)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)
        if not hasattr(self, "description"):
            self.description = None
        if not hasattr(self, "specification_name"):
            self.specification_name = None
        if not hasattr(self, "specification_version"):
            self.specification_version = None
        if not hasattr(self, "specification_url"):
            self.specification_url = None


class ShapesGraphDescription(GraphDescription):
    """Data class with details about a shapes graph."""

    pass


class OntologyGraphDescription(GraphDescription):
    """Data class with details about an ontology graph."""

    pass
