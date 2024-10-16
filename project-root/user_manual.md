# User Manual  
*Authors: Lewei Xu (23709058), Marc Labouchardiere (23857377)*  

In this project, we use a small subset of data from the iFixit dataset of procedures to demonstrate searching, adding, updating, and deleting procedures using ontologies and knowledge graphs.

---

## Overview of Schema and Ontology Rules  

The schema of our ontology defines the following core classes, representing the key objects in the iFixit dataset:  

![Ontology Schema](images/schema-white.png)
Diagram: *Ontology Schema*

- **Procedure:** `Thing`
- **Item:** `Thing`
- **Part:** _(subclass of)_ `Item`
- **Tool:** `Thing`
- **Step:** `Thing`
- **Image:** `Thing`

These are the foundational building blocks of our knowledge base, where all relevant objects can be expressed as one of these classes. Next, we define the relationships between these classes and set constraints for these relationships.

### Key Relationships and Constraints  
- **`step_uses_tool`**: `(Step → Tool)`  
    - **Minimum relations**: 0 (A step may not necessarily use a tool)  
    - **Maximum relations**: Theoretically, too many tools in one step would indicate a need to split it into smaller steps, but we do not enforce this here.  
    - **Constraint**: Every tool used in a step must belong to the procedure's toolbox.  
      
- **`has_step`**: `(Procedure → Step)`  
    - **Minimum relations**: 1 (A procedure must have at least one step)  
    - **Maximum relations**: Although having too many steps could indicate poor procedure design, we do not enforce any upper limit.  

- **`has_image`**: `(Step → Image)`  
    - **Minimum relations**: 0 (Steps may not necessarily include an image)  

- **`sub_procedure_of`**: `(Procedure → Procedure)`  
    - This occurs when two procedures are for the same item or part of an item.

- **`procedure_for`**: `(Procedure → Item)`  
    - **Minimum relations**: 1 (Every procedure must be for at least one item; otherwise, it's invalid).  

- **`part_of`**: `(Item → Item)`  
    - **Minimum relations**: 1 (An item must be a part of at least one other item).  
    - **Constraint**: This property is **transitive**. If Item 1 is part of Item 2, and Item 2 is part of Item 3, then Item 1 is also part of Item 3.  

- **`in_toolbox`**: `(Tool → Procedure)`  
    - **Minimum relations**: 1 (A tool must be included in at least one procedure's toolbox, or it's considered redundant).  

- **`procedure_uses_tool`**: `(Procedure → Tool)` _(inverse of `in_toolbox`)_  
    - **Minimum relations**: 0 (A procedure may not need any tools).

### Data Attributes for Classes  
In addition to relationships, specific objects have data attributes that store relevant information:

- **`has_name`**: `(Thing → str)`  
    - Every **procedure**, **item**, **part**, and **tool** has a `name` attribute, represented as a string.  

- **`has_text`**: `(Step → str)`  
    - Each **step** has a text description of its contents.

---

## URI Structure for Unique Instances  

To ensure consistency across our knowledge graph, each class instance must use a unique URI. The following rules apply:

- **Procedure**: Use the procedure's URL as its unique URI.
- **Item**: Use the item’s name (which is consistent in the dataset) as its unique identifier.
- **Part**: Follow the same method as for items.
- **Tool**: Use the URL of the tool if available. If a tool lacks a URL, default to its name.
- **Step**: Use the unique step ID associated with each step. This allows multiple procedures to share steps without duplicates.
- **Image**: Use the image's URL as its unique URI.

---

## How to Form Queries and Examples  

This section provides guidelines for forming SPARQL queries to retrieve information from the knowledge graph. The following are examples of typical queries:

### Example 1: Retrieving All Steps for a Procedure
```sparql
SELECT ?step
WHERE {
    ?procedure a :Procedure .
    ?procedure :has_step ?step .
    ?step :has_text ?text .
    FILTER (?procedure = <procedure_uri>)
}
