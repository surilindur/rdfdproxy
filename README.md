<p align="center">
    <img alt="logo" src="./.github/assets/logo.svg" width="64">
</p>

<p align="center">
    <a href="https://github.com/surilindur/rdfdproxy/actions/workflows/ci.yml"><img alt="CI" src=https://github.com/surilindur/rdfdproxy/actions/workflows/ci.yml/badge.svg?branch=main"></a>
    <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/%3C%2F%3E-Python-%233776ab.svg"></a>
    <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-%23750014.svg"></a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/Code%20Style-black-000000.svg"></a>
</p>

Experimental simple [Flask](https://github.com/pallets/flask) application
to serve [RDF](https://www.w3.org/RDF/) resources
from a [SPARQL endpoint](https://www.w3.org/TR/sparql11-protocol/)
with [content negotiation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Content_negotiation)
using [RDFLib](https://github.com/RDFLib/rdflib).

When the application receives a request for a document with a given URI,
it collects from the SPARQL endpoint graph the set of resources that would belong in that requested document based on their URIs,
and serves this collection in the client-requested format as if it were a document.
The URIs stored in the graph must therefore match the URIs at which this graph is published to clients as documents.
The resources are collected into a context-unaware graph, so context-aware serialisations are not supported.

## Dependencies

* Python
* RDFLib
* Flask
* Flask-CORS

## Compatibility

The queries are sent using `POST` with a `User-Agent` header following the [common conventions](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/User-Agent),
and should thus work with reverse proxies that do agent validation or block the use of query strings.

The application takes into consideration the following headers from reverse proxies when determining the requested document URI:

* `X-Forwarded-For` for the hostname and port.
* `X-Forwarded-Proto` for the protocol (http, https).

The application has been tested against the following SPARQL endpoints:

* Apache Jena Fuseki

## Usage

The application is configured using environment variables:

* `SPARQL_ENDPOINT`: The URI of the read-only SPARQL endpoint.
* `SPARQL_GRAPH`: The URI of the named graph to serve resources from.
* `SPARQL_USERNAME` and `SPARQL_PASSWORD`: The authentiation information if needed.

Templates for HTML serialisation can be provided in the templates directory:

* Resources use the `graph.html` template by default, but this can be overridden based on resource type.
  For example, to add a template for `foaf:PersonalProfileDocument`, it is sufficient to add `personalprofiledocument.html` in the templates directory.
  The graph containing the resources are supplied to the template in the variable `graph`.
* Errors use the `error.html` template by default, but this can be overridden for HTTP errors.
  For example, to add a template for HTTP status 500, it is sufficient to add `500.html` in the templates directory.
  The error is supplied to the template in the variable `error`.
* The `robots.txt` file can be served by adding a template for it in the templates directory.

Further configuration is possible for Flask and Flask-CORS via [environment variables](https://flask.palletsprojects.com/en/stable/api/#flask.Config.from_prefixed_env).

## Issues

Please feel free to report any issues on the GitHub issue tracker.

## License

This code is copyrighted and released under the [MIT license](http://opensource.org/licenses/MIT).
