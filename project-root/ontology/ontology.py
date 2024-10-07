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
 
    # Save the ontology
    onto.save(file = "ifixit_ontology.owl", format = "rdfxml")