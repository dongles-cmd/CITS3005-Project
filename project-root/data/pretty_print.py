import json
import os

def pretty_print_json(input_file):
    # Open and read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Create the output file name by appending "-prettyprinted" to the input file name
    file_name, file_ext = os.path.splitext(input_file)
    output_file = f"{file_name}-prettyprinted{file_ext}"

    # Write the pretty-printed JSON to the output file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Pretty-printed JSON saved to {output_file}")

# Example usage
input_file = 'desktop_pcs.json'  # Replace this with your actual file
pretty_print_json(input_file)
