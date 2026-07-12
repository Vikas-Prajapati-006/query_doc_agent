import os
from dotenv import load_dotenv

load_dotenv()

SLOW_QUERY_THRESHOLD_SEC = 2.0


HITL_PASSKEY = os.getenv("HITL_PASSKEY")

FAISS_PATH_FROM_ENV = os.getenv("FAISS_INDEX_PATH")
DB_FAISS_INDEX_DIR = os.path.join(os.getcwd(), FAISS_PATH_FROM_ENV)

ALLOWED_PATCH_KEYWORDS = ["CREATE", "INDEX", "ON", "ALTER", "TABLE", "ADD", "UNIQUE", "JOIN"]