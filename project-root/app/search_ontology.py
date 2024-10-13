# Python command-line application to query ontology -> results.MD
#!pip install rdflib argparse
#NOTE: Run `python3 -m app.search_ontology` in /project-root

import argparse
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import os
from config import ONTOLOGY

# Load the ontology into a graph
g = Graph()
g.parse(ONTOLOGY)

def query_class(class_name):
    """Search for classes in the ontology."""
    results = []
    class_uri = URIRef(f"http://test.org/ifixit.com#{class_name}")
    
    # Check if the class exists
    if (class_uri, RDF.type, OWL.Class) in g:
        results.append(f"Class '{class_name}' exists in the ontology.")
        
        # Check subclass relationships
        for _, _, subclass in g.triples((class_uri, RDFS.subClassOf, None)):
            results.append(f"Subclass of: {subclass}")
        
    else:
        results.append(f"Class '{class_name}' not found in the ontology.")
    
    return results

def query_property(property_name):
    """Search for properties in the ontology."""
    results = []
    property_uri = URIRef(f"http://test.org/ifixit.com#{property_name}")
    
    # Check if the property exists
    if (property_uri, RDF.type, OWL.ObjectProperty) in g or (property_uri, RDF.type, OWL.DatatypeProperty) in g:
        results.append(f"Property '{property_name}' exists in the ontology.")
        
        # Check domain and range
        domain = g.value(property_uri, RDFS.domain)
        range_ = g.value(property_uri, RDFS.range)
        if domain:
            results.append(f"Domain: {domain}")
        if range_:
            results.append(f"Range: {range_}")
    else:
        results.append(f"Property '{property_name}' not found in the ontology.")
    
    return results

def query_inferences():
    """Query inferred classes and relations."""
    results = []
    # Query for inferred classes (e.g., equivalent classes)
    for subj, _, obj in g.triples((None, OWL.equivalentClass, None)):
        results.append(f"Inferred equivalence: {subj} <=> {obj}")
    
    # Query for inferred relations (e.g., restrictions)
    for subj, _, obj in g.triples((None, RDF.type, OWL.Restriction)):
        results.append(f"Inferred restriction: {subj} => {obj}")
    
    return results

def validate_data():
    """Check for any errors in the data according to the ontology."""
    errors = []
    
    # Example: check for missing properties in classes
    for class_uri in g.subjects(RDF.type, OWL.Class):
        has_step = (class_uri, URIRef("http://test.org/ifixit.com#has_step"), None)
        if not has_step:
            errors.append(f"Error: Class {class_uri} is missing 'has_step' property.")
    
    return errors

def save_to_markdown(results):
    """Save the results to a markdown file."""
    with open('app/results.MD', 'w') as f:
        f.write("# Query Results\n\n")
        for result in results:
            f.write(f"- {result}\n")
    print("Results saved to results.MD")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search ontology and query inferred classes, properties.')
    
    parser.add_argument('-class_name', type=str, help="Search for a class in the ontology")
    parser.add_argument('-property', type=str, help="Search for a property in the ontology")
    parser.add_argument('-inferences', action='store_true', help="Query for inferred classes and relations")
    parser.add_argument('-validate', action='store_true', help="Validate data according to ontology")
    
    args = parser.parse_args()
    
    results = []
    
    if args.class_name:
        results.extend(query_class(args.class_name))
    
    if args.property:
        results.extend(query_property(args.property))
    
    if args.inferences:
        results.extend(query_inferences())
    
    if args.validate:
        results.extend(validate_data())
    
    if results:
        save_to_markdown(results)
    else:
        print("No results to display.")


