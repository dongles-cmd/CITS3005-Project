# Authors: Lewei Xu (23709058), Marc Labouchardiere (23857377)
import argparse
from ontology import ifixit_ontology, populate_graph, check_shacl
from graph import output_kg, sparql_queries
from app.app import run_app

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Construct an ontology and knowledge graph for a subset of Myfixit data and initialize a user app',
        usage='python3 init.py [-v] [-a]')
    
    parser.add_argument('-v', help="Run in verbose mode", action='store_true')
    parser.add_argument('-a', help="Run the application after initializing", action='store_true')
    args = parser.parse_args()

    # Pass args.v as verbose argument
    ifixit_ontology.init_ontology(verbose=args.v)
    populate_graph.populate(verbose=args.v)
    check_shacl.check(verbose=args.v)
    if args.v:
        output_kg.print_procedure_relationships()
        sparql_queries.run_queries()
    if args.a:
        run_app()