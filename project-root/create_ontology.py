from owlready2 import *

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
        transitive = True

    class procedure_for(ObjectProperty):
        domain = [Procedure]
        range = [Item]

    class part_of(ObjectProperty): 
        domain = [Item]  # Will allow Part to be used as it is a subclass of Item
        range = [Item]
        transitive = True

    class Procedure(Thing):
        equivalent_to = [
            has_step.some(Step) &
            procedure_uses_tool.some(Tool) &
            has_step.some(step_uses_tool.some(Tool))
        ]

    class Procedure(Thing):
        equivalent_to = [
            has_step.some(Step) & 
            procedure_for.some(Item) & 
            sub_procedure_of.only(procedure_for.some(Item))  # Sub-procedures share the same item
        ]

# Save the ontology
onto.save(file="ifixit_ontology.owl", format='rdfxml')
