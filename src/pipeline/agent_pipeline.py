import sys
import logging
import sqlite3
from typing import Dict, Any
from langgraph.graph import StateGraph, END, START 
from langgraph.checkpoint.memory import MemorySaver  

from src.pipeline.state import AgentState
from src.exception import CustomException

from src.components.log_parser import log_parser_node
from src.components.schema_retriever import schema_retriever_node
from src.components.query_agent import intent_classifier_node, command_generator_node
from src.components.sandbox_execution import sandbox_execution_node

logger = logging.getLogger(__name__)

def hitl_gate_node(state: AgentState) -> AgentState:
    logger.info("[HITL_Gate] Paused. Awaiting admin approval to run DDL Indexing query.")
    return state

def run_indexing_node(state: AgentState) -> Dict[str, Any]:
    try:
        index_query = state.get("generated_index_command")
        if index_query:
            logger.info(f"[PatchEngine] Admin Approved. Deploying Index Patch: {index_query}")
            conn = sqlite3.connect("database.db")
            conn.execute(index_query)
            conn.commit()
            conn.close()
            logger.info("[PatchEngine] Database performance index deployed successfully.")
            
        return {"intent": "OPTIMIZATION_COMPLETED"}
    except Exception as e:
        raise CustomException(e, sys)


def handle_latency_breach_node(state: AgentState) -> Dict[str, Any]:
    logger.warning("[StateModifier] Latency breach handled. Modifying intent to INDEX_OPTIMIZATION for LLM patch.")
    return {
        "intent": "INDEX_OPTIMIZATION" 
    }


def pre_execution_router(state: AgentState) -> str:
    try:
        intent = state.get("intent", "DATA_RETRIEVAL")
        if intent == "INDEX_OPTIMIZATION":
            return "route_to_hitl"
        return "route_to_sandbox"
    except Exception as e:
        raise CustomException(e, sys)


def post_sandbox_router(state: AgentState) -> str:
    try:
        latency = state.get("final_latency", 0.0)
        intent = state.get("intent", "DATA_RETRIEVAL")
        
        if intent in ["OPTIMIZATION_COMPLETED", "BYPASS_OPTIMIZATION", "ABORTED"]:
            return "exit_to_end"
            
        
        if intent == "DATA_RETRIEVAL" and latency > 0.001:
            logger.warning(f"[Router2] Latency Breach ({latency}s > 0.001s). Routing to modifier node.")
            return "route_to_modifier"
            
        return "exit_to_end"
    except Exception as e:
        raise CustomException(e, sys)


def hitl_choice_router(state: AgentState) -> str:
    try:
        intent = state.get("intent")
        if intent == "BYPASS_OPTIMIZATION":
            return "skip_indexing_to_sandbox"
        return "execute_indexing"
    except Exception as e:
        raise CustomException(e, sys)

def create_agent_pipeline():
    try:
        workflow = StateGraph(AgentState)

        
        workflow.add_node("log_parser", log_parser_node)
        workflow.add_node("schema_retriever", schema_retriever_node)
        workflow.add_node("intent_classifier", intent_classifier_node)
        workflow.add_node("command_generator", command_generator_node)
        workflow.add_node("sandbox_execution", sandbox_execution_node)
        workflow.add_node("hitl_gate", hitl_gate_node)
        workflow.add_node("run_indexing", run_indexing_node)
        workflow.add_node("handle_latency_breach", handle_latency_breach_node) 

        
        workflow.add_edge(START, "log_parser")
        workflow.add_edge("log_parser", "schema_retriever")
        workflow.add_edge("schema_retriever", "intent_classifier")
        workflow.add_edge("intent_classifier", "command_generator")

        workflow.add_conditional_edges(
            "command_generator",
            pre_execution_router,
            {"route_to_hitl": "hitl_gate", "route_to_sandbox": "sandbox_execution"}
        )

        workflow.add_conditional_edges(
            "hitl_gate",
            hitl_choice_router,
            {"execute_indexing": "run_indexing", "skip_indexing_to_sandbox": "sandbox_execution"}
        )
        
        workflow.add_edge("run_indexing", "sandbox_execution")

        workflow.add_conditional_edges(
            "sandbox_execution",
            post_sandbox_router,
            {
                "route_to_modifier": "handle_latency_breach", 
                "exit_to_end": END
            }
        )
        
        
        workflow.add_edge("handle_latency_breach", "command_generator")

        memory = MemorySaver()
        compiled_graph = workflow.compile(
            checkpointer=memory,
            interrupt_before=["hitl_gate"]
        )
        return compiled_graph
    except Exception as e:
        raise CustomException(e, sys)

app_pipeline = create_agent_pipeline()