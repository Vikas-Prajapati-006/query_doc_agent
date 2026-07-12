import os
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.logger import logging
from src.exception import CustomException
from src.utils.main_utils import MainUtils
from src.constant.database import DB_FAISS_INDEX_DIR

class DataIngestion:
    def __init__(self):
        
        logging.info("Initializing HuggingFaceEmbeddings model (all-MiniLM-L6-v2)...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def initiate_data_ingestion(self):
        logging.info("Starting data ingestion process...")
        try:
            
            raw_schemas = [
                "Table: users | Columns: id, username, email, created_at | Info: Contains user registration and profile details.",
                "Table: orders | Columns: order_id, user_id, product_id, amount, status | Info: Tracks all customer purchases and transaction statuses.",
                "Table: products | Columns: product_id, name, price, stock_count | Info: Stores inventory items, pricing, and available stock.",
                "Table: query_logs | Columns: log_id, query_text, execution_time_sec, status | Info: Database system logs tracking query performance metrics."
            ]
            
            logging.info(f"Successfully loaded {len(raw_schemas)} database schema descriptions.")

            
            logging.info("Generating mathematical vectors and organizing into FAISS inside RAM...")
            vector_store = FAISS.from_texts(texts=raw_schemas, embedding=self.embeddings)
            logging.info("FAISS Vector Store successfully generated in memory.")

            
            logging.info(f"Calling MainUtils to automatically serialize and dump index at: {DB_FAISS_INDEX_DIR}")
            
           
            MainUtils.save_object(file_path=DB_FAISS_INDEX_DIR, obj=vector_store)
            
            logging.info("Data Ingestion completed successfully! Vectors are locked on disk.")
            return DB_FAISS_INDEX_DIR

        except Exception as e:
            logging.error("Exception occurred during data ingestion process.")
            raise CustomException(e, sys)

if __name__ == "__main__":
    
    ingestion_engine = DataIngestion()
    ingestion_engine.initiate_data_ingestion()