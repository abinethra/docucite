import pytest
from unittest.mock import MagicMock, patch
from app.ingest import extract_text_from_pdf, chunk_text

@patch("app.ingest.os.path.exists", return_value=True)
@patch("app.ingest.PdfReader")
def test_extract_text_from_pdf(mock_pdf_reader, mock_exists):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample text from PDF page."
    mock_pdf_reader.return_value.pages = [mock_page]

    pages = extract_text_from_pdf("dummy.pdf")
    
    assert len(pages) == 1
    assert pages[0]["page"] == 1
    assert pages[0]["text"] == "Sample text from PDF page."

def test_chunk_text():
    pages_data = [
        {"page": 1, "text": "This is a test document used to verify chunking behavior in DocuCite."}
    ]
    chunks = chunk_text(pages_data, filename="sample.pdf", chunk_tokens=10, overlap=2)
    
    assert len(chunks) > 0
    assert chunks[0]["file"] == "sample.pdf"
    assert chunks[0]["page"] == 1
    assert chunks[0]["chunk_index"] == 0
    assert "text" in chunks[0]