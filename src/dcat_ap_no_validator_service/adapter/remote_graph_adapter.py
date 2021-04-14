"""Module for fetching remote graph."""
import logging
import os

from aiohttp import hdrs
from dotenv import load_dotenv
from rdflib import Graph
import redis
import requests
from requests.exceptions import RequestException
import requests_cache


# Setting up cache
load_dotenv()
# Enable cache in all other cases than test:
CONFIG = os.getenv("CONFIG", "production")
if CONFIG in {"test", "dev"}:
    pass
else:  # pragma: no cover
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    requests_cache.install_cache(
        backend="redis", namespace="dcat-ap-no-validator-service", connection=conn
    )

SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


class FetchError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


def fetch_graph(url: str) -> Graph:
    """Fetch remote graph at url and return as Graph."""
    logging.debug(f"Trying to fetch remote graph {url}")
    try:
        resp = requests.get(url, headers={hdrs.ACCEPT: "text/turtle"})
    except RequestException:
        raise FetchError(f"Could not fetch remote graph from {url}")
    logging.debug(f"Got status_code {resp.status_code}")
    if resp.status_code == 200:
        logging.debug(f"Got valid remote graph from {url}")
        return parse_text(input_graph=resp.text)
    else:
        raise FetchError(f"Could not fetch remote graph from {url}")


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
