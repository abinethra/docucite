import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the backend root
load_dotenv()

class Settings:
    """Centralized configuration class to load and type environment variables."""
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/docucite")
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_db")
    CHUNK_TOKENS: int = int(os.getenv("CHUNK_TOKENS", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K: int = int(os.getenv("TOP_K", "4"))

# Instantiate settings so it can be imported cleanly across modules
settings = Settings()