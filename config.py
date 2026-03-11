"""
DocuMind AI — Configuration
"""
import os
from dotenv import load_dotenv

# Load .env from the same directory as the main app
_base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, ".env"))

# App
APP_TITLE = "DocuMind AI"
APP_ICON = "🧠"

APP_PASSWORD = os.getenv("APP_PASSWORD", "")

# RAG
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "gemma-7b-it"
]
# PDF Font fallback
DEFAULT_FONT = "helv"
DEFAULT_FONT_SIZE = 11.0
DEFAULT_FONT_COLOR = (0, 0, 0)
