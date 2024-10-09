from rdflib import Graph

g = Graph().parse("ifixit_knowledge_graph.rdf")

query = """
    PREFIX ex: <http://test.org/ifixit.com#>

    SELECT ?procedure (COUNT(?step) as ?step_count)
    WHERE {
        ?procedure ex:has_step ?step .  # Find steps associated with the procedure
        ?step a ex:Step .               # Ensure the object is of type Step
    }
    GROUP BY ?procedure
    HAVING (?step_count > 6)           # Filter to only procedures with more than 6 steps
"""

query = """
    PREFIX ex: <http://test.org/ifixit.com#>

    SELECT ?item (COUNT(?procedure) as ?procedure_count)
    WHERE {
        ?procedure ex:procedure_for ?item .
    }
    GROUP BY ?item
    HAVING (?procedure_count > 10)
"""

query = """
    PREFIX ex: <http://test.org/ifixit.com#>

    SELECT ?item (COUNT(?procedure) as ?procedure_count)
    WHERE {
        ?procedure ex:procedure_for ?item .
    }
    GROUP BY ?item
    HAVING (?procedure_count > 10)
"""

query = """
    PREFIX ex: <http://test.org/ifixit.com#>

    SELECT ?step ?text
    WHERE {
        ?step ex:text ?text .
        FILTER (CONTAINS(LCASE(?text), "careful") || CONTAINS(LCASE(?text), "dangerous"))
    }
"""