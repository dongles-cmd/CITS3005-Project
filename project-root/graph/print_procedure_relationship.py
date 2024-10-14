# Simple program to represent knowledge graph based around procedures
# NOTE: Run `python3 -m graph.print_procedure_relationship` in /project-root

from config import KNOWLEDGE_GRAPH, PROCEDURE_RELATIONSHIP
from owlready2 import get_ontology
import logging

# Configure logging to output to a file
logging.basicConfig(
    filename=PROCEDURE_RELATIONSHIP,  # Log file name
    level=logging.INFO,                      # Set logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    filemode='w'                             # Overwrite the log file each time
)

logger = logging.getLogger(__name__)  # Create a logger

def print_procedure_relationships(onto):
    for procedure in onto.Procedure.instances():
        logger.info(f"Procedure: {procedure}")
        
        # Log related Items
        for item in procedure.procedure_for:
            logger.info(f"\tProcedure for: {item}")
            
            # Lewei oppsie
            for part in item.part_of:
                logger.info(f"\t\t\tPart of: {part}")

        # Log related Tools in the procedure toolbox
        for tool in procedure.uses_tool:
            logger.info(f"\tUses Toolbox Tool: {tool}")

        # Log related Steps
        for step in procedure.has_step:
            logger.info(f"\tStep: {step}, Order: {step.has_order}, Text: {step.has_text}")
            
            # Log related Tools in the step
            for tool in step.uses_tool:
                logger.info(f"\t\tUses Tool: {tool}")

            # Log related Images in the step
            for image in step.has_image:
                logger.info(f"\t\tUses Image: {image}")

        for procedure in procedure.sub_procedure_of:
            logger.info(f"Procedure is a sub-procedure of: {procedure}")

# Call the function to print relationships
graph = get_ontology(KNOWLEDGE_GRAPH).load()
print_procedure_relationships(graph)