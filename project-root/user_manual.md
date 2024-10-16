Authors: Lewei Xu (23709058), Marc Labouchardiere (23857377)

# User Manual
In this project, we use a small subset of data from the iFixit Dataset of procedures to demonstrate searching, adding, updating and deleting procedures using ontologies and knowledge graphs.

## Overview of Schema and Ontology Rules
The schema of our ontology involves defining classes for each of the types of objects that appear in the iFixit dataset:
    - Procedure: Thing
    - Item: Thing
    - Part: (subclass of) Item 
    - Tool: Thing
    - Step: Thing
    - Image: Thing

These are the basic building blocks of our knowledge base, all relevant objects can be expressed as one of these classes. Next, we need to define the relationships between classes, as well as some constraints:
    - step_uses_tool (Step >> Tool)
        - Minimum relations is 0, a step may not necessarily use a tool
        - There is a theoretical maximum as if there are too many tools used in one step, then the step should be split into multiple smaller steps, however this will not be considered here
        - However, each tool must be in the toolbox of the procedure
    - has_step (Procedure >> Step)
        - Minumum relations is 1, a procedure must have at least one step
        - There is a theoretical maximum as if there are too many steps in a procedure, the procedure most likely isn't very well written, but we won't consider this situation.
    - has_image (Step >> Image) (Some procedures have images, but they are not included in the JSON dataset)
        - Minimum relations is 0, a step does not necessarily have to have an image
    - sub_procedure_of (Procedure >> Procedure)
        - Only occurs when two procedures are for the same item of for part of an item
    - procedure_for (Procedure >> Item)
        - Minimum relations is 1, each procedure must be for at least one item, otherwise it is not a valid procedure
    - part_of (Item >> Item)
        - Minimum relations is 1, an item must be a part of at least one other item
        - This property is transitive, if an item 1 is a part of another item 2 and that item is a part of another item 3, then item 1 is a part of item 3 as well by definition
    - in_toolbox (Tool >> Procedure)
        - Minimum relations is 1, if a tool exists, it must be in at least one procedure toolbox otherwise it is redundant data
    - procedure_uses_tool (Procedure >> Tool) (inverse of in_toolbox)
        - Minimum relations is 0, a procedure may not need any tools

In addition to these relations between objects, certain objects also have data attributes:
    - has_name (Thing >> str)
        - Each procedure, item, part and tool has a name attributed to it, that is a string
    - has_text (Step >> str)
        - Each step has a text description of the contents of the step

For each class, we need to use a unique URI to initialize an instance to ensure consistency across the knowledge graph. When we inspected the json dataset, we found that this was especially an issue for tool, where the naming of the tool was inconsistent between step and procedure.
    - Procedure: use the URL to the procedure as the unique URI
    - Item: there is no URL for this, however the name of the item was found to be consistent throughout the dataset
    - Part: same as with Item
    - Tool: use the URL of the tool a the unique URI, some tools did not have a URL, so we default to the tool name
    - Step: use the unique step ID associated with each step, this allows multiple procedures to use the same step without duplicates
    - Image: use the URL of the image as the unique URI

## How to Form Queries and Examples

## How to Add, Remove and Update Data