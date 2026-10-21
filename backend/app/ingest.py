import os
from typing import List, Dict, Any
from pypdf import PdfReader
import tiktoken
from app.config import settings

def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extracts text page by page from a PDF file using pypdf."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    reader = PdfReader(pdf_path)
    pages_data = []
    
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text or not text.strip():
            text = ""  # Fallback for scanned or empty pages
            
        pages_data.append({
            "page": page_num,
            "text": text
        })
        
    return pages_data

def chunk_text(pages_data: List[Dict[str, Any]], filename: str, chunk_tokens: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """Chunks page text into token-sized segments with overlap and metadata."""
    encoding = tiktoken.get_encoding("cl100k_base")
    all_chunks = []
    
    for page_info in pages_data:
        page_num = page_info["page"]
        text = page_info["text"]
        
        if not text.strip():
            continue
            
        tokens = encoding.encode(text)
        if not tokens:
            continue
            
        chunk_index = 0
        start = 0
        while start < len(tokens):
            end = min(start + chunk_tokens, len(tokens))
            chunk_token_slice = tokens[start:end]
            chunk_text_str = encoding.decode(chunk_token_slice)
            
            all_chunks.append({
                "file": filename,
                "page": page_num,
                "chunk_index": chunk_index,
                "text": chunk_text_str
            })
            
            chunk_index += 1
            if end == len(tokens):
                break
            start += (chunk_tokens - overlap)
            
    return all_chunks

def process_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    filename = os.path.basename(pdf_path)
    pages = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(
        pages, 
        filename=filename, 
        chunk_tokens=settings.CHUNK_TOKENS, 
        overlap=settings.CHUNK_OVERLAP
    )
    return chunks