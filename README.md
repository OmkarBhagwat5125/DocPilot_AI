# DocPilot AI

**Upload. Ask. Understand.**

A full-stack document intelligence platform built with FastAPI, React, and RAG (Retrieval-Augmented Generation). Upload documents (PDF, DOCX, PPTX, CSV, TXT), ask natural-language questions, and get answers with cited sources.

## Architecture

User uploads file  ──►  Parse (PDF/DOCX/PPTX/CSV/TXT)
                    ──►  Chunk (RecursiveCharacterTextSplitter)
                    ──►  Embed (BGE-small-en-v1.5, 384-dim)
                    ──►  Store vectors in Qdrant
                    ──►  Store raw file in Supabase Storage

User asks question ──►  Embed question
                    ──►  Vector search in Qdrant (user-scoped)
                    ──►  Gemini 2.5 Flash generates answer with citations

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Supabase Auth (email/password) |
| Backend | FastAPI, Uvicorn |
| LLM | Gemini 2.5 Flash |
| Vector DB | Qdrant (local or cloud) |
| Embeddings | BAAI/bge-small-en-v1.5 via FastEmbed |
| File Storage | Supabase Storage |
| Auth | Supabase Auth (JWT Bearer) |

## Prerequisites

- Python 3.10+
- Node.js 18+
- Supabase project (free tier)
- Gemini API key (free tier)

## Setup

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd DocPilot AI
cp .env.example .env
```

Fill in your keys in `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

Also add these frontend-facing vars in the same `.env`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

> Leave `QDRANT_URL` empty for local file-based storage (data lives in `qdrant_db/`).

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
cd ..
uvicorn backend.app.main:app --reload --port 8000
```

The API starts at `http://localhost:8000`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app opens at `http://localhost:3000`.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/` | No | Health check |
| `POST` | `/api/upload` | Bearer | Upload a document |
| `POST` | `/api/query` | Bearer | Ask a question |
| `GET` | `/api/documents` | Bearer | List user's documents |
| `DELETE` | `/api/documents/{filename}` | Bearer | Delete a document |

All API routes (except health check) require a Supabase JWT in the `Authorization: Bearer <token>` header.

## Project Structure

```
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI entry point
│       ├── api/endpoints.py     # All routes
│       ├── core/config.py       # Settings & env vars
│       ├── core/auth.py         # JWT auth dependency
│       └── services/
│           ├── chat.py          # Gemini answer generation
│           ├── document_parser.py
│           ├── embedding.py     # FastEmbed wrapper
│           ├── storage.py       # Supabase Storage
│           └── vector_db.py     # Qdrant service
├── frontend/
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx              # Root component
│       ├── lib/
│       │   ├── api.js           # API client
│       │   └── supabase.js      # Supabase client
│       └── components/
│           ├── AuthScreen.jsx   # Login / Sign up
│           ├── Sidebar.jsx      # Upload + document list
│           └── ChatArea.jsx     # Chat interface
├── .env.example
└── qdrant_db/                   # Local vector storage (gitignored)
```
