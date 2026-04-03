import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """
    Application configuration loaded from environment variables.
    """

    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    CLINICAL_API = os.getenv("CLINICAL_API", "https://clinicaltrials.gov/api/v2/")
    GEMINI_API = os.getenv("GEMINI_API", "")
    GEMINI_API_2 = os.getenv("GEMINI_API_2", "")
    GEMINI_API_3 = os.getenv("GEMINI_API_3", "")
    CSV_PATH = os.getenv("CSV_PATH", str(BASE_DIR / "db" / "ClinicalTrialsDB.csv"))
    JSON_PATH = os.getenv("JSON_PATH", str(BASE_DIR / "db" / "ClinicalTrialsDB.json"))
    MISTRAL_AI_API = os.getenv("MISTRAL_AI_API", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPBRICKS_API_KEY = os.getenv("DEEPBRICKS_API_KEY", "")
    TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY", "")
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("PORT", os.getenv("FLASK_PORT", "7860")))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
