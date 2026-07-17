import sys
import time
import sqlite3
import logging
from typing import Dict, Any
from src.pipeline.state import AgentState
from src.exception import CustomException

logger = logging.getLogger(__name__)

class SandboxExecutionComponent:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path

    def execute_command(self, state: AgentState) -> Dict[str, Any]:
        conn = None
        try:
            intent = state.get("intent", "DATA_RETRIEVAL")
            command = state.get("generated_command", "").strip()

            if not command:
                logger.error("[SandboxExecution] Execution aborted: Generated command is empty.")
                return {
                    "execution_result": {"status": "FAILED", "message": "SQL command is empty."},
                    "final_latency": 0.0
                }

            logger.info(f"[SandboxExecution] Establishing connection to database at: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            start_time = time.perf_counter()
            logger.info(f"[SandboxExecution] Running targeted SQL command script: '{command}'")
            cursor.execute(command)
            
            
            if intent in ["DATA_RETRIEVAL", "OPTIMIZATION_COMPLETED", "BYPASS_OPTIMIZATION"]:
                records = cursor.fetchall()
                headers = [desc[0] for desc in cursor.description] if cursor.description else []
                conn.commit()
                
                end_time = time.perf_counter()
                total_time = end_time - start_time
                
                logger.info(f"[SandboxExecution] Data retrieval completed successfully in {total_time:.4f}s. Fetched rows: {len(records)}")

                
                if intent == "BYPASS_OPTIMIZATION":
                    display_msg = "Original slow data fetched successfully (Optimization Bypassed)."
                elif intent == "OPTIMIZATION_COMPLETED":
                    display_msg = "Optimized data fetched successfully!"
                else:
                    display_msg = "Data fetched successfully!"

                return {
                    "execution_result": {
                        "status": "SUCCESS",
                        "headers": headers,
                        "data": records,
                        "message": display_msg
                    },
                    "final_latency": total_time,
                    "explanation": state.get("explanation", "Data fetched via execution pipeline.")
                }
            
            
            else:
                conn.commit()
                end_time = time.perf_counter()
                total_time = end_time - start_time
                
                logger.info(f"[SandboxExecution] Optimization index query executed successfully in {total_time:.4f}s.")
                
                return {
                    "execution_result": {
                        "status": "INDEX_DEPLOYED",
                        "applied_command": command,
                        "message": "Index statement synced."
                    },
                    "final_latency": total_time,
                    "explanation": state.get("explanation", "Index optimization deployed successfully.")
                }

        except sqlite3.Error as sql_err:
            logger.error(f"[SandboxExecution] SQLite runtime constraint failure: {str(sql_err)}")
            return {
                "execution_result": {
                    "status": "CRASHED",
                    "message": f"SQLite Syntax Error: {str(sql_err)}"
                },
                "final_latency": 0.0
            }
        except Exception as e:
            raise CustomException(e, sys)
        finally:
            if conn:
                conn.close()
                logger.info("[SandboxExecution] Database session connection closed safely.")

def sandbox_execution_node(state: AgentState) -> Dict[str, Any]:
    try:
        executor = SandboxExecutionComponent()
        return executor.execute_command(state)
    except Exception as e:
        raise CustomException(e, sys)