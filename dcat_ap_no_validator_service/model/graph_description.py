"""GraphDescription details data class."""
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GraphDescription(ABC):  # noqa: B024
    """Abstract data class with details regarding a graph."""

    id: str
    name: str
    version: str
    url: str
    description: Optional[str] = field(default=None)
    specification_name: Optional[str] = field(default=None)
    specification_version: Optional[str] = field(default=None)
    specification_url: Optional[str] = field(default=None)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ShapesGraphDescription(GraphDescription):
    """Data class with details about a shapes graph."""

    pass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class OntologyGraphDescription(GraphDescription):
    """Data class with details about an ontology graph."""

    pass
