from pyshacl import validate
from rdflib import Graph
from config import SHACL_CONSTRAINTS, KNOWLEDGE_GRAPH

def check(verbose=False):
    data_graph = Graph()
    data_graph.parse(KNOWLEDGE_GRAPH)
    shacl_graph = Graph()
    shacl_graph.parse(SHACL_CONSTRAINTS, format='ttl')
    conforms, results_graph, results_text = validate(data_graph, shacl_graph=shacl_graph, inference='both')
    if verbose:
        print('\nRunning pySHACL validation...')
        print(results_text)
        input("\nPress any key to continue...")
