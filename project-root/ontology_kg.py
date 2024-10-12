from owlready2 import *
from rdflib import Graph
import json

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
    class procedure_has_name(DataProperty):
        domain = [Procedure]
        range = [str]
    class item_has_name(DataProperty):
        domain = [Item]
        range = [str]
    class part_has_name(DataProperty):
        domain = [Part]
        range = [str]
    class tool_has_name(DataProperty):
        domain = [Tool]
        range = [str]
    class has_order(DataProperty):
        domain = [Step]
        range = [int]
    class has_text(DataProperty):
        domain = [Step]
        range = [str]

    # Define object properties
    class procedure_uses_tool(ObjectProperty):
        domain = [Procedure]
        range = [Tool]
    class step_uses_tool(ObjectProperty):
        domain = [Step]
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
    
    # An item, with a subclass relation that is transitive, and a part-of relation that identifies when one item is a part of another item
    class part_of(ObjectProperty): 
        domain = [Item]  # Will allow Part to be used as it is a subclass of Item
        range = [Item]
        transitive = True

    # Tools used in a step of the procedure appear in the toolbox of the procedure
    PropertyChain([[has_step, step_uses_tool], procedure_uses_tool])

    # A sub-procedure of a procedure must be a procedure for the same item or a part of that item
    Procedure.equivalent_to.append(
        procedure_for.some(Item) & 
        sub_procedure_of.only(procedure_for.some(Item))  # Sub-procedures share the same item
        )   

# Save the ontology
onto.save(file="ifixit_ontology.owl", format='rdfxml')


onto = get_ontology('ifixit_ontology.owl').load()
# Use small test JSON file first
with open('test.json', 'r') as file:
    data = json.load(file)

tool_name_url = {}

with onto:
    # Use unique identifier (preferably URL for URI), then set the attribute name for pretty print name
    for procedure in data:
        # Process procedure
        procedure_instance = onto.Procedure(procedure['Url'])  # Use URL as unique identifier
        procedure_instance.procedure_has_name.append(procedure['Title'])

        # Process item of procedure
        item_name = procedure['Category']
        item_instance = onto.Item(item_name.replace(' ', '_'))  # Prevent serialization error by removing spaces
        if item_name not in item_instance.item_has_name:
            item_instance.item_has_name.append(item_name)
        procedure_instance.procedure_for.append(item_instance)
        
        # Process part
        part_name = procedure['Subject']
        part_instance = onto.Part(part_name.replace(' ', '_'))
        if part_name not in part_instance.part_has_name:
            part_instance.part_has_name.append(part_name)
        part_instance.part_of.append(item_instance)

        # Process toolbox
        for tool in procedure['Toolbox']:
            tool_id = tool['Url']
            tool_name = tool['Name']
            tool_instance = onto.Tool(tool_id)
            tool_name_url[tool_name] = tool_id
            if tool_name not in tool_instance.tool_has_name:
                tool_instance.tool_has_name.append(tool_name)  # Set name attribute
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
                image_instance = onto.Image(url)
                step_instance.has_image.append(image_instance)
            
            # Process tools in step
            for tool in step['Tools_extracted']:
                if tool == 'NA': break
                if tool not in tool_name_url: continue  # Not sure what to do here, occurs when tool is in toolbox but not in step
                tool_id = tool_name_url[tool]
                tool_instance = onto.Tool(tool_id)
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

# g = Graph().parse("ifixit_knowledge_graph.rdf")

# # Get the names of procedures with more than 12 steps
# query = """
#     PREFIX ex: <http://test.org/ifixit.com#>

#     SELECT ?procedure_name (COUNT(?step) AS ?step_count)
#     WHERE {
#         ?procedure ex:has_step ?step ;
#             ex:has_name ?procedure_name .
#     }
#     GROUP BY ?procedure
#     HAVING (COUNT(?step) > 12)
# """
# print("Procedures with more than 12 steps:")
# for result in g.query(query):
#     print(f"Procedure [{result['procedure_name']}], number of steps [{result['step_count']}]")

# # Get names of items with more than 10 procedures written for them
# query = """
#     PREFIX ex: <http://test.org/ifixit.com#>

#     SELECT ?item_name (COUNT(?procedure) as ?procedure_count)
#     WHERE {
#         ?procedure ex:procedure_for ?item .
#         ?item ex:has_name ?item_name .
#     }
#     GROUP BY ?item
#     HAVING (COUNT(?procedure) > 10)
# """
# print("\nItems with more than 10 procedures:")
# for result in g.query(query):
#     print(f"Item [{result['item_name']}], number of procedures [{result['procedure_count']}]")

# # Find procedures where tools mentioned in toolbox don't appear in any steps
# query = """
# PREFIX ex: <http://test.org/ifixit.com#>

# SELECT ?procedure_name ?tool_name
# WHERE {
#     ?procedure ex:uses_tool ?tool ;
#                ex:has_name ?procedure_name .
#     ?tool ex:has_name ?tool_name .
#     FILTER NOT EXISTS {
#         ?procedure ex:has_step ?step .
#         ?step ex:uses_tool ?tool .
#     }
# }
# """
# print("\nProcedures with tools in toolbox in mentioned in any step:")
# for result in g.query(query):
#     print(f"Procedure [{result['procedure_name']}] has tool [{result['tool_name']}] in toolbox but not in any steps")

# # Find potentially dangerous procedures 
# query = """
#     PREFIX ex: <http://test.org/ifixit.com#>

#     SELECT ?procedure_name
#     WHERE {
#         ?procedure ex:has_step ?step ;
#             ex:has_name ?procedure_name .
#         ?step ex:has_text ?text .
#         FILTER (CONTAINS(LCASE(?text), "careful") || CONTAINS(LCASE(?text), "dangerous"))
#     }
# """

# print("\nPotentially hazardous procedures:")
# for result in g.query(query):
#     print(f"Procedures [{result['procedure_name']}] may be potentially hazardous")