# Authors: Lewei Xu (23709058), Marc Labouchardiere (23857377)
import json
import os

def pretty_print_json(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    file_name, file_ext = os.path.splitext(input_file)
    output_file = f"{file_name}-prettyprinted{file_ext}"

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Pretty-printed JSON saved to {output_file}")

input_file = 'desktop_pcs.json'
pretty_print_json(input_file)
