from rdflib import Graph
from fuzzywuzzy import process

# Load your RDF/XML knowledge graph
def load_graph(file_path):
    graph = Graph()
    graph.parse(file_path, format="xml")
    return graph

# Function to extract 'procedure_for' relationships
def extract_procedures(graph):
    query = """
    PREFIX ifixit: <http://test.org/ifixit.com#>
    
    SELECT ?procedure ?procedure_name ?item_name
    WHERE {
        ?procedure a ifixit:Procedure ;
                   ifixit:has_name ?procedure_name ;
                   ifixit:procedure_for ?item .
        ?item ifixit:has_name ?item_name .
    }
    """
    
    results = graph.query(query)
    procedure_data = []
    
    for row in results:
        procedure_data.append({
            "procedure": str(row.procedure),
            "procedure_name": str(row.procedure_name),
            "item_name": str(row.item_name)
        })
    
    return procedure_data

# Fuzzy search function
def fuzzy_search_procedures(query, procedure_data, limit=20):
    # Extract item names for fuzzy matching
    item_names = [proc['item_name'] for proc in procedure_data]
    
    # Get top matches using fuzzy matching
    matches = process.extract(query, item_names, limit=limit)
    
    # Prepare matched results with procedure links
    matched_procedures = []
    for match in matches:
        item_name, score = match
        for proc in procedure_data:
            if proc['item_name'] == item_name:
                matched_procedures.append({
                    "procedure_name": proc['procedure_name'],
                    "procedure_link": proc['procedure'],
                    "item_name": proc['item_name'],
                    "score": score
                })
                break
    
    return matched_procedures
