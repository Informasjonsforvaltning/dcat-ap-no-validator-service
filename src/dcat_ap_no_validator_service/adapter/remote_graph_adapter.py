"""Module for fetching remote graph."""
import logging

from aiohttp import hdrs
from rdflib import Graph
import requests

SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


def fetch_graph(url: str) -> Graph:
    """Fetch remote graph at url and return as Graph."""
    logging.debug(f"Trying to fetch remote graph {url}")
    resp = requests.get(url, headers={hdrs.ACCEPT: "text/turtle"})
    logging.debug(f"Got status_code {resp.status_code}")
    if resp.status_code == 200:
        try:
            g = parse_text(input_graph=resp.text)
            logging.debug(f"Got valid remote graph from {url}")
            return g
        except SyntaxError:
            return None
    else:
        return None


def parse_text(input_graph: str) -> Graph:
    """Try to parse text as graph."""
    for _format in SUPPORTED_FORMATS:
        # the following is flagged by S110 Try, Except, Pass. But there is
        # no easy way to catch specific errors from the parse function.
        # TODO: find a way to solve this without ignoring S110
        try:
            return Graph().parse(data=input_graph, format=_format)
        except Exception:
            pass
    # If we reached this point, we were unable to parse.
    raise SyntaxError()
