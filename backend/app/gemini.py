import time
from typing import List
from google import genai
from google.genai import types
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)
EMBEDDING_MODEL = "gemini-embedding-001"  # Updated to current stable embedding model

def embed_documents(texts: List[str]) -> List[List[float]]:
    """Embeds a list of document texts using Gemini with RETRIEVAL_DOCUMENT task type.
    Includes batching (batches of 100) and exponential backoff retry on rate limits.
    """
    if not texts:
        return []
        
    all_embeddings = []
    batch_size = 100
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        success = False
        retries = 3
        delay = 2
        
        while retries > 0 and not success:
            try:
                response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                )
                for emb in response.embeddings:
                    all_embeddings.append(emb.values)
                success = True
            except Exception as e:
                retries -= 1
                if retries == 0:
                    raise RuntimeError(f"Embedding failed after retries: {str(e)}")
                time.sleep(delay)
                delay *= 2
                
    return all_embeddings

def embed_query(text: str) -> List[float]:
    """Embeds a single query string using Gemini with RETRIEVAL_QUERY task type."""
    retries = 3
    delay = 2
    
    for attempt in range(retries):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            )
            return response.embedding.values
        except Exception as e:
            if attempt == retries - 1:
                raise RuntimeError(f"Query embedding failed after retries: {str(e)}")
            time.sleep(delay)
            delay *= 2