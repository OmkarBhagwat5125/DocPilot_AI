**DocPilot AI** is a full-stack RAG-based document intelligence platform that lets users upload documents (PDF, DOCX, PPTX, CSV, TXT) and ask natural-language questions about them, getting back answers with cited sources.

**How it works:** Uploaded files are parsed, chunked, embedded (BGE-small-en-v1.5 via FastEmbed), and stored as vectors in Qdrant, with raw files kept in Supabase Storage. User queries are embedded and matched against these vectors (scoped per user), and Gemini 2.5 Flash generates the final cited answer.

**Stack:**
- **Frontend:** React 19 + Vite, Supabase Auth
- **Backend:** FastAPI + Uvicorn
- **Vector DB:** Qdrant
- **Storage/Auth:** Supabase

**Core API:** upload, query, list, and delete documents — all authenticated via Supabase JWT bearer tokens.

In short: it's a personal, authenticated "chat with your documents" tool with a modern RAG pipeline end to end.