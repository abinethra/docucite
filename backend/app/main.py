import os
import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.models import User, Document, ChatSession, Message
from app.ingest import process_pdf, chunk_text
from app.vector_store import add_chunks_to_vector_store, list_stored_documents
from app.retrieval import answer_question

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DocuCite API",
    description="Backend for DocuCite RAG Chatbot with PostgreSQL & SQLAlchemy",
    version="1.0.0"
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    username: Optional[str] = "default_user"

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": "DocuCite API",
        "chunk_tokens": settings.CHUNK_TOKENS
    }

@app.post("/documents", tags=["Documents"])
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
        
        # Save document record to DB
        db_doc = Document(filename=filename)
        db.add(db_doc)
        db.commit()
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
    documents = list_stored_documents()
    return {
        "documents": documents,
        "count": len(documents)
    }

@app.post("/chat", tags=["Chat"])
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )
        
    # Ensure default user exists
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        user = User(username=request.username)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Manage or create chat session
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(id=session_id, user_id=user.id, title=request.question[:30])
        db.add(chat_session)
        db.commit()
    else:
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not chat_session:
            chat_session = ChatSession(id=session_id, user_id=user.id, title=request.question[:30])
            db.add(chat_session)
            db.commit()

    # Get RAG answer & citations
    result = answer_question(request.question)
    
    # Save message to DB
    db_message = Message(
        session_id=session_id,
        question=request.question,
        answer=result["answer"],
        citations=result["citations"]
    )
    db.add(db_message)
    db.commit()
    
    return {
        "session_id": session_id,
        "answer": result["answer"],
        "citations": result["citations"]
    }

@app.get("/chats/{session_id}", tags=["Chat"])
async def get_chat_session(session_id: str, db: Session = Depends(get_db)):
    chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )
        
    messages = []
    for msg in chat_session.messages:
        messages.append({
            "question": msg.question,
            "answer": msg.answer,
            "citations": msg.citations,
            "created_at": msg.created_at
        })
        
    return {
        "session_id": chat_session.id,
        "title": chat_session.title,
        "created_at": chat_session.created_at,
        "messages": messages
    }