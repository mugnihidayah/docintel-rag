---
title: DocIntel API
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# DocIntel API

FastAPI backend for the Document Intelligence System — RAG over multi-format documents
with traceable citations. Runs as a Hugging Face **Docker** Space.

## Required Space secrets
| Secret | Notes |
|---|---|
| `DATABASE_URL` | Supabase Postgres (asyncpg), session pooler or direct connection |
| `LLM_API_KEY` | Groq |
| `EMBEDDING_API_KEY` | Jina |
| `COHERE_API_KEY` | reranker (or set `RERANK_ENABLED=false`) |
| `ALLOWED_ORIGINS` | your frontend origin, e.g. `https://your-app.vercel.app` |
| `API_KEY` | optional, protects upload/delete |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL` | optional tracing |

The container applies Alembic migrations on start, then serves on port 8000.
See `DEPLOY.md` in the repo root for full step-by-step instructions.
