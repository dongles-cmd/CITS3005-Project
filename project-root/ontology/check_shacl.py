# Authors: Lewei Xu (23709058), Marc Labouchardiere (23857377)
from pyshacl import validate
from rdflib import Graph
from config import SHACL_CONSTRAINTS, KNOWLEDGE_GRAPH

def check(verbose=False):
    print('\nRunning pySHACL validation...')
    data_graph = Graph()
    data_graph.parse(KNOWLEDGE_GRAPH)
    shacl_graph = Graph()
    shacl_graph.parse(SHACL_CONSTRAINTS, format='ttl')
    conforms, results_graph, results_text = validate(data_graph, shacl_graph=shacl_graph, inference='both')
    print(results_text)
    if verbose:
        print(f"Results graph: {results_graph}")
        input("\nPress any key to continue...")

if __name__ == "__main__":
    check(verbose=True)