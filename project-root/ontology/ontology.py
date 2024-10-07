from owlready2 import *
 
# Load an empty ontology
onto = get_ontology("http://test.org/ifixit.owl#")
 
with onto:
    # Define core classes
    class Procedure(Thing): pass
    class Item(Thing): pass
    class Tool(Thing): pass
    class Step(Thing): pass
    class Image(Thing): pass
    class Part(Thing): pass

    class part_of(ObjectProperty): 
        domain = [Item]
        range = [Item]
        transitive = True  # Part-of is transitive
    class used_in(ObjectProperty):
        domain = [Tool]
        range = [Step]
    class has_step(ObjectProperty):
        domain = [Procedure]
        range = [Step]
    class has_tool(ObjectProperty):
        domain = [Procedure]
        range = [Tool]
    class has_image(ObjectProperty):
        domain = [Step]
        range = [Image]
    class sub_procedure_of(ObjectProperty):
        domain = [Procedure]
        range = [Procedure]

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

    # Example instance creation from the dataset
    dell_procedure = Procedure("Dell_Latitude_D620_CD_Drive_Replacement")
    screwdriver = Tool("Phillips_00_Screwdriver")
    spudger = Tool("Spudger")
    step1 = Step("Step1_Power_Down_Remove_Battery")
    step2 = Step("Step2_Lift_Plastic_Cover")
    # Relations
    dell_procedure.has_step.append(step1)
    dell_procedure.has_step.append(step2)
    dell_procedure.has_tool.append(screwdriver)
    dell_procedure.has_tool.append(spudger)
 
    # Step Images
    img1 = Image("https://d3nevzfk7ii3be.cloudfront.net/igi/2ahoN1SZaDunCRlW.standard")
    step1.has_image.append(img1)
 

    # Specify that tool is used in step
    screwdriver.used_in.append(step1)
    spudger.used_in.append(step2)

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


# Save the ontology
onto.save(file = "ifixit_ontology.owl", format = "rdfxml")