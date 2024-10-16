import logging
from owlready2 import *
from config import KNOWLEDGE_GRAPH

# Helper functions
def safe_append(property_list, value):
    """Helper function for checking and appending to avoid duplication."""
    if value not in property_list:
        property_list.append(value)

def add_procedure(procedure_data, onto):
    """Add a procedure to the ontology using input data."""
    # Dictionary to cache tool name-URL mappings for each procedure
    toolbox_name_url = {}

    with onto:
        # Create procedure instance
        procedure_url = procedure_data['url']
        procedure_instance = onto.Procedure(procedure_url)
        safe_append(procedure_instance.has_name, procedure_data['Title'])

        # Create or get existing item instance
        item_name = procedure_data['Category'].replace(' ', '_').replace('"', '-Inch').strip("'")
        item_instance = onto.Item(item_name)
        safe_append(item_instance.has_name, procedure_data['Category'])
        safe_append(procedure_instance.procedure_for, item_instance)

        # Handle ancestors
        for ancestor_name in procedure_data.get('Ancestors', []):
            ancestor_instance = onto.Item(ancestor_name.replace(' ', '_').replace('"', '-Inch').strip("'"))
            safe_append(item_instance.part_of, ancestor_instance)

        # Handle subject as a part
        part_name = procedure_data['Subject'].replace(' ', '_').replace('"', '-Inch').strip("'")
        part_instance = onto.Part(part_name)
        safe_append(part_instance.has_name, procedure_data['Subject'])
        safe_append(procedure_instance.procedure_for, part_instance)

        # Handle toolbox (tools used in procedure)
        for tool in procedure_data.get('Toolbox', []):
            tool_id = tool['url']
            tool_name = tool['Name']
            if not tool_id:
                tool_id = tool_name.replace(' ', '_')
            tool_instance = onto.Tool(tool_id)
            toolbox_name_url[tool_name] = tool_id
            safe_append(tool_instance.has_name, tool_name)
            safe_append(tool_instance.in_toolbox, procedure_instance)
            safe_append(procedure_instance.procedure_uses_tool, tool_instance)

        # Handle steps
        for step in procedure_data.get('Steps', []):
            step_id = str(step['StepId'])
            step_instance = onto.Step(step_id)
            safe_append(step_instance.has_text, step['Text_raw'])
            safe_append(procedure_instance.has_step, step_instance)

            # Handle images in steps
            for image_url in step.get('Images', []):
                image_instance = onto.Image(image_url)
                safe_append(step_instance.has_image, image_instance)

            # Handle tools in steps
            for tool_name in step.get('Tools_extracted', []):
                if tool_name == 'NA':
                    continue
                tool_ids = check_in_toolbox(tool_name, toolbox_name_url)
                if len(tool_ids) == 0:
                    logging.warning(f"Tool '{tool_name}' not in toolbox for step {step['StepId']}.")
                    continue
                for tool_id in tool_ids:
                    tool_instance = onto.Tool(tool_id)
                    safe_append(step_instance.step_uses_tool, tool_instance)

    # Sync the reasoner and save the updated ontology
    sync_reasoner(infer_property_values=True)
    onto.save(file=KNOWLEDGE_GRAPH, format='rdfxml')
    print(f"Procedure '{procedure_data['Title']}' added successfully!")

def check_in_toolbox(tool_name, toolbox_name_url):
    """Function to match tool name with names in toolbox."""
    matches = []
    for key, value in toolbox_name_url.items():
        for word in tool_name.split():  # Look through each word in tool extracted
            if word not in key:
                break
        else:
            matches.append(value)  # Return tool_id if match is found
    return matches
