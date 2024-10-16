from config import KNOWLEDGE_GRAPH, BASE_URI
from owlready2 import get_ontology


# Placeholder function for getting procedure details (you will implement this)
def get_procedure_details(procedure_iri="http://test.org/ifixit.com#https://www.ifixit.com/Guide/Dell+OptiPlex+FX170+RAM++Replacement/36709"):
    # Implement the logic here to retrieve details of the procedure using its IRI
    # This function should return a dictionary with all necessary details like:
    # - Name
    # - Step-by-step instructions
    # - Tools required
    # - Images
    # etc.
    
    onto = get_ontology(KNOWLEDGE_GRAPH).load()
    procedure_instances = onto.search(iri=procedure_iri)

    # Assuming there's only one procedure instance for the IRI
    i = procedure_instances[0]
    name = str(i.has_name).strip("[]'")

    # Procedure tools
    toolbox = []
    for tool in i.procedure_uses_tool:
        t = str(tool.has_name).strip("[]'")
        toolbox.append(t)

    steps = []
    for n, step in enumerate(i.has_step):
        images = []
        tools = []

        step_number = n+1
        description = str(step.has_text).strip("[]'")
        #print(f"{step_number}: {description}")

        for image in step.has_image:
            i = str(image.iri).removeprefix(BASE_URI).removesuffix('.standard')
            images.append(str(i))
        
        for tool in step.step_uses_tool:
            tool_name = str(tool.has_name).strip("[]'")
            tools.append(tool_name)
            print(f"{step_number}\t{tool_name}")
        
        # Append step information
        steps.append({'step_number':step_number, 'description':str(description), 'images':images, 'tools': tools})
    
    procedure_details = {
        "name": name,
        "steps": 
            steps,
            # [{'step_number':step_number, 'description':str(description), 'images':images, 'tools': tools}]
        "tools": toolbox
    }

    return procedure_details


if __name__ == "__main__":
    p = get_procedure_details()
    print(p)