from owlready2 import *
import json

# Load your ontology
onto = get_ontology('ifixit_ontology.owl').load()

# Use small test JSON file first
with open('test_1_proc.json', 'r') as file:
    data = json.load(file)

with onto:
    item = onto.Item("Dell_Laptop")
    
    procedure1 = onto.Procedure("Procedure_1")
    procedure1.procedure_for.append(item)
    
    procedure2 = onto.Procedure("Procedure_2")
    procedure2.procedure_for.append(item)
    
    sync_reasoner(infer_property_values = True)  

    print(f"Procedure 1 sub-procedures: {procedure1.sub_procedure_of}")
    print(f"Procedure 2 sub-procedures: {procedure2.sub_procedure_of}")