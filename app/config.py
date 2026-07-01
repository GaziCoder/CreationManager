import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "outputs")))

# Ensure directories exist
Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
