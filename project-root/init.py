import argparse
from ontology import ifixit_ontology, populate_graph, check_shacl
from graph import output_kg, sparql_queries
from app import app
from config import *
from owlready2 import *

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Construct an ontology and knowledge graph for subset of Myfixit data and initialize a user app',
        usage='python3 init.py -inspectmode')
    
    parser.add_argument('-inspectmode', help="Run verbose", action='store_true')
    args = parser.parse_args()

    if args.inspectmode:
        ifixit_ontology.init_ontology(verbose=True)
        populate_graph.populate(verbose=True)
        check_shacl.check(verbose=True)
        output_kg.print_procedure_relationships()
        sparql_queries.run_queries()
        app.run_app(verbose=True)
    else:
        ifixit_ontology.init_ontology()
        populate_graph.populate()
        check_shacl.check()
        app.run_app()