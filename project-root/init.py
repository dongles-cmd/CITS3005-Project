import argparse
from ontology import ifixit_ontology, populate_graph, check_shacl
from graph import print_procedure_relationship, sparql_queries
from app import app
from config import *

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Construct an ontology and knowledge graph for subset of Myfixit data and initialize a user app',
        usage='python3 init.py -inspectionmode')
    
    parser.add_argument('-inspectionmode', help="Run verbose", action='store_true')
    args = parser.parse_args()

    if args.inspectionmode:
        pass
    else:
        ifixit_ontology.init_ontology()
        populate_graph.populate()
        check_shacl.check()
        app.run_app()