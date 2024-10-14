from owlready2 import *

# Load your ontology
onto = get_ontology("http://test.org/test/")

with onto:
    # Define classes
    class Procedure(Thing): pass
    class Item(Thing): pass

    class sub_procedure_of(ObjectProperty):
        domain = [Procedure]
        range = [Procedure]

    class procedure_for(ObjectProperty):
        domain = [Procedure]
        range = [Item]

    # Create an instance of an item
    item = onto.Item("Dell_Laptop")

    # Create instances of procedures
    procedure1 = onto.Procedure("Procedure_1")
    procedure1.procedure_for.append(item)

    procedure2 = onto.Procedure("Procedure_2")
    procedure2.procedure_for.append(item)

    # Define SWRL rule
    ImplicationRule = Imp()
    ImplicationRule.set_as_rule("""
        Procedure(?p1) ^ 
        Procedure(?p2) ^ 
        procedure_for(?p1, ?item) ^ 
        procedure_for(?p2, ?item)
        -> 
        sub_procedure_of(?p1, ?p2) ^ 
        sub_procedure_of(?p2, ?p1)
    """)

# Synchronize the reasoner
sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

# Debugging outputs
print(f"Procedure 1 sub-procedures: {[str(sub) for sub in procedure1.sub_procedure_of]}")
print(f"Procedure 2 sub-procedures: {[str(sub) for sub in procedure2.sub_procedure_of]}")

# Verify the procedures and their properties
print("Procedures and their procedures_for relationships:")
for proc in onto.Procedure.instances():
    print(f"{proc.name} is for item: {[str(i) for i in proc.procedure_for]}")