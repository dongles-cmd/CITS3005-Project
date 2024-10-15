import json
import logging
from config import DATASET, ONTOLOGY, KNOWLEDGE_GRAPH
from owlready2 import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the already saved ontology
onto = get_ontology(ONTOLOGY).load()
with open(DATASET, 'r') as file:
    data = json.load(file)

# Cache to store instances and avoid repeated `search_one` calls
instance_cache = {}

def safe_append(property_list, value):
    """"Helper function for checking and appending to avoid duplication."""
    if value not in property_list:
        property_list.append(value)

def get_or_create_instance(cls, identifier):
    """Helper function to create/get new/existing instance."""
    if identifier in instance_cache:
        return instance_cache[identifier]
    
    base_uri = onto.base_iri  # Get base IRI of the ontology
    existing_instance = onto.search_one(iri=f"{base_uri}{identifier}")
    
    if existing_instance: 
        instance_cache[identifier] = existing_instance
        return existing_instance
    else: 
        new_instance = cls(identifier)
        instance_cache[identifier] = new_instance
        return new_instance

def check_in_toolbox(tool_name, toolbox_name_url):
    """Function to match tool name with names in toolbox"""
    matches = []
    for key, value in toolbox_name_url.items():
        for word in tool_name.split(): # Look through each word in tool extracted and check if it is in key
            match = True # Match is true unless proven otherwise
            if word not in key:
                match = False 
        if match: matches.append(value) # Return tool_id if match is found
    return matches

def populate(verbose=False):
    with onto:
        # Use unique identifier (preferably URL for URI), then set the attribute name for pretty print name
        for procedure in data:
            try:
                # Dictionary to cache tool name-URL mappings for each procedure
                toolbox_name_url = {}

                # Process procedure using its URL as a unique identifier
                procedure_url = procedure['Url']
                procedure_instance = get_or_create_instance(onto.Procedure, procedure_url)
                safe_append(procedure_instance.has_name, procedure['Title'])

                # Process item category of procedure
                item_name = procedure['Category'].replace(' ', '_').replace('"', '-Inch').strip("'")     # Prevent serialisation errors
                item_instance = get_or_create_instance(onto.Item, item_name)
                safe_append(item_instance.has_name, procedure['Category'])
                safe_append(procedure_instance.procedure_for, item_instance)

                for ancestor_name in procedure['Ancestors']:
                    ancestor_instance = get_or_create_instance(onto.Item, ancestor_name.replace(' ', '_').replace('"', '-Inch').strip("'"))
                    # safe_append(procedure_instance.procedure_for, ancestor_instance)
                    safe_append(item_instance.part_of, ancestor_instance)
                
                # Process part (subject or procedure)
                part_name = procedure['Subject'].replace('"', '-Inch').strip("'").replace(' ', '_')
                part_instance = get_or_create_instance(onto.Part, part_name)
                safe_append(part_instance.has_name, procedure['Subject'])
                # safe_append(part_instance.part_of, item_instance)
                safe_append(procedure_instance.procedure_for, part_instance)

                # Process toolbox (tools used in procedure)
                for tool in procedure.get('Toolbox', []):
                    tool_id = tool['Url']
                    tool_name = tool['Name']
                    if not tool_id:
                        tool_id = tool_name.replace(' ', '_')
                    tool_instance = get_or_create_instance(onto.Tool, tool_id)
                    toolbox_name_url[tool_name] = tool_id
                    safe_append(tool_instance.has_name, tool_name)
                    safe_append(procedure_instance.uses_tool, tool_instance)

                # Process steps
                for step in procedure.get('Steps', []):
                    step_id = str(step['StepId'])
                    step_instance = get_or_create_instance(onto.Step, step_id)
                    safe_append(step_instance.has_order, step['Order'])
                    safe_append(step_instance.has_text, step['Text_raw'])
                    safe_append(procedure_instance.has_step, step_instance)

                    # Process images for the step
                    for image_url in step.get('Images', []):
                        image_instance = get_or_create_instance(onto.Image, image_url)
                        safe_append(step_instance.has_image, image_instance)
                    
                    # Process tools extracted in the step (ensuring tools are in the toolbox)
                    for tool_name in step.get('Tools_extracted', []):
                        if tool_name == 'NA':    # Ignore 'NA' tools
                            break
                        tool_ids = check_in_toolbox(tool_name, toolbox_name_url)
                        if len(tool_ids) == 0:
                            # NOTE to Lewei: Skip tools that aren't in the toolbox
                            logger.warning(f"Tool '{tool_name}' extracted in step but not in toolbox for procedure {procedure['Title']}")
                            continue
                        for tool_id in tool_ids:
                            tool_instance = get_or_create_instance(onto.Tool, tool_id)
                            safe_append(step_instance.uses_tool, tool_instance)
            
            except KeyError as e:
                logger.error(f"Missing field {str(e)} in procedure {procedure.get('Title', 'Unknown')}")
            except Exception as e: 
                logger.error(f"Unexpected error while processing procedure {procedure.get('Title', 'Unknown')}: {str(e)}")
        
        # Sync the reasoner
        sync_reasoner(infer_property_values=True)

    # Save the updated ontology
    onto.save(file=KNOWLEDGE_GRAPH, format='rdfxml')
    logger.info(f"\nKnowledge graph saved successfully as '{KNOWLEDGE_GRAPH}'.")
    if verbose:
        print(f"Procedures {len(list(onto.Procedure.instances()))}")
        print(f"Items {len(list(onto.Item.instances()))}")
        print(f"Tools {len(list(onto.Tool.instances()))}")
        print(f"Parts {len(list(onto.Part.instances()))}")
        print(f"Steps {len(list(onto.Step.instances()))}")
        print(f"Images {len(list(onto.Image.instances()))}")
        input("\nPress any key to continue...")
