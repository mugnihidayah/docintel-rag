# TECHNICAL.md — Document Intelligence System (RAG)

Keputusan teknis & arsitektur beserta alasannya — dokumen mandiri.

## 1. Arsitektur
_(diagram + ringkasan arsitektur — TODO)_

## 2. Parsing & Ekstraksi Multi-format
Deteksi format gabungan **ekstensi + magic bytes** (menolak file yang ekstensinya menipu), lalu di-route ke extractor per-format lewat **registry**. Tiap extractor menghasilkan model ternormalisasi yang sama (`ExtractedDocument` → `Element{text, type, location}`), jadi downstream tak peduli format asal.

| Format | Library | Lokasi sitasi |
|---|---|---|
| PDF | PyMuPDF | halaman |
| DOCX | python-docx | section/heading + block_index (jangkar deterministik) |
| PPTX | python-pptx | nomor slide (+ recurse grouped shapes, speaker notes) |
| XLSX | openpyxl/pandas | sheet + rentang baris _(Fase 1.6)_ |
| CSV/TXT | pandas/plain | rentang baris _(Fase 1.7)_ |

**Konten gambar (vision LLM).** Gambar tertanam (PDF/DOCX/PPTX) dan **PDF hasil scan** (halaman tanpa teks → di-render jadi gambar) dikirim ke **vision LLM** (Llama 4 Scout via Groq) saat ingestion → teks/deskripsi jadi `Element` tipe `image` dengan lokasi sumbernya. Dipilih hosted vision LLM (bukan OCR lokal) agar sejalan prinsip no-local-compute & lebih kaya (paham diagram). Pengaman: skip gambar kecil, batas jumlah per dokumen, timeout + **fallback** (gagal → skip, ekstraksi tetap jalan). Batasan: gambar di sel tabel/header-footer & dokumen scan sangat panjang (dibatasi budget) = future work.

**Ketahanan.** Deteksi format menolak ekstensi yang menipu (magic bytes) & file kosong dengan pesan jelas; file korup → `ExtractionError` (status `failed`, batch lain tetap jalan); teks di-decode **UTF-8** dengan fallback (teks Indonesia utuh, tak pernah crash karena byte aneh).

## 3. Chunking
_(structure-aware chunking — TODO Fase 2)_

## 4. Embedding & LLM
- **Embedding:** Jina v5 (`jina-embeddings-v5-text-small`, hosted, multilingual 90+ bahasa, 1024-dim), pluggable. Task `retrieval.passage`.
- **LLM:** Groq `llama-3.3-70b` (OpenAI-compatible), pluggable.
- Alasan & trade-off: _(TODO)_

## 5. Retrieval & Reranking
**Hybrid search** native pgvector: jalur **vektor** (HNSW, cosine) untuk kemiripan makna + jalur **full-text** (`simple` config) untuk kecocokan kata/istilah eksak — digabung jadi kandidat top-k. Vektor unggul untuk parafrase, full-text unggul untuk kode/istilah persis; gabungan menutup kelemahan masing-masing.

Kandidat lalu di-**rerank** oleh **Cohere rerank-multilingual** (cross-encoder, baca pertanyaan+chunk bersama) → top-n paling relevan. **Default ON**, dengan **graceful fallback**: bila reranker gagal (rate limit/timeout/provider down), query tetap jalan memakai urutan retriever (di-log, tanpa menjatuhkan permintaan). Semua parameter (`retrieve_top_k`, `rerank_top_n`, model) lewat env.

## 6. Grounding & Sitasi
**Grounding.** Prompt menyuruh LLM menjawab **hanya** dari konteks yang diberikan; jika tak ada, balas `"Tidak ditemukan dalam dokumen."` (refusal eksplisit). Konteks ditandai sebagai **data, bukan instruksi** (mitigasi prompt injection dari isi dokumen). LLM dijalankan `temperature=0` agar deterministik.

**Sitasi.** Dirakit langsung dari **metadata tiap node** hasil retrieval (`document_id`, `filename`, lokasi: halaman/slide/sheet/section/baris) — bukan diminta ke LLM, jadi tak bisa dikarang. Tiap sitasi membawa `snippet` (cuplikan sumber), `score`, dan `score_type` (`hybrid` bila reranker dilewati via fallback, `rerank` bila aktif). Orchestrator query (`rag/query.py`) merangkai: retrieve → rerank (fallback) → jawab grounded → kumpulkan sitasi → `QueryResult{answer, citations, retrieved_chunks, model, latency_ms}`.

## 7. Model Data
- **`documents`** (relasional, via Alembic async): lifecycle per file — `id`, `filename`, `mime_type`, `file_hash` (unik → dedup), `size_bytes`, `status` (`pending`→`indexing`→`indexed`/`failed`), `num_chunks`, `storage_path`, `error`, `created_at`/`updated_at`.
- **`data_docintel`** (dikelola PGVectorStore): node + `embedding` `vector(1024)` (HNSW cosine) + `metadata_` (json: `document_id` + lokasi) + `text_search_tsv` (FTS `simple`). Jembatan ke `documents` lewat `metadata_->>'document_id'`. Alembic `include_object` sengaja meng-exclude tabel ini agar autogenerate tak mengutak-atiknya.
- **Future:** `conversations` + `messages` (riwayat chat + snapshot sitasi) saat UI chat dibangun.

## 8. Evaluasi
Retrieval: hit-rate@k + MRR (deterministik). Generation: RAGAS (judge gpt-oss-120b). Offline. _(TODO Fase 3)_

## 9. Observability
Langfuse tracing (opsional). _(TODO Fase 6)_

## 10. Security & Auth
- **API key** (`X-API-Key`) di endpoint mutasi (`POST /documents`, `DELETE`): mati di dev (`API_KEY` kosong), aktif otomatis saat di-set (deploy). Query (baca) tetap terbuka.
- **Rate limit** per-IP (sliding window 60 dtk, `RATE_LIMIT_PER_MIN`; `0` = mati). In-memory/1-instance; multi-instance → Redis (future).
- **CORS** dari `ALLOWED_ORIGINS`. **Upload**: guard ukuran (`MAX_UPLOAD_MB`) + nama file ter-sanitasi (anti path-traversal) + deteksi format magic-bytes (tolak ekstensi menipu).
- **Error terpusat**: `AppError` → JSON `{error:{code,detail}}` + status tepat; 500 generik menyembunyikan detail internal. Tiap request punya `X-Request-ID` untuk korelasi log.
- Auth + rate limit diimplementasi sebagai **dependency** (bukan middleware) agar error-nya lewat exception handler terpusat → 401/429 JSON konsisten, bukan 500 mentah.

## 11. Rencana Deployment
Backend → HF Spaces (Docker) · DB → Supabase · FE → Vercel. _(TODO Fase 8)_

## 12. Trade-off & Future Work
- **Node-level idempotency.** Dedup level-file sudah ada di API (`file_hash`), jadi upload file identik tak menambah node. Tapi `index_document` sendiri *append-only* (tiap pemanggilan langsung memakai `document_id` baru). Future: upsert / hapus-by-`document_id` sebelum re-index, agar re-index lewat jalur non-API juga aman.
- **Granularitas chunk vs recall daftar.** Chunk 1-elemen sangat presisi untuk sitasi (lokasi tepat), tapi memecah satu "daftar logis" (mis. PDF/DOCX/PPTX masing-masing jadi node terpisah) → pertanyaan "sebutkan semua X" butuh `RERANK_TOP_N` lebih besar agar semua sibling ikut. Future: gabung heading+anak yang berurutan jadi chunk komposit, atau *small-to-big retrieval*.
- **Lainnya:** versioning dokumen, cache embedding per-chunk, gambar di sel tabel/header-footer, query-vs-passage task terpisah untuk embedding.
