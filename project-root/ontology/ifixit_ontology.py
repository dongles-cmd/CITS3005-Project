# Python script to load and manage the ontology (uses OWLReady2)
# NOTE: Run `python3 -m ontology.ifixit_ontology` in /project-root

from owlready2 import *
import json
import logging
from config import DATASET, ONTOLOGY, KNOWLEDGE_GRAPH

# basic logging for error checking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load an empty ontology
onto = get_ontology("http://test.org/ifixit.com#")

with onto:
    # Define classes
    class Procedure(Thing): pass
    class Item(Thing): pass
    class Part(Item): pass  # Part is a subclass of Item
    class Tool(Thing): pass
    class Step(Thing): pass
    class Image(Thing): pass

    # Define data properties
    class has_name(DataProperty):
        domain = [Thing]
        range = [str]

    class has_order(DataProperty):
        domain = [Step]
        range = [int]

    class has_text(DataProperty):
        domain = [Step]
        range = [str]


    # Define object properties
    class uses_tool(ObjectProperty):
        domain = [Thing]    # Both Procedure and Step can use tools
        range = [Tool]

    class has_step(ObjectProperty):
        domain = [Procedure]
        range = [Step]

    class has_image(ObjectProperty):
        domain = [Step]
        range = [Image]

    class sub_procedure_of(ObjectProperty):
        domain = [Procedure]
        range = [Procedure]

    class procedure_for(ObjectProperty):
        domain = [Procedure]
        range = [Item]
    
    class part_of(ObjectProperty): 
        """An item, with a subclass relation that is transitive, and a part-of relation that identifies when one item is a part of another item. 
        Will allow Part to be used as it is a subclass of Item. """
        domain = [Item] 
        range = [Item]
        transitive = True

    class precedes(ObjectProperty):
        """Enforce that each step has a sequential order, e.g., step 1 comes before step 2. """
        domain = [Step]
        range = [Step]
    
    class in_toolbox(ObjectProperty):
        """Ensure that if a tool is used in a step, it must be in the toolbox of the procedure. """
        domain = [Tool]
        range = [Procedure]


    # Define relationships 

    """A sub-procedure of a procedure must be a procedure for the same item or a part of that item. 
        Sub-procedures share the same item."""
    Procedure.is_a.append(
        procedure_for.some(Item) & 
        sub_procedure_of.only(procedure_for.some(Item))
        )     
    
    """A Procedure uses tools that are in its toolbox."""
    Procedure.is_a.append(uses_tool.only(in_toolbox.some(Procedure)))  # Tools in the Procedure's toolbox

    """Procedure has at least one Step. """
    Procedure.is_a.append(has_step.some(Step))

    """A Step uses tools, but only those in the Procedure's toolbox."""
    Step.is_a.append(uses_tool.some(Tool))  # Steps can use tools
    Step.is_a.append(uses_tool.only(in_toolbox.some(Procedure)))  # Step tools must be in Procedure's toolbox

    """Step relationships."""
    Step.is_a.append(precedes.only(Step))  # Each step has a predecessor
    Step.is_a.append(has_text.some(str))  # Each step has some text description

# Save the ontology
onto.save(file=ONTOLOGY)

# Use subset of PC.json dataset (e.g. "Dell Latitude" PCs)
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

# Begin ontology population
with onto:
    # Use unique identifier (preferably URL for URI), then set the attribute name for pretty print name
    for line_number, procedure in enumerate(data, start=1):
        try:
            # Dictionary to cache tool name-URL mappings for each procedure
            toolbox_name_url = {}

            # Process procedure using its URL as a unique identifier
            procedure_url = procedure['Url']
            procedure_instance = get_or_create_instance(onto.Procedure, procedure_url)
            safe_append(procedure_instance.has_name, procedure['Title'])

            # Process item category of procedure
            item_name = procedure['Category'].replace(' ', '_')     # Prevent serialisation errors
            item_instance = get_or_create_instance(onto.Item, item_name)
            safe_append(item_instance.has_name, procedure['Category'])
            safe_append(procedure_instance.procedure_for, item_instance)
            
            # Process part (subject or procedure)
            part_name = procedure['Subject'].replace(' ','_')
            part_instance = get_or_create_instance(onto.Part, part_name)
            safe_append(part_instance.has_name, procedure['Subject'])
            safe_append(part_instance.part_of, item_instance)
            safe_append(procedure_instance.procedure_for, part_instance)

            # Process toolbox (tools used in procedure)
            for tool in procedure.get('Toolbox', []):
                tool_id = tool['Url']
                tool_name = tool['Name']
                if not tool_id:
                    tool_id = tool_name
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
                        logger.warning(f"Line {line_number}: Tool '{tool}' extracted in step but not in toolbox.")
                        continue
                    tool_instance = get_or_create_instance(onto.Tool, tool_id)
                    safe_append(step_instance.uses_tool, tool_instance)
            
            # Example: Check if the procedure has steps
            if not procedure_instance.has_step:
                logger.warning(f"Line {line_number}: Procedure '{procedure['Title']}' has no steps defined. ")

            # Check if a step is missing a text or order
            for step in procedure.get('Steps', []):
                if 'Text_raw' not in step or 'Order' not in step:
                    logger.warning(f"Line {line_number}: Step with ID '{step.get('StepId')}' in procedure '{procedure['Title']}' is missing required data. ")
                    continue
                
                for tool_id in tool_ids:
                    tool_instance = get_or_create_instance(onto.Tool, tool_id)
                    safe_append(step_instance.uses_tool, tool_instance)
        
        except KeyError as e:
            logger.error(f"Line {line_number}: Missing field {str(e)} in procedure {procedure.get('Title', 'Unknown')}")
        except Exception as e: 
            logger.error(f"Line {line_number}: Unexpected error while processing procedure {procedure.get('Title', 'Unknown')}: {str(e)}")
    
# Sync the reasoner
sync_reasoner(infer_property_values=True)

# Save the updated ontology
onto.save(file=KNOWLEDGE_GRAPH, format='rdfxml')
logger.info(f"Knowledge graph saved successfully as '{KNOWLEDGE_GRAPH}'.")

print(f"Procedures {len(list(onto.Procedure.instances()))}")
print(f"Items {len(list(onto.Item.instances()))}")
print(f"Tools {len(list(onto.Tool.instances()))}")
print(f"Parts {len(list(onto.Part.instances()))}")
print(f"Steps {len(list(onto.Step.instances()))}")
print(f"Images {len(list(onto.Image.instances()))}")