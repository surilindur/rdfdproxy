"""Constant values used within the application."""

from typing import Dict
from typing import Sequence
from platform import python_implementation
from platform import python_version
from platform import system
from platform import machine
from collections import OrderedDict

from rdflib import __version__ as RDFLIB_VERSION

# The mimetypes need to be ordered for content negotiation purposes,
# and mapped to format keywords for RDFLib serialization
MIMETYPE_FORMATS: Dict[str, str] = OrderedDict(
    (
        ("text/turtle", "turtle"),
        ("text/plain", "turtle"),
        ("text/html", "html"),
        ("text/n3", "n3"),
        # ("application/hext", "hext"),
        ("application/ld+json", "json-ld"),
        # ("application/n-quads", "nquads"),
        ("application/n-triples", "nt11"),
        ("application/rdf+xml", "pretty-xml"),
        # ("application/trig", "trig"),
        # ("application/trix", "trix"),
    )
)

# Accepted mimetypes in preferential order
ACCEPT_MIMETYPES: Sequence[str] = tuple(MIMETYPE_FORMATS.keys())

# HTTP User-Agent header
HTTP_USER_AGENT: str = " ".join(
    (
        f"RDFDProxy/0.1 ({system()} {machine()})",
        f"RDFLib/{RDFLIB_VERSION}",
        f"{python_implementation()} {python_version()}",
    )
)
