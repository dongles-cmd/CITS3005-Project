import argparse
import os
from owlready2 import *
from config import KNOWLEDGE_GRAPH

# Load the knowledge graph
onto = get_ontology(KNOWLEDGE_GRAPH).load()

def search_class(class_name):
    """Search for a class in the knowledge graph."""
    results = []
    class_iri = f"http://test.org/ifixit.com#{class_name}"
    
    try:
        found_class = onto.search_one(iri=class_iri)
        if found_class:
            results.append(f"Class '{class_name}' found in the knowledge graph.")
            for instance in found_class.instances():
                results.append(f"Instance of {class_name}: {instance}")
        else:
            results.append(f"Class '{class_name}' not found in the knowledge graph.")
    except Exception as e:
        results.append(f"Error searching for class '{class_name}': {str(e)}")
    
    return results

def search_property(property_name):
    """Search for a property in the knowledge graph."""
    results = []
    property_iri = f"http://test.org/ifixit.com#{property_name}"
    
    try:
        found_property = onto.search_one(iri=property_iri)
        if found_property:
            results.append(f"Property '{property_name}' found in the knowledge graph.")
            if isinstance(found_property, ObjectPropertyClass):
                domain = found_property.domain
                range_ = found_property.range
                results.append(f"Domain: {domain}")
                results.append(f"Range: {range_}")
        else:
            results.append(f"Property '{property_name}' not found in the knowledge graph.")
    except Exception as e:
        results.append(f"Error searching for property '{property_name}': {str(e)}")
    
    return results

def search_individual(individual_name):
    """Search for an individual in the knowledge graph."""
    results = []
    individual_iri = f"http://test.org/ifixit.com#{individual_name}"
    
    try:
        found_individual = onto.search_one(iri=individual_iri)
        if found_individual:
            results.append(f"Individual '{individual_name}' found in the knowledge graph.")
            # Display the properties of the individual
            for prop in found_individual.get_properties():
                prop_value = found_individual[prop]
                results.append(f"Property: {prop} -> Value: {prop_value}")
        else:
            results.append(f"Individual '{individual_name}' not found in the knowledge graph.")
    except Exception as e:
        results.append(f"Error searching for individual '{individual_name}': {str(e)}")
    
    return results

def save_results_to_markdown(results):
    """Save results to a markdown file."""
    with open("app/results.MD", "w") as f:
        f.write("# Knowledge Graph Query Results\n\n")
        for result in results:
            f.write(f"- {result}\n")
    print("Results saved to results.MD")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search the knowledge graph for classes, properties, and individuals.")
    
    parser.add_argument("-class_name", type=str, help="Search for a class in the knowledge graph.")
    parser.add_argument("-property", type=str, help="Search for a property in the knowledge graph.")
    parser.add_argument("-individual", type=str, help="Search for an individual in the knowledge graph.")
    
    args = parser.parse_args()
    
    results = []
    
    if args.class_name:
        results.extend(search_class(args.class_name))
    
    if args.property:
        results.extend(search_property(args.property))
    
    if args.individual:
        results.extend(search_individual(args.individual))
    
    if results:
        save_results_to_markdown(results)
    else:
        print("No results found.")
