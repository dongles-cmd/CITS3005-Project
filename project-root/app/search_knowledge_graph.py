import argparse
import os
from owlready2 import *
from config import KNOWLEDGE_GRAPH

from rdflib import Graph

def search_graph(query):
    g = Graph()
    g.parse(KNOWLEDGE_GRAPH, format="xml")

    # Example SPARQL query to search for something in the graph
    sparql_query = """
    SELECT ?subject ?predicate ?object
    WHERE {
      ?subject ?predicate ?object .
      FILTER(CONTAINS(str(?object), "%s"))
    }
    """ % query

    results = g.query(sparql_query)
    return results
