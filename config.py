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

# RAG
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

# PDF Font fallback
DEFAULT_FONT = "helv"
DEFAULT_FONT_SIZE = 11.0
DEFAULT_FONT_COLOR = (0, 0, 0)
