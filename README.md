# Document Intelligence System (RAG)

Sistem tanya-jawab atas dokumen internal multi-format (PDF, DOCX, PPTX, XLSX, CSV/TXT)
dengan jawaban yang **grounded** dan **bisa ditrace ke sumbernya** (file + halaman/slide/sheet/baris).

> Take-home test — AI Engineer. Python/FastAPI · LlamaIndex · PostgreSQL+pgvector.

## ✨ Fitur
- Ingest multi-format dengan deteksi otomatis + metadata lokasi
- RAG: hybrid retrieval (vektor + keyword) + reranker + grounding
- Jawaban + sitasi yang dapat diklik
- Riwayat chat persisten
- _(TODO: lengkapi saat fitur jadi)_

## 🏗️ Arsitektur
Frontend (React) → API (FastAPI) → RAG Engine (LlamaIndex) → PostgreSQL+pgvector.
Detail keputusan teknis: [TECHNICAL.md](TECHNICAL.md).

## 🧰 Tech Stack
Python 3.12 · FastAPI · LlamaIndex · PostgreSQL+pgvector · uv · Docker
· embedding Jina v3 · LLM Groq · reranker Cohere.

## 🚀 Setup & Run (lokal)
Prasyarat: Docker, uv.

```bash
# 1. Database (Postgres + pgvector)
docker compose up -d db

# 2. Backend
cd backend
cp .env.example .env        # isi API key: Groq, Jina, Cohere
uv sync
uv run uvicorn app.main:app --reload   # tersedia mulai Fase 4
```

## 🔑 Environment Variables
Lihat [backend/.env.example](backend/.env.example).

## 💬 Contoh Q&A
_(TODO: isi setelah pipeline jalan)_

## 📁 Struktur Proyek
```
backend/   — API + RAG (Python, uv)
frontend/  — UI (React) [TODO Fase 5]
```

## 📊 Evaluasi
Eval offline: hit-rate@k/MRR + RAGAS. Detail: [TECHNICAL.md](TECHNICAL.md). _(TODO Fase 3)_

## ☁️ Deployment
Backend → HF Spaces · DB → Supabase · Frontend → Vercel. Detail: [TECHNICAL.md](TECHNICAL.md).

## 📄 License
MIT _(TODO: tambah file LICENSE)_
