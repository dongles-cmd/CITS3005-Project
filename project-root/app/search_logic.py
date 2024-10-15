from fuzzywuzzy import process
from config import KNOWLEDGE_GRAPH
from owlready2 import get_ontology

# Extract procedure details including the first image if it exists
def extract_procedures(graph):
    results = []

    # Iterate over all procedures in the ontology
    for procedure in graph.Procedure.instances():
        procedure_name = str(procedure.has_name).strip("[]'")
        tags = procedure_name.lower().split(" ")
        procedure_link = procedure.iri

        # Find the first image (None if no image)
        image = None
        for step in procedure.has_step:
            for img in step.has_image:
                image = str(img.iri).removeprefix("http://test.org/ifixit.com#")
                break
            if image is not None: break
    
        results.append({'name':procedure_name, 'link':procedure_link, 'tags':tags, 'image':image})
    
    return results

# # Fuzzy search function based on tags
def fuzzy_search(query, procedure_data):
    # Prepare a list of all tags for fuzzy matching
    all_tags = [tag for proc in procedure_data for tag in proc['tags']]
    
    # Get top matches using fuzzy matching
    matches = process.extract(query, all_tags)
    
    # Prepare matched results with procedure links and images
    matched_procedures = []
    for match in matches:
        tag_name, score = match
        for proc in procedure_data:
            if tag_name in proc['tags']:  # Check if the tag matches
                matched_procedures.append({
                    "name": proc['name'],
                    "link": proc['link'],
                    "image": proc['image'],
                    "score": score
                })
    
    return filter_duplicated_matches(matched_procedures)

# Filter the matches to remove duplicates and keep the matching ones
def filter_duplicated_matches(duplicated_matches):
    filtered_matches = set()
    for m in duplicated_matches:
        # Close enough match
        if m['score'] >= 90:
            filtered_matches.add((m['name'], m['link'], m['image']))
    
    return list(filtered_matches)

def main():
    g = get_ontology(KNOWLEDGE_GRAPH).load()
    data = extract_procedures(g)
    matches = fuzzy_search(query="Dell Laptop", procedure_data=data)
    return matches

if __name__ == "__main__":
    results = main()
    for i in results:
        print(i)
