# Deployment Guide

Split deploy (all free tier):

```
Vercel (frontend)  ──HTTPS──►  HF Spaces (FastAPI, Docker)  ──►  Supabase (Postgres + pgvector)
```

Order: **Supabase → HF Spaces → Vercel** (each needs the previous one's URL/keys).

---

## 1. Supabase (database)

1. Create a project at [supabase.com](https://supabase.com) (pick a region close to you).
2. **Enable pgvector**: Dashboard → Database → Extensions → enable **`vector`**.
   (or run in the SQL editor: `create extension if not exists vector;`)
3. Get the connection string: Dashboard → Project Settings → Database → **Connection string**.
   - Use the **Session pooler** (or **Direct connection**) — *not* the Transaction pooler.
     asyncpg uses prepared statements, which the transaction pooler (pgbouncer) breaks.
   - Convert it to the asyncpg driver and keep it for the next step:
     ```
     DATABASE_URL=postgresql+asyncpg://postgres.<ref>:<password>@<host>:5432/postgres
     ```

> The backend auto-creates the vector table + runs Alembic migrations (`documents` table) on
> first start, so no manual schema setup is needed beyond enabling the extension.

---

## 2. Hugging Face Spaces (backend)

1. Create a new **Space** at [huggingface.co/new-space](https://huggingface.co/new-space) →
   SDK = **Docker** (blank template).
2. Push **the contents of `backend/`** to the Space repo (its `Dockerfile` + `README.md`
   must be at the Space root). E.g. from a fresh clone of the Space:
   ```bash
   # inside the Space repo
   cp -r /path/to/take-home-test/backend/. .
   git add -A && git commit -m "deploy backend" && git push
   ```
3. Set **Settings → Secrets** (do NOT commit `.env`):
   | Secret | Value |
   |---|---|
   | `DATABASE_URL` | the asyncpg string from step 1 |
   | `LLM_API_KEY` | Groq key |
   | `EMBEDDING_API_KEY` | Jina key |
   | `COHERE_API_KEY` | Cohere key (or set `RERANK_ENABLED=false`) |
   | `APP_ENV` | `prod` |
   | `API_KEY` | optional — a random string to protect upload/delete |
   | `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL` | optional |
   | `ALLOWED_ORIGINS` | set after step 3 (the Vercel URL) |
4. The Space builds the image and serves on port 8000. Test: `https://<user>-<space>.hf.space/health`.

> Notes: the free Space sleeps after inactivity (cold start on first request). Uploaded files
> live on ephemeral storage — they survive while the Space is warm; after a rebuild/restart,
> re-upload (DB rows remain, but the raw file for the source viewer is gone).

---

## 3. Vercel (frontend)

1. Import the repo at [vercel.com/new](https://vercel.com/new).
2. Set **Root Directory = `frontend`** (Vercel auto-detects Vite).
3. Add an environment variable:
   | Key | Value |
   |---|---|
   | `VITE_API_BASE` | your HF Space URL, e.g. `https://<user>-<space>.hf.space` |
   | `VITE_API_KEY` | only if you set `API_KEY` on the backend |
4. Deploy. You'll get a URL like `https://<app>.vercel.app`.

---

## 4. Wire CORS (connect the two)

Back on the **HF Space**, set the secret:
```
ALLOWED_ORIGINS=https://<app>.vercel.app
```
Restart the Space. Done — open the Vercel URL, upload a document, ask a question.

---

## Quick local alternative (no cloud)

```bash
docker compose up --build      # db + api + frontend, UI on localhost:5173
```
