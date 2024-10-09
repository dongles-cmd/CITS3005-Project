from owlready2 import *
import json

onto = get_ontology('ifixit_ontology.owl').load()

# Use small test json file first 
with open('test.json', 'r') as file:
    data = json.load(file)

existing_tools = {}
existing_items = {}
existing_parts = {}
existing_images = {}

for procedure in data:
    # Process procedure
    procedure_instance = onto.Procedure(procedure['Title'].replace(' ', '_')) # Use URL as unique identifier

    # Process item of procedure
    item_name = procedure['Category'].replace(' ', '_')
    if item_name not in existing_items:
        item_instance = onto.Item(item_name)
        existing_items[item_name] = item_instance
    else:
        item_instance = existing_items[item_name]
    procedure_instance.procedure_for.append(item_instance)
    
    # Process part
    part_name = procedure['Subject'].replace(' ', '_')
    if part_name not in existing_parts:
        part_instance = onto.Part(part_name)
        existing_parts[part_name] = part_instance
    else:
        part_instance = existing_parts[part_name]
    part_instance.part_of.append(item_instance)

    # Process toolbox
    for tool in procedure['Toolbox']:
        tool_name = tool['Name'].replace(' ', '_')
        if tool_name not in existing_tools:
            tool_instance = onto.Tool(tool_name)
            existing_tools[tool_name] = tool_instance
        else:
            tool_instance = existing_tools[tool_name]
        procedure_instance.procedure_uses_tool.append(tool_instance)

    # Process steps
    for step in procedure['Steps']:
        stepid = str(step['StepId'])
        step_instance = onto.Step(stepid)
        step_instance.order = step['Order']
        step_instance.text = step['Text_raw']
        procedure_instance.has_step.append(step_instance)

        # Process images in step
        for url in step['Images']:
            if url not in existing_images:
                image_instance = onto.Image(url)
                existing_images[url] = image_instance
            else:
                image_instance = existing_images[url]
            step_instance.has_image.append(image_instance)
        
        # Process tools in step:
        for tool in step['Tools_extracted']:
            if tool == 'NA': break
            tool_instance = existing_tools[tool_name] # Should already be defined
            step_instance.step_uses_tool.append(tool_instance)

onto.save(file = "ifixit_knowledge_graph.rdf", format='rdfxml')
# # Function to output relationships of Procedures and their Steps
# def print_procedure_relationships():
#     for procedure in onto.Procedure.instances():
#         print(f"Procedure: {procedure}")
        
#         # Print related Items
#         for item in procedure.procedure_for:
#             print(f"  Related Item: {item}")

#         # Print related Steps
#         for step in procedure.has_step:
#             print(f"  Step: {step}, Order: {step.order}, Text: {step.text}")
            
#             # Print related Tools in the step
#             for tool in step.step_uses_tool:
#                 print(f"    Uses Tool: {tool}")

#         # Print related Tools in the procedure toolbox
#         for tool in procedure.procedure_uses_tool:
#             print(f"  Uses Toolbox Tool: {tool}")

# # Call the function to print relationships
# print_procedure_relationships()