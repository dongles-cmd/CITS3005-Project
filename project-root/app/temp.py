from owlready2 import *
from config import KNOWLEDGE_GRAPH

# Load the ontology
onto = get_ontology(KNOWLEDGE_GRAPH).load()

with onto:
    # Class name as a string
    class_name = "Procedure"

    # Get the class dynamically using getattr
    class_to_add = getattr(onto, class_name)

    # Create an instance of the class
    instance = class_to_add("UWU")

onto.save(file=KNOWLEDGE_GRAPH)