# Python script to load and manage the ontology (uses OWLReady2)
from owlready2 import *
from config import ONTOLOGY

def init_ontology(verbose=False):
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

        """A sub-procedure of a procedure must be a procedure for the same item or a part of that item. 
            Sub-procedures share the same item."""
        Procedure.is_a.append(
            procedure_for.some(Item) & 
            sub_procedure_of.only(procedure_for.some(Item))
            )     
        
        """Inference rule where if two procedures are for the same item, then they are sub-procedures of each other"""
        sub_procedure_rule = Imp()
        sub_procedure_rule.set_as_rule("""Procedure(?p1), Item(?i), procedure_for(?p1, ?i), 
                                        Procedure(?p2), procedure_for(?p2, ?i)->
                                        sub_procedure_of(?p1, ?p2), sub_procedure_of(?p2, ?p1)""")

        """Inference rule where if a procedure is for both a part and an item, then the part is a part of the item"""
        part_of_rule = Imp()
        part_of_rule.set_as_rule("""Procedure(?p), Part(?i), procedure_for(?p, ?i), 
                                    Item(?i1), procedure_for(?p, ?i1) ->
                                    part_of(?i, ?i1)""")

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
    print(f".owl ontology file saved to {ONTOLOGY}")