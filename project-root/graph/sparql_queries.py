# Python script with SPARQL queries (find procedures, items, etc.)

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