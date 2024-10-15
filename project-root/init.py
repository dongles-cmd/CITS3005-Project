import argparse

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Construct an ontology and knowledge graph for subset of Myfixit data and initialize a user app'
        ,
        usage='python3 init.py -verbose')
    
    parser.add_argument('-verbose', help="Run verbose", action='store_true')
    args = parser.parse_args()

    if args.verbose:
        pass
    else:
        pass