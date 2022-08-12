"""Module for fetching remote graph."""
import asyncio
import logging
import os
import traceback

from aiohttp import (
    ClientError,
    ClientOSError,
    ClientTimeout,
    hdrs,
    ServerDisconnectedError,
)
from aiohttp_client_cache import CachedSession
from dotenv import load_dotenv
from rdflib import Graph

load_dotenv()
TIMEOUT = int(os.getenv("TIMEOUT", "5"))

SUPPORTED_FORMATS = set(["text/turtle", "application/ld+json", "application/rdf+xml"])


class FetchError(Exception):
    """Class representing custom exception for fetch method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


async def fetch_graph(
    session: CachedSession, url: str, use_cache: bool = True
) -> Graph:
    """Fetch remote graph at url and return as Graph."""
    logging.debug(f"Trying to fetch remote graph {url}.")
    timeout = ClientTimeout(total=TIMEOUT)

    max_retries = 5
    attempt = 0

    while True:
        try:
            if use_cache:
                response = await session.get(
                    url, headers={hdrs.ACCEPT: "text/turtle"}, timeout=timeout
                )
                body = await response.text()
            else:
                async with session.disabled():
                    response = await session.get(
                        url, headers={hdrs.ACCEPT: "text/turtle"}, timeout=timeout
                    )
                    body = await response.text()
            break
        except (
            ClientOSError,
            ServerDisconnectedError,
        ) as e:  # pragma: no cover
            if attempt < max_retries:
                attempt += 1
                await asyncio.sleep(1)
            else:
                logging.debug(traceback.format_exc())
                raise FetchError(f"Max retries reached. Reason: {e}") from e
        except ClientError as e:
            logging.debug(traceback.format_exc())
            raise FetchError(
                f"Could not fetch remote graph from {url}: ClientError."
            ) from e
        except UnicodeDecodeError as e:
            logging.debug(traceback.format_exc())
            raise FetchError(
                f"Could not fetch remote graph from {url}: UnicodeDecodeError."
            ) from e

    logging.debug(f"Got status_code {response.status}.")
    if response.status == 200:
        logging.debug(f"Trying to parse response from {url}")
        try:
            return parse_text(input_graph=body)
        except SyntaxError as e:
            raise SyntaxError(f"Bad syntax in graph {url}.") from e
    else:
        raise FetchError(
            f"Could not fetch remote graph from {url}: Status = {response.status}."
        ) from None


def parse_text(input_graph: str) -> Graph:
    """Try to parse text as graph."""
    for _format in SUPPORTED_FORMATS:
        # the following is flagged by S110 Try, Except, Pass. But there is
        # no easy way to catch specific errors from the parse function.
        # TODO: find a way to solve this without ignoring S110
        try:
            return Graph().parse(
                data=input_graph,
                format=_format,
            )
        except Exception:
            pass
    # If we reached this point, we were unable to parse.
    raise SyntaxError("Bad syntax in input graph.")
