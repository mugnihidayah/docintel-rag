# TECHNICAL.md — Document Intelligence System (RAG)

Keputusan teknis & arsitektur beserta alasannya — dokumen mandiri.

## 1. Arsitektur
_(diagram + ringkasan arsitektur — TODO)_

## 2. Parsing & Ekstraksi Multi-format
_(strategi per-format + metadata lokasi — TODO Fase 1)_

## 3. Chunking
_(structure-aware chunking — TODO Fase 2)_

## 4. Embedding & LLM
- **Embedding:** Jina v3 (hosted, multilingual, 1024-dim), pluggable.
- **LLM:** Groq `llama-3.3-70b` (OpenAI-compatible), pluggable.
- Alasan & trade-off: _(TODO)_

## 5. Retrieval & Reranking
Hybrid native pgvector (default) + Cohere rerank (default-on + fallback). _(TODO)_

## 6. Grounding & Sitasi
_(prompt grounding + sitasi dari source_nodes — TODO Fase 3)_

## 7. Model Data
4 tabel: `documents`, node (PGVectorStore), `conversations`, `messages`. _(TODO)_

## 8. Evaluasi
Retrieval: hit-rate@k + MRR (deterministik). Generation: RAGAS (judge gpt-oss-120b). Offline. _(TODO Fase 3)_

## 9. Observability
Langfuse tracing (opsional). _(TODO Fase 6)_

## 10. Security & Auth
API key di endpoint mutasi (default-on saat deploy) · CORS · rate limit · guard zip-bomb. _(TODO)_

## 11. Rencana Deployment
Backend → HF Spaces (Docker) · DB → Supabase · FE → Vercel. _(TODO Fase 8)_

## 12. Trade-off & Future Work
_(tabel trade-off + future work: versioning, OCR, cache embedding — TODO)_
