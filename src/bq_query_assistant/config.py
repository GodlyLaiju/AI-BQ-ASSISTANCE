import os
from dotenv import load_dotenv

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_GEMINI_MODEL = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-1.5-pro")
BQ_CREDENTIALS = os.getenv("BQ_CREDENTIALS_PATH")
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")

if not all([GOOGLE_API_KEY, BQ_CREDENTIALS, BQ_PROJECT_ID, BQ_DATASET_ID]):
    raise RuntimeError("Missing one or more required environment variables.")
