# Python script with SPARQL queries (find procedures, items, etc.)
# NOTE: Run `python3 -m graph.sparql_queries` in /project-root

from rdflib import Graph
from config import KNOWLEDGE_GRAPH
from owlready2 import get_ontology

# Function to output relationships of Procedures and their Steps
def print_procedure_relationships(onto):
    for procedure in onto.Procedure.instances():
        print(f"Procedure: {procedure}")
        
        # Print related Items
        for item in procedure.procedure_for:
            print(f"\tRelated Item: {item}")

        # Print related Steps
        for step in procedure.has_step:
            print(f"\tStep: {step}, Order: {step.has_order}, Text: {step.has_text}")
            
            # Print related Tools in the step
            for tool in step.uses_tool:
                print(f"\t\tUses Tool: {tool}")

            # Print related Images in the step
            for image in step.has_image:
                print(f"\t\tUses Image: {image}")

        # Print related Tools in the procedure toolbox
        for tool in procedure.uses_tool:
            print(f"\tUses Toolbox Tool: {tool}")

# Call the function to print relationships
onto = get_ontology(KNOWLEDGE_GRAPH).load()
print_procedure_relationships(onto)

# Load in the knowledge graph from RDF file
g = Graph()
g.parse(KNOWLEDGE_GRAPH)

# Get the names of procedures with more than 12 steps
query = """
    PREFIX ex: <http://test.org/ifixit.com#>

    SELECT ?procedure_name (COUNT(?step) AS ?step_count)
    WHERE {
        ?procedure ex:has_step ?step ;
            ex:has_name ?procedure_name .
    }
    GROUP BY ?procedure
    HAVING (COUNT(?step) > 12)
"""
print("Procedures with more than 12 steps:")
for result in g.query(query):
    print(f"Procedure [{result['procedure_name']}], number of steps [{result['step_count']}]")

# Get names of items with more than 10 procedures written for them
query = """
    PREFIX ex: <http://test.org/ifixit.com#>

    SELECT ?item_name (COUNT(?procedure) as ?procedure_count)
    WHERE {
        ?procedure ex:procedure_for ?item .
        ?item ex:has_name ?item_name .
    }
    GROUP BY ?item
    HAVING (COUNT(?procedure) > 10)
"""
print("\nItems with more than 10 procedures:")
for result in g.query(query):
    print(f"Item [{result['item_name']}], number of procedures [{result['procedure_count']}]")

# Find procedures where tools mentioned in toolbox don't appear in any steps
query = """
    PREFIX ex: <http://test.org/ifixit.com#>

    SELECT ?procedure_name ?tool_name
    WHERE {
        ?procedure ex:uses_tool ?tool ;
                ex:has_name ?procedure_name .
        ?tool ex:has_name ?tool_name .
        FILTER NOT EXISTS {
            ?procedure ex:has_step ?step .
            ?step ex:uses_tool ?tool .
        }
    }
"""
print("\nProcedures with tools in toolbox in mentioned in any step:")
for result in g.query(query):
    print(f"Procedure [{result['procedure_name']}] has tool [{result['tool_name']}] in toolbox but not in any steps")

# Find potentially dangerous procedures 
# Ensure superstring match not included (e.g. "carefully")
query = """
    PREFIX ex: <http://test.org/ifixit.com#>

    SELECT ?procedure_name
    WHERE {
        ?procedure ex:has_step ?step ;
            ex:has_name ?procedure_name .
        ?step ex:has_text ?text .
        FILTER (
        (REGEX(STR(?text), "careful", "i") || 
         REGEX(STR(?text), "dangerous", "i")) &&
        !(REGEX(STR(?text), "carefully", "i") || 
          REGEX(STR(?text), "dangerously", "i"))
    )
    }
"""

print("\nPotentially hazardous procedures:")
for result in g.query(query):
    print(f"Procedures [{result['procedure_name']}] may be potentially hazardous")