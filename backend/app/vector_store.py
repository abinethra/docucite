import os
import json
import numpy as np
from typing import List, Dict, Any
from app.config import settings
from app.gemini import embed_documents

VECTOR_DIR = settings.CHROMA_PATH
os.makedirs(VECTOR_DIR, exist_ok=True)
INDEX_FILE = os.path.join(VECTOR_DIR, "vector_index.json")

def _load_store() -> List[Dict[str, Any]]:
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_store(data: List[Dict[str, Any]]) -> None:
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_chunks_to_vector_store(chunks: List[Dict[str, Any]]) -> None:
    """Generates embeddings for chunks and stores them locally."""
    if not chunks:
        return
        
    texts = [c["text"] for c in chunks]
    embeddings = embed_documents(texts)
    
    store_data = _load_store()
    
    for c, emb in zip(chunks, embeddings):
        store_data.append({
            "id": f"{c['file']}_p{c['page']}_c{c['chunk_index']}",
            "file": c["file"],
            "page": c["page"],
            "chunk_index": c["chunk_index"],
            "text": c["text"],
            "embedding": emb
        })
        
    _save_store(store_data)

def list_stored_documents() -> List[str]:
    """Retrieves a unique sorted list of uploaded filenames."""
    store_data = _load_store()
    if not store_data:
        return []
    return sorted(list(set(item["file"] for item in store_data if "file" in item)))

def search_vectors(query_embedding: List[float], top_k: int = 4) -> List[Dict[str, Any]]:
    """Performs cosine similarity search against stored chunk embeddings."""
    store_data = _load_store()
    if not store_data:
        return []
        
    q_vec = np.array(query_embedding)
    results = []
    
    for item in store_data:
        doc_vec = np.array(item["embedding"])
        norm_q = np.linalg.norm(q_vec)
        norm_doc = np.linalg.norm(doc_vec)
        
        if norm_q == 0 or norm_doc == 0:
            similarity = 0.0
        else:
            similarity = float(np.dot(q_vec, doc_vec) / (norm_q * norm_doc))
            
        results.append({
            "file": item["file"],
            "page": item["page"],
            "chunk_index": item["chunk_index"],
            "text": item["text"],
            "score": similarity
        })
        
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]