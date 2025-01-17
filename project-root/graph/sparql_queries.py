# Authors: Lewei Xu (23709058), Marc Labouchardiere (23857377)
# Python script with SPARQL queries (find procedures, items, etc.)

from rdflib import Graph
from config import KNOWLEDGE_GRAPH

def run_queries():
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

    # Get names of items with more than 3 procedures written for them
    query = """
        PREFIX ex: <http://test.org/ifixit.com#>

        SELECT ?item_name (COUNT(?procedure) as ?procedure_count)
        WHERE {
            ?procedure ex:procedure_for ?item .
            ?item ex:has_name ?item_name .
        }
        GROUP BY ?item
        HAVING (COUNT(?procedure) > 3)
    """
    print("\nItems with more than 3 procedures:")
    for result in g.query(query):
        print(f"Item [{result['item_name']}], number of procedures [{result['procedure_count']}]")

    # Find procedures where tools mentioned in toolbox don't appear in any steps
    query = """
        PREFIX ex: <http://test.org/ifixit.com#>

        SELECT ?procedure_name ?tool_name
        WHERE {
            # Select procedures and their associated tools from the toolbox
            ?procedure ex:has_name ?procedure_name .
            ?tool ex:has_name ?tool_name ;
                ex:in_toolbox ?procedure.

            # Ensure that the selected tool is NOT used in any step of the procedure
            FILTER NOT EXISTS {
                ?procedure ex:has_step ?step .
                ?step ex:step_uses_tool ?tool .
            }
        }
    """
    print("\nProcedures with tools in toolbox not mentioned in any step:")
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

    input("\nPress any key to continue...")

if __name__ == "__main__":
    run_queries()