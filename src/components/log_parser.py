# src/components/log_parser.py
import re
import sys
import logging
from typing import Dict, Any
from src.pipeline.state import AgentState


from src.exception import CustomException

logger = logging.getLogger(__name__)

class LogParserComponent:
    def __init__(self):
        """
        Initializes the log parser component with a deterministic regex pattern 
        targeting standard system slow query log blocks.
        """
        self.log_pattern = re.compile(
            r"Query:\s*(?P<query>.*?)\s*\|\s*Duration:\s*(?P<duration>[\d\.]+)s", 
            re.IGNORECASE
        )

    def parse_input(self, state: AgentState) -> Dict[str, Any]:
        """
        Parses the dashboard raw input stream and updates the clean query context.
        Uses project-level CustomException for trackable error diagnostics.
        """
        try:
            raw_text = state.get("raw_input", "")
            
            
            if not raw_text or not isinstance(raw_text, str):
                logger.info("INFO: [LogParser] Received empty or invalid data type for 'raw_input'.")
                return {"clean_query": ""}

            raw_text = raw_text.strip()
            logger.info("INFO: [LogParser] Scanning incoming input stream metadata...")

            
            match = self.log_pattern.search(raw_text)
            if match:
                extracted_query = match.group("query").strip()
                logger.info(f"INFO: [LogParser] System slow log metrics detected. Target query: '{extracted_query}'")
                return {
                    "clean_query": extracted_query
                }
            
            
            logger.info(f"INFO: [LogParser] Direct search intent detected. Processing raw string: '{raw_text}'")
            return {
                "clean_query": raw_text
            }

        except Exception as e:
           
            raise CustomException(e, sys)

def log_parser_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph execution wrapper node binding the log parser workflow to the global graph state.
    """
    try:
        parser = LogParserComponent()
        return parser.parse_input(state)
    except Exception as e:
        raise CustomException(e, sys)