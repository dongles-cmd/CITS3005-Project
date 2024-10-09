from owlready2 import *

# Load empty ontology
onto = owlready2.get_ontology("http://test.org/onto.com#")

# Define classes
with onto:
    class Pizza(Thing): pass
    class Cheese(Thing): pass

    class hasTopping(ObjectProperty): 
        domain = [Pizza]
        range = [Thing]

    class CheesePizza(Pizza):
        equivalent_to = [Pizza & hasTopping.some(Cheese)]

    onto.Pizza("pizza_1")
    onto.Cheese("cheese_1")

    # Say that pizza_1 hasTopping cheese_1
    onto.pizza_1.hasTopping.append(onto.cheese_1)

    print('before reasoner:')
    print(str(list(onto.CheesePizza.instances())))

    sync_reasoner()

    print('before reasoner:')
    print(str(list(onto.CheesePizza.instances())))

    onto.save(file = "onto.owl", format = "rdfxml")