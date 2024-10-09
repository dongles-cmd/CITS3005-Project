from owlready2 import *
 
# Load an empty ontology
onto = get_ontology("http://test.org/ifixit.com#")
 
with onto:
    # Define classes
    class Procedure(Thing): pass
    class Item(Thing): pass
    class Part(Item): pass # Part is a subclass of Item
    class Tool(Thing): pass
    class Step(Thing): pass
    class Image(Thing): pass

    class has_name(DataProperty):
        domain = [Procedure, Item, Part, Tool, Step, Image] 
        range = [str] 

    # Define relationships
    class uses_tool(ObjectProperty):
        domain = [Procedure, Step]
        range = [Tool]
    class has_step(ObjectProperty):
        domain = [Procedure]
        range = [Step]
    class has_image(ObjectProperty):
        domain = [Step]
        range = [Image]
    class sub_procedure_for(ObjectProperty):
        domain = [Procedure]
        range = [Procedure]
    class procedure_for(ObjectProperty):
        domain = [Procedure]
        range = [Item]

    
    # An item, with a subclass relation that is transitive
    # and a part-of relation that identifies when one item is a part of another item
    class part_of(ObjectProperty): 
        domain = [Item] # Will allow Part to be used as it is a subclass of Item
        range = [Item]
        transitive = True
    # Tools used in a step of the procedure must appear in the toolbox of the procedure
    class Procedure(Thing):
        equivalent_to = [Thing & has_step.some(Step) & uses_tool.some(Tool)]
    # A sub-procedure of a procedure must be a procedure for the same item or a part of that item
    class Procedure(Thing):
        equivalent_to = [Thing & sub_procedure_for.only(procedure_for.some(Item) | procedure_for.some(part_of))]

onto.save(file = "ifixit_ontology.owl", format='rdfxml')