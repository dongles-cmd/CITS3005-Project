from owlready2 import *
import json

# Load your ontology
onto = get_ontology('ifixit_ontology.owl').load()

# Use small test JSON file first
with open('test_1_proc.json', 'r') as file:
    data = json.load(file)

tool_name_url = {}
existing_tools = {}
existing_items = {}
existing_parts = {}
existing_images = {}

with onto:
    # Use unique identifier (preferably URL for URI), then set the attribute name for pretty print name
    for procedure in data:
        # Process procedure
        procedure_instance = onto.Procedure(procedure['Url'])  # Use URL as unique identifier
        procedure_instance.procedure_has_name.append(procedure['Title'])

        # Process item of procedure
        item_name = procedure['Category']
        if item_name not in existing_items:
            item_instance = onto.Item(item_name.replace(' ', '_'))  # Prevent serialization error by removing spaces
            item_instance.item_has_name.append(item_name)
            existing_items[item_name] = item_instance
        else:
            item_instance = existing_items[item_name]
        procedure_instance.procedure_for.append(item_instance)
        
        # Process part
        part_name = procedure['Subject']
        if part_name not in existing_parts:
            part_instance = onto.Part(part_name.replace(' ', '_'))  # Prevent serialization error by removing spaces
            part_instance.part_has_name.append(part_name)
            existing_parts[part_name] = part_instance
        else:
            part_instance = existing_parts[part_name]
        part_instance.part_of.append(item_instance)

        # Process toolbox
        for tool in procedure['Toolbox']:
            tool_id = tool['Url']
            tool_name = tool['Name']
            if tool_id not in existing_tools:
                tool_instance = onto.Tool(tool_id)  # Initialize instance
                tool_instance.tool_has_name.append(tool_name)  # Set name attribute
                existing_tools[tool_id] = tool_instance
                tool_name_url[tool_name] = tool_id
            else:
                tool_instance = existing_tools[tool_id]
            procedure_instance.procedure_uses_tool.append(tool_instance)

        # Process steps
        for step in procedure['Steps']:
            stepid = str(step['StepId'])
            step_instance = onto.Step(stepid)
            if step['Order'] not in step_instance.has_order:
                step_instance.has_order.append(step['Order'])
            
            if step['Text_raw'] not in step_instance.has_text:
                step_instance.has_text.append(step['Text_raw'])
            procedure_instance.has_step.append(step_instance)

            # Process images in step
            for url in step['Images']:
                if url not in existing_images:
                    image_instance = onto.Image(url)
                    existing_images[url] = image_instance
                else:
                    image_instance = existing_images[url]
                step_instance.has_image.append(image_instance)
            
            # Process tools in step
            for tool in step['Tools_extracted']:
                if tool == 'NA': break
                if tool not in tool_name_url: continue  # Not sure what to do here, occurs when tool is in toolbox but not in step
                tool_id = tool_name_url[tool]
                tool_instance = existing_tools[tool_id]  # Should already be defined
                step_instance.step_uses_tool.append(tool_instance)

    # Sync the reasoner
    sync_reasoner(infer_property_values=True)

# Save the updated ontology
onto.save(file="ifixit_knowledge_graph.rdf", format='rdfxml')

# # Function to output relationships of Procedures and their Steps
# def print_procedure_relationships():
#     for procedure in onto.Procedure.instances():
#         print(f"Procedure: {procedure}")
        
#         # Print related Items
#         for item in procedure.procedure_for:
#             print(f"  Related Item: {item}")

#         # Print related Steps
#         for step in procedure.has_step:
#             print(f"  Step: {step}, Order: {step.has_order}, Text: {step.has_text}")
            
#             # Print related Tools in the step
#             for tool in step.step_uses_tool:
#                 print(f"    Uses Tool: {tool}")

#         # Print related Tools in the procedure toolbox
#         for tool in procedure.procedure_uses_tool:
#             print(f"  Uses Toolbox Tool: {tool}")

# # Call the function to print relationships
# print_procedure_relationships()