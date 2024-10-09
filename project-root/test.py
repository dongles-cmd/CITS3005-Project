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
