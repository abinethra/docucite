from fastapi import FastAPI
from app.config import settings

# Initialize FastAPI application
app = FastAPI(
    title="DocuCite API",
    description="Backend for DocuCite RAG Chatbot",
    version="1.0.0"
)

@app.get("/health", tags=["Health"])
async def health_check():
    """Verify that the API is running and configuration is accessible."""
    return {
        "status": "healthy",
        "app": "DocuCite API",
        "chunk_tokens": settings.CHUNK_TOKENS
    }