from owlready2 import *

onto = get_ontology('ifixit_ontology.owl')

for test in onto.data_properties():
    print(test)