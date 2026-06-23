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
- **Embedding:** Jina v3 (hosted, multilingual, 1024-dim), pluggable.
- **LLM:** Groq `llama-3.3-70b` (OpenAI-compatible), pluggable.
- Alasan & trade-off: _(TODO)_

## 5. Retrieval & Reranking
**Hybrid search** native pgvector: jalur **vektor** (HNSW, cosine) untuk kemiripan makna + jalur **full-text** (`simple` config) untuk kecocokan kata/istilah eksak — digabung jadi kandidat top-k. Vektor unggul untuk parafrase, full-text unggul untuk kode/istilah persis; gabungan menutup kelemahan masing-masing.

Kandidat lalu di-**rerank** oleh **Cohere rerank-multilingual** (cross-encoder, baca pertanyaan+chunk bersama) → top-n paling relevan. **Default ON**, dengan **graceful fallback**: bila reranker gagal (rate limit/timeout/provider down), query tetap jalan memakai urutan retriever (di-log, tanpa menjatuhkan permintaan). Semua parameter (`retrieve_top_k`, `rerank_top_n`, model) lewat env.

## 6. Grounding & Sitasi
**Grounding.** Prompt menyuruh LLM menjawab **hanya** dari konteks yang diberikan; jika tak ada, balas `"Tidak ditemukan dalam dokumen."` (refusal eksplisit). Konteks ditandai sebagai **data, bukan instruksi** (mitigasi prompt injection dari isi dokumen). LLM dijalankan `temperature=0` agar deterministik.

**Sitasi.** Dirakit langsung dari **metadata tiap node** hasil retrieval (`document_id`, `filename`, lokasi: halaman/slide/sheet/section/baris) — bukan diminta ke LLM, jadi tak bisa dikarang. Tiap sitasi membawa `snippet` (cuplikan sumber), `score`, dan `score_type` (`hybrid` bila reranker dilewati via fallback, `rerank` bila aktif). Orchestrator query (`rag/query.py`) merangkai: retrieve → rerank (fallback) → jawab grounded → kumpulkan sitasi → `QueryResult{answer, citations, retrieved_chunks, model, latency_ms}`.

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
_(tabel trade-off + future work: versioning, cache embedding per-chunk, gambar di sel tabel — TODO)_
