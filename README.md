<div align="center">

# 📚 DocuCite

### Chat with your documents. Every answer comes with its source.

A citation-first **Retrieval-Augmented Generation (RAG)** chatbot. Upload PDFs or text files, ask questions in plain English, and get answers grounded in your documents, with clickable citations to the exact file and page. If the answer isn't in your documents, it says so instead of guessing.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**[Live Demo](#)** · **[Demo Video](#)** · **[Report a Bug](../../issues)**

</div>

---

## 🎬 Demo

> Replace this with a GIF or screenshot of: upload a PDF → ask a question → streamed answer with citation chips → click a chip to see the source passage.

![DocuCite demo](docs/demo.gif)

---

## ✨ Features

- **Document ingestion:** upload PDF and TXT files; text is extracted page by page.
- **Smart chunking:** 500-token chunks with 50-token overlap, so context isn't lost at boundaries.
- **Semantic search:** chunks are embedded with Gemini embeddings and stored in ChromaDB with file and page metadata.
- **Grounded answers:** the model answers *only* from retrieved context, using Gemini generation.
- **Clickable citations:** every answer shows source chips (`file.pdf · p. 12`) that open the exact passage.
- **"Not found" handling:** a clear fallback message when the documents don't contain the answer.
- **Streaming responses:** answers appear token by token in the React UI.
- **Persistent chat history:** sessions are stored in PostgreSQL.
- **Per-user isolation:** users can only search their own documents.
- **Evaluation suite:** a 20-question benchmark to measure answer accuracy and compare chunk size and top-k settings.

---

## 🏗️ Architecture

```mermaid
flowchart LR
    U[User] --> F[React Frontend]
    F -->|POST /documents| B[FastAPI Backend]
    F -->|POST /chat - streamed| B
    B --> P[(PostgreSQL<br/>users, documents, chats)]
    B --> C[(ChromaDB<br/>vectors + metadata)]
    B -->|embed + generate| G[Gemini API]
```

**Ingestion flow:** Upload → extract text per page (`pypdf`) → chunk (500 / 50) → embed with Gemini → store vectors with `{file, page}` metadata in ChromaDB → record the document in PostgreSQL.

**Query flow:** Question → embed → retrieve top-4 chunks (filtered by user) → build a grounded prompt → Gemini streams an answer → return answer + citations → save to chat history.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite), Tailwind CSS |
| Backend | FastAPI, Uvicorn, Pydantic |
| Database | PostgreSQL (SQLAlchemy) |
| Vector store | ChromaDB |
| AI / ML | Google Gemini (embeddings + generation), `pypdf` |
| Auth | JWT (passlib + bcrypt) |
| Deployment | Render (backend, persistent disk), Vercel (frontend) |

---

## 📁 Project Structure

```
docucite/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app and routes
│   │   ├── config.py        # settings from environment variables
│   │   ├── gemini.py        # embedding + generation helpers
│   │   ├── ingest.py        # PDF extraction and chunking
│   │   ├── retrieval.py     # vector search and prompt building
│   │   ├── models.py        # SQLAlchemy tables
│   │   ├── schemas.py       # Pydantic models
│   │   ├── auth.py          # JWT login / register
│   │   └── db.py
│   ├── eval/
│   │   ├── questions.json   # 20 questions with expected answers
│   │   └── run_eval.py      # accuracy benchmark
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── components/      # ChatWindow, UploadPanel, CitationChip, SourceModal
│       ├── pages/
│       └── api.js
├── docs/
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+ (or use SQLite for local development)
- A Gemini API key from [Google AI Studio](https://aistudio.google.com)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/docucite.git
cd docucite
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env
uvicorn app.main:app --reload
```

`.env` file:

```env
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/docucite
CHROMA_PATH=./chroma_data
JWT_SECRET=change-this-to-a-long-random-string
EMBED_MODEL=gemini-embedding-001
CHAT_MODEL=gemini-2.5-flash
CHUNK_TOKENS=500
CHUNK_OVERLAP=50
TOP_K=4
```

> Model names change over time. Check the Google AI Studio docs for current names.

The API runs at `http://localhost:8000`, with interactive docs at `/docs`.

### 3. Frontend setup

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

Open `http://localhost:5173`.

> ⚠️ Never commit `.env` or expose your API key in frontend code. Only the backend calls Gemini.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create an account |
| `POST` | `/auth/login` | Get a JWT token |
| `POST` | `/documents` | Upload and ingest a PDF or TXT file |
| `GET` | `/documents` | List the current user's documents |
| `DELETE` | `/documents/{id}` | Remove a document and its vectors |
| `POST` | `/chat` | Ask a question; streams the answer, then returns citations |
| `GET` | `/chats/{session_id}` | Retrieve a saved conversation |

**Example: `POST /chat`**

```json
{
  "session_id": "b2f1...",
  "question": "What is the passing criteria for the internal assessment?"
}
```

**Response (final event)**

```json
{
  "answer": "The internal assessment requires a minimum of 50% ...",
  "citations": [
    { "file": "syllabus.pdf", "page": 14, "snippet": "Internal assessment ..." }
  ]
}
```

---

## 🧠 How the RAG Pipeline Works

1. **Extract:** `pypdf` reads each page and keeps the page number.
2. **Chunk:** text is split into ~500-token chunks with 50-token overlap; each chunk keeps `{file, page}` metadata.
3. **Embed:** each chunk is converted to a vector with the Gemini embedding model (document task type).
4. **Store:** vectors and metadata are saved in ChromaDB under the user's collection.
5. **Retrieve:** the question is embedded (query task type) and the top-4 most similar chunks are fetched.
6. **Generate:** a strict prompt tells Gemini to answer only from the numbered context and to cite sources.
7. **Cite:** the response includes the chunks used so the UI can render clickable citations.

### Grounding prompt (core of the project)

The model is instructed to use only the supplied context, cite using `[1]`, `[2]` markers, and reply with *"I couldn't find this in your documents."* when the context is insufficient. See [`backend/app/retrieval.py`](backend/app/retrieval.py).

---

## 📊 Evaluation

I built a 20-question benchmark with known answers from my test documents and measured how often the chatbot answered correctly **and** cited the right page.

| Chunk size | Overlap | Top-k | Answer accuracy | Correct citation | Avg latency |
|---|---|---|---|---|---|
| 300 | 30 | 3 | _XX%_ | _XX%_ | _X.X s_ |
| **500** | **50** | **4** | _XX%_ | _XX%_ | _X.X s_ |
| 800 | 100 | 4 | _XX%_ | _XX%_ | _X.X s_ |
| 500 | 50 | 6 | _XX%_ | _XX%_ | _X.X s_ |

**Key findings:** _(Fill in after running. For example: "500/50 with top-4 gave the best accuracy; larger chunks hurt citation precision.")_

Run it yourself:

```bash
cd backend
python eval/run_eval.py --chunk 500 --overlap 50 --k 4
```

---

## 🔒 Security and Privacy

- API keys live only in environment variables on the server.
- Per-user collections ensure one user can never retrieve another user's chunks.
- Upload validation: file type and size limits.
- Rate limiting on `/chat` and `/documents`.
- Passwords are hashed with bcrypt; sessions use JWT.
- Retrieved document text is treated as untrusted data, and the prompt instructs the model to ignore any instructions found inside documents (a basic defense against prompt injection).

---

## ⚠️ Limitations

- Scanned (image-only) PDFs need OCR, which isn't included yet.
- Tables and multi-column layouts can extract poorly.
- Answers are only as good as retrieval; very vague questions may retrieve irrelevant chunks.
- The model can still occasionally misread context, so always check the cited source.

---

## 🗺️ Roadmap

- [ ] Hybrid search (BM25 + vector)
- [ ] Re-ranking of retrieved chunks
- [ ] Conversation memory with query rewriting
- [ ] OCR support for scanned PDFs
- [ ] DOCX and PPTX ingestion
- [ ] Highlight the cited passage inside an in-app PDF viewer

---

## ☁️ Deployment

- **Backend:** Render web service with a persistent disk mounted for `CHROMA_PATH` (or use a hosted Chroma instance). Set all `.env` variables in the Render dashboard.
- **Database:** Render PostgreSQL or Neon.
- **Frontend:** Vercel, with `VITE_API_URL` pointing to the Render URL.
- Enable CORS on the backend only for your Vercel domain.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

## 👤 Author

**Abi Nethra**
2nd-year B.Tech, Artificial Intelligence and Data Science
[GitHub](https://github.com/<your-username>) · [LinkedIn](https://linkedin.com/in/<your-profile>)

---

<div align="center">
If this project helped you, consider giving it a ⭐
</div>