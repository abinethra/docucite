import os
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from app.config import settings
from app.ingest import process_pdf, chunk_text
from app.vector_store import add_chunks_to_vector_store, list_stored_documents
from app.retrieval import answer_question

app = FastAPI(
    title="DocuCite API",
    description="Backend for DocuCite RAG Chatbot",
    version="1.0.0"
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

class ChatRequest(BaseModel):
    question: str

@app.get("/health", tags=["Health"])
async def health_check():
    """Verify that the API is running and configuration is accessible."""
    return {
        "status": "healthy",
        "app": "DocuCite API",
        "chunk_tokens": settings.CHUNK_TOKENS
    }

@app.post("/documents", tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or TXT document, validate size and type, chunk, embed, and store locally."""
    filename = file.filename or "unknown"
    ext = filename.split(".")[-1].lower()
    
    if ext not in ["pdf", "txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and TXT files are supported."
        )
        
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10 MB limit."
        )
        
    temp_path = f"./temp_{filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)
        
    try:
        if ext == "pdf":
            chunks = process_pdf(temp_path)
        else:
            text_content = contents.decode("utf-8", errors="ignore")
            pages_data = [{"page": 1, "text": text_content}]
            chunks = chunk_text(pages_data, filename=filename, chunk_tokens=settings.CHUNK_TOKENS, overlap=settings.CHUNK_OVERLAP)
            
        add_chunks_to_vector_store(chunks)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return {
        "filename": filename,
        "status": "success",
        "chunks_stored": len(chunks)
    }

@app.get("/documents", tags=["Documents"])
async def get_documents():
    """List all uploaded documents currently stored in the vector index."""
    documents = list_stored_documents()
    return {
        "documents": documents,
        "count": len(documents)
    }

@app.post("/chat", tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """Ask a question against your uploaded documents using RAG and Gemini."""
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )
        
    result = answer_question(request.question)
    return result