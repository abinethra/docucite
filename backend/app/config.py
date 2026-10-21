from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DATABASE_URL: str
    CHROMA_PATH: str = "./vector_db"
    CHUNK_TOKENS: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 4

    class Config:
        env_file = ".env"

settings = Settings()