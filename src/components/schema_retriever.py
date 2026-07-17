# src/components/schema_retriever.py
import os
import sys
import logging
from typing import Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from src.pipeline.state import AgentState
from src.exception import CustomException


from src.utils.main_utils import MainUtils
from src.constant.database import DB_FAISS_INDEX_DIR

logger = logging.getLogger(__name__)

class SchemaRetrieverComponent:
    def __init__(self, artifacts_path: str = DB_FAISS_INDEX_DIR):
        """
        Initializes the component by loading the serialized FAISS object using MainUtils.
        """
        try:
            self.artifacts_path = artifacts_path
            logger.info("[SchemaRetriever] Loading HuggingFace embedding model...")
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vector_store = None

            
            if os.path.exists(self.artifacts_path):
                logger.info(f"[SchemaRetriever] Loading pickle binary via MainUtils from: {self.artifacts_path}")
                self.vector_store = MainUtils.load_object(file_path=self.artifacts_path)
                logger.info("[SchemaRetriever] FAISS object deserialized successfully.")
            else:
                logger.warning(f"[SchemaRetriever] Vector artifact path not found at: {self.artifacts_path}")

        except Exception as e:
            raise CustomException(e, sys)

    def retrieve_context(self, state: AgentState) -> Dict[str, Any]:
        """
        Searches the FAISS database to get table schemas and past solution logs.
        """
        try:
            query_to_search = state.get("clean_query", "")
            
            if not self.vector_store:
                logger.error("[SchemaRetriever] Search failed: FAISS vector store is not initialized.")
                return {"retrieved_context": "Error: FAISS vector store missing."}

            if not query_to_search:
                logger.warning("[SchemaRetriever] Search skipped: Clean query is empty.")
                return {"retrieved_context": ""}

            logger.info(f"[SchemaRetriever] Searching FAISS for query: '{query_to_search}'")
            
            matching_documents = self.vector_store.similarity_search(query_to_search, k=2)
            combined_context = "\n\n".join([doc.page_content for doc in matching_documents])
            
            logger.info("[SchemaRetriever] Relevant database context fetched successfully from FAISS.")
            
            return {
                "retrieved_context": combined_context
            }

        except Exception as e:
            raise CustomException(e, sys)

def schema_retriever_node(state: AgentState) -> Dict[str, Any]:
    try:
        retriever = SchemaRetrieverComponent()
        return retriever.retrieve_context(state)
    except Exception as e:
        raise CustomException(e, sys)