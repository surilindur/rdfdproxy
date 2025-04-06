"""Utilities related to data access."""

from os import getenv
from functools import cache

from rdflib.term import URIRef
from rdflib.graph import Graph
from rdflib.graph import Dataset
from rdflib.namespace import NamespaceManager
from rdflib.plugins.stores.sparqlstore import SPARQLStore

from constants import HTTP_USER_AGENT


@cache
def get_graph() -> Graph | None:
    """Get the selected graph from SPARQL endpoint."""

    graph_uri = URIRef(getenv("SPARQL_GRAPH"))
    endpoint_uri = URIRef(getenv("SPARQL_ENDPOINT"))

    assert endpoint_uri, "Missing SPARQL endpint URI"
    assert graph_uri, "Missing graph URI"

    username = getenv("SPARQL_USERNAME")
    password = getenv("SPARQL_PASSWORD")
    auth = (username, password) if username and password else None

    store = SPARQLStore(
        auth=auth,
        context_aware=True,
        query_endpoint=endpoint_uri,
        headers={"User-Agent": HTTP_USER_AGENT},
        method="POST_FORM",
    )

    dataset = Dataset(store=store)
    dataset.namespace_manager = NamespaceManager(graph=dataset, bind_namespaces="none")

    graph = dataset.get_context(identifier=graph_uri)

    return graph


def get_document_resources(document_uri: URIRef) -> Graph:
    """Collect the resources for a document from the SPARQL endpoint."""

    graph = get_graph()
    document_graph = Graph(identifier=document_uri)

    if graph:
        query = f"""
            CONSTRUCT {{
                ?s ?p ?o .
            }} WHERE {{
                {{
                    ?s ?p ?o .
                    VALUES ?s {{ {document_uri.n3()} }}
                }}
                UNION
                {{
                    ?s ?p ?o .
                    FILTER ( isIRI(?s) && STRSTARTS(STR(?s), "{document_uri}#") )
                }}
            }}
        """
        # Clean up the query to avoid sending too many whitespaces
        query = query.replace("    ", "").replace("\n", " ").strip()
        document_graph += graph.query(query_object=query).graph

    return document_graph
