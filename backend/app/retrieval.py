from typing import List, Dict, Any
from google import genai
from app.config import settings
from app.gemini import embed_query
from app.vector_store import search_vectors

client = genai.Client(api_key=settings.GEMINI_API_KEY)
CHAT_MODEL = "gemini-3.8-flash"
SIMILARITY_THRESHOLD = 0.15

SYSTEM_PROMPT = (
    "You are DocuCite, an expert AI assistant that answers questions accurately "
    "based strictly on the provided document context chunks. "
    "Always cite the source files and page numbers corresponding to the context chunks used."
)

def answer_question(question: str) -> Dict[str, Any]:
    """Embeds the query, retrieves top-k chunks, validates relevance, 
    builds a numbered-context prompt, and calls Gemini for a grounded answer.
    """
    # 1. Embed query
    q_emb = embed_query(question)
    
    # 2. Fetch top-k chunks from vector store
    top_chunks = search_vectors(q_emb, top_k=settings.TOP_K)
    
    # 3. Check similarity threshold fallback
    if not top_chunks or top_chunks[0]["score"] < SIMILARITY_THRESHOLD:
        return {
            "answer": "I couldn't find this in your documents.",
            "citations": []
        }
        
    # 4. Build numbered-context prompt and citations list
    context_str = ""
    citations = []
    
    for idx, chunk in enumerate(top_chunks, start=1):
        context_str += f"[{idx}] File: {chunk['file']} (Page {chunk['page']})\n{chunk['text']}\n\n"
        citations.append({
            "file": chunk["file"],
            "page": chunk["page"],
            "snippet": chunk["text"][:150] + "..."
        })
        
    prompt = f"Context:\n{context_str}\nQuestion: {question}\nAnswer:"
    
    # 5. Call Gemini chat model
    from google.genai.errors import ServerError
    from fastapi import HTTPException

    # Inside your answer_question function:
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
    except ServerError:
        raise HTTPException(
            status_code=503,
            detail="The AI model is currently experiencing high demand. Please wait a few seconds and try your question again."
        )
    
    return {
        "answer": response.text,
        "citations": citations
    }