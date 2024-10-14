from owlready2 import *

# Load an ontology (or create a new one)
onto = get_ontology("http://example.org/onto.owl")

with onto:
    # Define classes
    class Person(Thing):
        pass
    
    class Cat(Thing):
        pass
    
    # Define properties
    class owns(ObjectProperty):
        domain = [Person]
        range = [Cat]
    
    class likes(ObjectProperty):
        domain = [Person]
        range = [Cat]
    
    # Define the rule
    # If a person owns a cat, they like cats
    ImplicationRule = Imp()
    ImplicationRule.set_as_rule(f"""
    Person(?p), Cat(?c), owns(?p, ?c) -> likes(?p, ?c)
    """)

    # Example individuals
    john = Person("John")
    whiskers = Cat("Whiskers")
    john.owns.append(whiskers)

    sync_reasoner(infer_property_values = True)

# After reasoning, John should like Whiskers if the rule is applied correctly
for pet in john.likes:
    print(f"{john.name} likes {pet.name}")
