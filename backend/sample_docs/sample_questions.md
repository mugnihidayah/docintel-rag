# Contoh Pertanyaan — Korpus Uji (Dokumen Publik Indonesia)

> Domain korpus: **dokumen publik Indonesia lintas-format**, undang-undang, Kerangka Acuan Kerja (KAK), paparan kebijakan Kementerian Keuangan, data administratif pemerintah, dan data wilayah.
> Semua dokumen di folder ini **asli dan diunduh dari sumber publik** (peraturan.bpk.go.id, djpk.kemenkeu.go.id, portal PPID/satu-data daerah, dan data wilayah administratif).
> Pertanyaan dirancang agar mencakup retrieval sederhana, parameter numerik, data spreadsheet, lintas-dokumen, dan kasus "tidak ditemukan".

---

## Korpus

| File | Format | Sumber | Isi singkat |
|---|---|---|---|
| `UU-14-2005-Guru-dan-Dosen.pdf` | PDF | peraturan.bpk.go.id | UU tentang Guru dan Dosen (50 hlm) |
| `UU-20-2023-ASN.pdf` | PDF | peraturan.bpk.go.id | UU tentang Aparatur Sipil Negara (44 hlm) |
| `KAK-Satu-Data-Rembang.docx` | DOCX | rembangkab.go.id | KAK Forum Satu Data Indonesia Kab. Rembang |
| `KAK-Penataan-Gedung-Magelang.docx` | DOCX | magelangkab.go.id | KAK Studi Penataan Bangunan Gedung Kantor |
| `Paparan-DJPK-DAK-Nonfisik-Pendidikan.pptx` | PPTX | djpk.kemenkeu.go.id | Kebijakan DAK Nonfisik Bidang Pendidikan |
| `Paparan-DJPK-Dampak-Covid-Ekonomi.pptx` | PPTX | djpk.kemenkeu.go.id | Kebijakan TKDD masa pandemi Covid-19 |
| `Data-PAUD-Jakarta-Timur.xlsx` | XLSX | timur.jakarta.go.id | Data PAUD per kelurahan (multi-sheet) |
| `SK-Lurah-Jakarta-Timur.xlsx` | XLSX | timur.jakarta.go.id | Rekap SK Lurah 2022–2023 |
| `wilayah-provinsi-indonesia.csv` | CSV | data wilayah administratif | Kode + nama 34 provinsi |
| `wilayah-kabupaten-kota-indonesia.csv` | CSV | data wilayah administratif | Kode + nama 514 kabupaten/kota |

---

## Daftar Pertanyaan

### 1. Apa definisi guru menurut UU Guru dan Dosen?
**Tipe:** Retrieval sederhana (PDF)
**Harus kembali ke:** UU-14-2005-Guru-dan-Dosen.pdf, Pasal 1 (Ketentuan Umum)
**Jawaban diharapkan:** "Pendidik profesional dengan tugas utama mendidik, mengajar, membimbing, mengarahkan, melatih, menilai, dan mengevaluasi peserta didik…"
**Sitasi diharapkan:** `UU-14-2005-Guru-dan-Dosen.pdf` halaman 2

### 2. Pegawai ASN terdiri dari apa saja?
**Tipe:** Retrieval sederhana (PDF)
**Harus kembali ke:** UU-20-2023-ASN.pdf, Pasal 1 (definisi Pegawai ASN)
**Jawaban diharapkan:** Pegawai Negeri Sipil (PNS) dan Pegawai Pemerintah dengan Perjanjian Kerja (PPPK)
**Sitasi diharapkan:** `UU-20-2023-ASN.pdf` halaman 2

### 3. Berapa jumlah peserta Forum Satu Data Indonesia Tingkat Kabupaten Rembang?
**Tipe:** Parameter numerik (DOCX)
**Harus kembali ke:** KAK-Satu-Data-Rembang.docx, bagian "Sasaran"
**Jawaban diharapkan:** 45 peserta (terdiri dari Perangkat Daerah dan Instansi Vertikal)
**Sitasi diharapkan:** `KAK-Satu-Data-Rembang.docx` section "Sasaran"

### 4. Undang-Undang apa yang menjadi dasar tentang bangunan gedung dalam KAK Penataan Gedung Magelang?
**Tipe:** Retrieval spesifik (DOCX)
**Harus kembali ke:** KAK-Penataan-Gedung-Magelang.docx, bagian "Latar Belakang"
**Jawaban diharapkan:** Undang-Undang Nomor 28 Tahun 2002 tentang Bangunan Gedung
**Sitasi diharapkan:** `KAK-Penataan-Gedung-Magelang.docx` section "Latar Belakang"

### 5. Berapa besaran Tunjangan Profesi Guru (TPG) PNSD menurut paparan DAK Nonfisik Bidang Pendidikan?
**Tipe:** Parameter numerik (PPTX)
**Harus kembali ke:** Paparan-DJPK-DAK-Nonfisik-Pendidikan.pptx, slide tentang TPG PNSD
**Jawaban diharapkan:** 1 (satu) kali gaji pokok PNS yang bersangkutan
**Sitasi diharapkan:** `Paparan-DJPK-DAK-Nonfisik-Pendidikan.pptx` slide 3

### 6. Peraturan Presiden mana yang dipakai untuk menyesuaikan alokasi TKDD tahun 2020?
**Tipe:** Retrieval spesifik (PPTX)
**Harus kembali ke:** Paparan-DJPK-Dampak-Covid-Ekonomi.pptx, slide penyesuaian alokasi TKDD
**Jawaban diharapkan:** Peraturan Presiden Nomor 54 Tahun 2020
**Sitasi diharapkan:** `Paparan-DJPK-Dampak-Covid-Ekonomi.pptx` slide 6

### 7. Apa nama PAUD nomor 1 di Kelurahan Makasar?
**Tipe:** Retrieval dari XLSX (data spreadsheet, multi-sheet)
**Harus kembali ke:** Data-PAUD-Jakarta-Timur.xlsx, sheet "Makasar"
**Jawaban diharapkan:** PAUD Kuntum Melati
**Sitasi diharapkan:** `Data-PAUD-Jakarta-Timur.xlsx` sheet "Makasar", rentang baris awal

### 8. Provinsi apa yang memiliki kode wilayah 14?
**Tipe:** Retrieval dari CSV (lookup tabel)
**Harus kembali ke:** wilayah-provinsi-indonesia.csv
**Jawaban diharapkan:** Riau
**Sitasi diharapkan:** `wilayah-provinsi-indonesia.csv` rentang baris yang memuat kode 14

### 9. Sebutkan Peraturan Presiden yang menjadi dasar penyelenggaraan Satu Data Indonesia dan Peraturan Presiden yang dipakai untuk penyesuaian alokasi TKDD tahun 2020.
**Tipe:** Lintas-dokumen (2 dokumen, format berbeda)
**Harus kembali ke:** KAK-Satu-Data-Rembang.docx (Dasar Hukum) **dan** Paparan-DJPK-Dampak-Covid-Ekonomi.pptx
**Jawaban diharapkan:** Perpres Nomor 39 Tahun 2019 (Satu Data Indonesia) dan Perpres Nomor 54 Tahun 2020 (penyesuaian TKDD)
**Sitasi diharapkan:** dua sitasi, `KAK-Satu-Data-Rembang.docx` + `Paparan-DJPK-Dampak-Covid-Ekonomi.pptx`

### 10. Apakah ada SOP penggunaan AI generatif (ChatGPT) di tempat kerja?
**Tipe:** Pertanyaan di luar korpus harus dijawab "tidak ditemukan"
**Harus kembali ke:** Tidak ada dokumen yang relevan
**Jawaban diharapkan:** "Tidak ditemukan dalam dokumen." (tanpa sitasi)

---

## Ringkasan Cakupan

| # | Tipe | Format Sumber | Catatan |
|---|---|---|---|
| 1 | Sederhana | PDF | Definisi/Pasal |
| 2 | Sederhana | PDF | Definisi (PNS + PPPK) |
| 3 | Numerik | DOCX | Angka peserta |
| 4 | Spesifik | DOCX | Rujukan UU |
| 5 | Numerik | PPTX | Besaran tunjangan |
| 6 | Spesifik | PPTX | Nomor Perpres |
| 7 | Spreadsheet | **XLSX** | Multi-sheet, lookup baris |
| 8 | Lookup | **CSV** | Kode → nama wilayah |
| 9 | Lintas-dokumen | **DOCX + PPTX** | Dua sumber, dua sitasi |
| 10 | Di luar korpus | — | Harus "tidak ditemukan" |

---

## Cara Pakai

Taruh dokumen sampel di `backend/sample_docs/`, lalu jalankan skrip seed untuk mengindeks semuanya sekaligus:

```bash
cd backend
uv run python -m scripts.seed_sample_docs
```

Lalu uji satu per satu via Swagger atau curl (field-nya `question`):

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Berapa jumlah peserta Forum Satu Data Indonesia Tingkat Kabupaten Rembang?"}'
```

Verifikasi:
- Jawaban **grounded** (bukan karangan model)
- **Sitasi** menunjuk ke file + halaman/slide/sheet/baris yang benar
- Pertanyaan #10 menjawab **"tidak ditemukan"**, bukan halusinasi
