from config import KNOWLEDGE_GRAPH, PROCEDURE_RELATIONSHIP
from owlready2 import get_ontology
import logging

def print_procedure_relationships():
    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # File handler - Logs to a file
    file_handler = logging.FileHandler(PROCEDURE_RELATIONSHIP, mode='w')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Terminal handler - Logs to the terminal
    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.INFO)
    terminal_formatter = logging.Formatter('%(message)s')  # Simpler format for terminal output
    terminal_handler.setFormatter(terminal_formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(terminal_handler)

    # Load the ontology
    graph = get_ontology(KNOWLEDGE_GRAPH).load()
    for procedure in graph.Procedure.instances():
        logger.info(f"Procedure: {procedure}")

        for item in procedure.procedure_for:
            logger.info(f"\tProcedure for: {item}")  

            for part in item.part_of:
                logger.info(f"\t\t\tPart of: {part}")

        for tool in procedure.procedure_uses_tool:
            logger.info(f"\tProcedure uses tool: {tool}")
            logger.info(f"\t{tool} in toolbox")

        for step in procedure.has_step:
            logger.info(f"\tStep: {step}, Order: {step.has_order}, Text: {step.has_text}")

            for tool in step.step_uses_tool:

                logger.info(f"\t\tUses Tool: {tool}")
            for image in step.has_image:
                logger.info(f"\t\tUses Image: {image}")

        for sub_procedure in procedure.sub_procedure_of:
            logger.info(f"Procedure is a sub-procedure of: {sub_procedure}")

    logger.handlers[0].flush()

    print(f"\nKnowledge graph readable output saved to {PROCEDURE_RELATIONSHIP} for inspection")
    input("\nPress any key to continue...")