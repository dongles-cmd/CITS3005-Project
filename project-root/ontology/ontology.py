from owlready2 import *

onto = get_ontology("http://pc-procedures/")

with onto:
    class Procedure(Thing): pass
    class Item(Thing): pass
    class Tool(Thing): pass
    class Step(Thing): pass
    class Image(Thing): pass
    class Part(Item): pass

    class has_part(ObjectProperty, Item >> Part):  # Declare as ObjectProperty
        pass
   
    class is_part_of(ObjectProperty, Part >> Item):  # Declare as ObjectProperty
        inverse_property = has_part  # Define inverse property
 
    class uses_tool(ObjectProperty, Procedure >> Tool):  # Declare as ObjectProperty
        pass
 
    class part_of_procedure(ObjectProperty, Step >> Procedure):  # Declare as ObjectProperty
        pass
   
    class sub_procedure(ObjectProperty, Procedure >> Procedure):  # Declare as ObjectProperty
        pass
 
    # Data properties (attributes for instances)
    class step_number(DataProperty, FunctionalProperty, Step >> int):  # Declare as DataProperty
        pass
 
    class step_description(DataProperty, Step >> str):  # Declare as DataProperty
        pass
 
    class image_path(DataProperty, Image >> str):  # Declare as DataProperty
        pass

    # Define constraints and axioms
    # Example of a transitive relationship
    has_part.transitive = True  # Now `has_part` is a transitive object property
 
    # Example of using domain and range to define property usage
    uses_tool.domain = [Procedure]
    uses_tool.range = [Tool]
 
    # Ensure sub-procedures are for the same item or a part of that item
    sub_procedure.domain = [Procedure]
    sub_procedure.range = [Procedure]
   
    # Add example individuals (instances)
    pc = Item("PC")
    hard_drive = Part("HardDrive")
    screwdriver = Tool("Screwdriver")
   
    # Add relationships
    pc.has_part = [hard_drive]
    procedure = Procedure("ReplaceHardDriveProcedure")
    step1 = Step("Step1")
    step1.step_number = 1
    step1.step_description = "Unscrew the back cover using a screwdriver"
    step1.part_of_procedure = [procedure]
   
    procedure.uses_tool = [screwdriver]

# Save the ontology to a file
onto.save(file="ifixit_ontology.owl")
 
print("Ontology successfully saved to ifixit_ontology.owl")
