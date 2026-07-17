import os
import sys
import logging
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.pipeline.state import AgentState
from src.exception import CustomException

logger = logging.getLogger(__name__)

class QueryAgentComponent:
    def __init__(self):
        """
        Initializes the Query Agent with Groq LLM using Llama model.
        """
        try:
            logger.info("[QueryAgent] Connecting to Groq Cloud LLM backend...")
            self.llm = ChatGroq(
                       model="llama-3.1-8b-instant", 
                       temperature=0.0
                          )
            logger.info("[QueryAgent] Groq Llama model linked successfully.")
        except Exception as e:
            raise CustomException(e, sys)

    def classify_intent(self, state: AgentState) -> Dict[str, Any]:
        """
        Reads the clean query and classifies if it is a normal data request 
        or an optimization task using ChatPromptTemplate.
        """
        try:
            query = state.get("clean_query", "")
            logger.info(f"[QueryAgent] Classifying intent for query: '{query}'")

            intent_template = ChatPromptTemplate.from_messages([
                ("system", 
                 "You are an expert database administrator.\n"
                 "Analyze the user input and classify its intent into exactly one of these two categories:\n"
                 "1. DATA_RETRIEVAL -> If the user wants to fetch, see, or read records from the database.\n"
                 "2. INDEX_OPTIMIZATION -> If the input is a system slow log report or asks to optimize performance.\n"
                 "Respond with ONLY the category string, nothing else. Do not add explanations or punctuation."),
                ("user", "Classify this input: {user_query}")
            ])

            formatted_prompt = intent_template.format_messages(user_query=query)
            response = self.llm.invoke(formatted_prompt)
            intent_result = response.content.strip().upper()

            final_intent = "INDEX_OPTIMIZATION" if "INDEX" in intent_result else "DATA_RETRIEVAL"
            logger.info(f"[QueryAgent] Detected Intent: '{final_intent}'")
            
            return {"intent": final_intent}

        except Exception as e:
            raise CustomException(e, sys)

    def generate_command(self, state: AgentState) -> Dict[str, Any]:
        """
        Generates the final SQL execution command or Index patch script based on the intent and FAISS context.
        """
        try:
            intent = state.get("intent", "DATA_RETRIEVAL")
            query = state.get("clean_query", "")
            context = state.get("retrieved_context", "")

            logger.info(f"[QueryAgent] Generating command for intent: '{intent}'")

            
            if intent == "INDEX_OPTIMIZATION":
                system_instruction = (
                    "You are an expert SQL Tuning Agent.\n"
                    "Analyze the slow query log and the database schema provided in the context.\n"
                    "Generate a high-performance 'CREATE INDEX' statement to optimize the slow column to O(log N) speed.\n"
                    "CRITICAL: Under the 'COMMAND:' section, output the raw SQL script ONLY. Do NOT wrap the query in backticks (`), quotes, or markdown code blocks (```sql).\n"
                    "Provide your response in exactly this format:\n"
                    "COMMAND: <your SQL index script here>\n"
                    "EXPLANATION: <1-line simple reason why this column needs an index>"
                )
            else:
                system_instruction = (
                    "You are a helpful text-to-SQL assistant.\n"
                    "Convert the natural language query into a clean SQLite SELECT statement using the provided schema context.\n"
                    "CRITICAL: Under the 'COMMAND:' section, output the raw SQL statement ONLY. Do NOT wrap the query in backticks (`), quotes, or markdown code blocks (```sql).\n"
                    "Provide your response in exactly this format:\n"
                    "COMMAND: <your SQL select statement here>\n"
                    "EXPLANATION: <1-line reason explaining what data is being fetched>"
                )

            command_template = ChatPromptTemplate.from_messages([
                ("system", system_instruction),
                ("user", "Context Schema & History:\n{db_context}\n\nTarget Input:\n{user_query}")
            ])

            formatted_prompt = command_template.format_messages(db_context=context, user_query=query)
            response = self.llm.invoke(formatted_prompt)
            output_text = response.content.strip()

            command_out = ""
            explanation_out = ""
            
            for line in output_text.split("\n"):
                if line.startswith("COMMAND:"):
                    
                    command_out = line.replace("COMMAND:", "").replace("`", "").replace("sql", "").strip()
                elif line.startswith("EXPLANATION:"):
                    explanation_out = line.replace("EXPLANATION:", "").strip()

            logger.info("[QueryAgent] Successfully generated command matrix from LLM.")
            
            if intent == "INDEX_OPTIMIZATION":
                return {
                    "generated_index_command": command_out,
                    "generated_command": state.get("generated_command"), 
                    "explanation": explanation_out
                }
            else:
                return {
                    "generated_command": command_out,
                    "generated_index_command": None,
                    "explanation": explanation_out
                }

        except Exception as e:
            raise CustomException(e, sys)


def intent_classifier_node(state: AgentState) -> Dict[str, Any]:
    try:
        agent = QueryAgentComponent()
        return agent.classify_intent(state)
    except Exception as e:
        raise CustomException(e, sys)

def command_generator_node(state: AgentState) -> Dict[str, Any]:
    try:
        agent = QueryAgentComponent()
        return agent.generate_command(state)
    except Exception as e:
        raise CustomException(e, sys)