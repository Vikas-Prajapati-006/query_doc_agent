import os
import sys
import pickle
from src.logger import logging
from src.exception import CustomException

class MainUtils:
    def __init__(self):
        pass

    @staticmethod
    def save_object(file_path: str, obj: object) -> None:
        """
        Saves a python object (like models, pickles, vector indexes) into a local file directory.
        """
        try:
            logging.info(f"Attempting to save object binary serialization at: {file_path}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "wb") as file_obj:
                pickle.dump(obj, file_obj)
                
            logging.info(f"Successfully serialized and locked object at destination.")
        except Exception as e:
            raise CustomException(e, sys)

    @staticmethod
    def load_object(file_path: str) -> object:
        """
        Loads and de-serializes a binary object file back into python context.
        """
        try:
            logging.info(f"Attempting to load binary object from path: {file_path}")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Requested object file binary not found at: {file_path}")
                
            with open(file_path, "rb") as file_obj:
                obj = pickle.load(file_obj)
                
            logging.info("Successfully fetched and deserialized object runtime memory.")
            return obj
        except Exception as e:
            raise CustomException(e, sys)