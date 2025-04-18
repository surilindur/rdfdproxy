"""Simple Flask application to serve RDF data as documents from a graph."""

from http import HTTPStatus
from typing import Any
from typing import Dict
from pathlib import Path
from logging import exception
from os.path import splitext
from datetime import UTC
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask
from flask import request
from flask import render_template
from flask.wrappers import Response

from flask_cors import CORS as FlaskCORS

from mistune import html

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import NotAcceptable
from werkzeug.exceptions import InternalServerError

from rdflib.term import URIRef
from rdflib.namespace import RDF
from rdflib.namespace import OWL

from storage import get_document_resources
from constants import ACCEPT_MIMETYPES
from constants import MIMETYPE_FORMATS

# The Flask application, with template clean-ups
app = Flask(import_name=__name__)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True

# Load configuration from environment variables if available
app.config.from_prefixed_env()

# Setup Flask-CORS
cors = FlaskCORS(app=app)

# List of all template names for faster lookups
templates: Dict[str, str] = {
    splitext(fp.name)[0]: fp.name for fp in Path(app.template_folder).iterdir()
}


@app.get("/")
@app.get("/<path:path>")
def get_document(path: str = "/") -> Response:
    """Return a document-scoped collection of CBDs in the client-preferrec format."""

    mimetype = (
        request.accept_mimetypes.best_match(ACCEPT_MIMETYPES)
        if request.accept_mimetypes.provided
        else ACCEPT_MIMETYPES[0]
    )

    if not mimetype:
        raise NotAcceptable()

    request_host = request.headers.get(key="x-forwarded-for", default=request.host)
    request_proto = request.headers.get(key="x-forwarded-proto", default=request.scheme)

    document_uri = URIRef(value=path, base=f"{request_proto}://{request_host}")
    document_graph = get_document_resources(document_uri=document_uri)

    if not document_graph:
        raise NotFound()

    same_as = document_graph.value(subject=document_uri, predicate=OWL.sameAs)

    if same_as and isinstance(same_as, URIRef):
        return Response(
            status=HTTPStatus.TEMPORARY_REDIRECT,
            headers={"location": same_as},
        )

    format_keyword = MIMETYPE_FORMATS[mimetype]

    if format_keyword == "html":
        template_key: str | None = "graph" if "graph" in templates else None
        for type_uri in document_graph.objects(
            subject=document_graph.identifier,
            predicate=RDF.type,
            unique=True,
        ):
            if isinstance(type_uri, URIRef):
                parsed_type = urlparse(type_uri)
                if parsed_type.fragment:
                    fragment = parsed_type.fragment.lower()
                    if fragment in templates:
                        template_key = fragment
                        break
                else:
                    last_path_element = parsed_type.path.split("/").pop().lower()
                    if last_path_element in templates:
                        template_key = last_path_element
                        break
        if template_key:
            return render_template(templates[template_key], graph=document_graph)
    else:
        return Response(
            response=document_graph.serialize(format=format_keyword),
            mimetype=mimetype,
        )

    raise InternalServerError()


@app.get("/robots.txt")
def get_robots() -> Response:
    """Return the robots.txt file as text-only representation."""
    if not "robots" in templates:
        raise NotFound()
    if not request.accept_mimetypes.find("text/plain"):
        raise NotAcceptable()
    return render_template(templates["robots"])


@app.context_processor
def handle_context() -> Dict[str, Any]:
    """Add various utility types into the template context."""
    return {
        "now": datetime.now(tz=UTC),
        "html": html,
    }


@app.errorhandler(Exception)
def handle_error(error: Exception) -> Response:
    """Return a representation of a server error."""

    if isinstance(error, HTTPException):
        status_code = error.code
    else:
        exception(error)
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value

    if request.accept_mimetypes.accept_html:
        status = str(status_code)
        if status in templates:
            return Response(
                response=render_template(
                    template_name_or_list=templates[status],
                    error=error,
                ),
                status=status_code,
            )
        if "error" in templates:
            return Response(
                response=render_template(
                    template_name_or_list=templates["error"],
                    error=error,
                ),
                status=status_code,
            )

    return Response(status=status_code)
