import json

# Load a sample JSON file (e.g., Apparel.json)
with open('PC.json', 'r') as file:
    data = json.load(file)

# Print out the structure
print(json.dumps(data, indent=2))  # Pretty-print the JSON structure to inspect it
