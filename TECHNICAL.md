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
_(tabel trade-off + future work: versioning, cache embedding per-chunk, gambar di sel tabel — TODO)_
