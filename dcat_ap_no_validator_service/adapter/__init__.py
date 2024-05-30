"""Package for all adapters."""

from .ontology_graph_adapter import OntologyGraphAdapter
from .remote_graph_adapter import fetch_graph, FetchError, parse_text
from .shapes_graph_adapter import ShapesGraphAdapter
