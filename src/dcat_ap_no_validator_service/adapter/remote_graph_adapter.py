"""Module for fetching remote graph."""
import logging
from typing import Any

from rdflib import Graph
from rdflib.plugin import PluginException
import requests

SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


def fetch_graph(url: str) -> Graph:
    """Fetch remote graph at url and return as Graph."""
    logging.debug(f"Trying to fetch remote graph {url}")
    headers = {"Accept": "text/turtle"}  # We need to get rdf from url
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        format = resp.headers["content-type"].split(";")[0]
        try:
            g = parse_text(input_graph=resp.text, format=format)
            logging.debug(
                f"Got valid remote graph from parse_text\n{g.serialize().decode()}"
            )
            return g
        except PluginException:
            return Graph()
    else:
        return Graph()


def parse_text(input_graph: Any, format: Any = None) -> Graph:
    """Try to parse text as graph."""
    # If format is valid, we go ahead with parsing:
    if format and format.lower() in SUPPORTED_FORMATS:
        return Graph().parse(data=input_graph, format=format)
    # Else we try the valid format one after the other:
    else:
        for _format in SUPPORTED_FORMATS:
            # the following is flagged by S110 Try, Except, Pass. But there is
            # no easy way to catch specific errors from the parse function.
            # TODO: find a way to solve this without ignoring S110
            try:
                g = Graph().parse(data=input_graph, format=_format)
                return g
            except Exception:
                pass
        # If we reached this point, we were unable to parse.
        raise PluginException()
