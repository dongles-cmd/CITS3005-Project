# Python command-line application to query ontology -> results.MD
#!pip install rdflib argparse
#NOTE: Run `python3 -m app.search_ontology` in /project-root

from rdflib import Graph
from config import ONTOLOGY

def search_ontology(query):
    g = Graph()
    g.parse(ONTOLOGY, format="xml")

    sparql_query = """
    SELECT ?subject ?predicate ?object
    WHERE {
      ?subject ?predicate ?object .
      FILTER(CONTAINS(str(?subject), "%s"))
    }
    """ % query

    results = g.query(sparql_query)
    return results


