# Inazuma Cube 3D — Z3 + Three.js

Visualizer 3D puzzle constraint-satisfaction (mod-4 toggle puzzle).
Solver pakai **Z3 Theorem Prover** (Python) lewat backend Flask,
frontend pakai **Three.js** untuk render kubus 3D interaktif.

## Struktur

```
FP_PVS/
├── solver.py            # Flask app + model Z3 (Optimize, minimize total clicks)
├── sanity_check.py       # brute-force cross-check (tanpa Z3) untuk verifikasi model
├── requirements.txt
├── Procfile               # untuk deploy (Render/Railway): gunicorn solver:app
├── .gitignore
└── templates/
    └── index.html        # Three.js frontend, fetch ke /api/cases dan /api/solve
```

---

## 1. Jalankan LOKAL (untuk presentasi offline / laptop sendiri)

```bash
cd FP_PVS
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python solver.py
```

Buka **http://localhost:5000/** di browser. Tinggal share-screen / projector
saat presentasi — tidak perlu koneksi internet (kecuali untuk load
Three.js dan font dari CDN, sekali saat halaman pertama dibuka).

Saat start, `solver.py` juga menjalankan self-test Z3 dan mencetak hasil
5 studi kasus di terminal — bagus untuk ditunjukkan sebagai bukti solver
bekerja.

---

## 2. Deploy ONLINE (supaya bisa diakses via link, misal untuk dosen/demo)

Karena ini Flask + Z3 (server Python, bukan static site), pilihan termudah
adalah **Render.com** (free tier tersedia). Langkah-langkah:

### a. Siapkan repo GitHub

```bash
cd FP_PVS
git init
git add .
git commit -m "Inazuma Cube 3D - Z3 solver"
```

Buat repo baru di GitHub, lalu push:

```bash
git remote add origin https://github.com/<username>/<repo>.git
git branch -M main
git push -u origin main
```

> Pastikan folder `venv/` TIDAK ikut ter-push (sudah dicover oleh `.gitignore`).

### b. Deploy di Render

1. Buka render.com → Sign up / login (bisa pakai akun GitHub)
2. Klik **New +** → **Web Service**
3. Connect ke repo GitHub yang baru dibuat
4. Isi konfigurasi:
   - **Name**: bebas, misal `inazuma-cube-z3`
   - **Region**: pilih yang terdekat (Singapore jika ada)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn solver:app` (otomatis terbaca dari `Procfile`)
   - **Instance Type**: Free
5. Klik **Create Web Service**

Render akan build dan deploy otomatis (~2-5 menit). Setelah selesai, akan
muncul URL publik seperti:

```
https://inazuma-cube-z3.onrender.com
```

URL inilah yang bisa dibagikan/dibuka saat presentasi dari device lain.

> **Catatan free tier Render**: service akan "sleep" jika tidak ada traffic
> beberapa menit, dan butuh ~30-60 detik untuk "bangun" lagi saat diakses
> pertama kali. Untuk presentasi, buka link tersebut **beberapa menit
> sebelum mulai** supaya sudah aktif.

### Alternatif lain

- **Railway.app** — alur serupa, connect GitHub repo, auto-detect `Procfile`
- **PythonAnywhere** — khusus Flask, tapi setup WSGI sedikit lebih manual

---

## Model matematis (untuk slide/penjelasan)

Setiap kubus `k` punya state `s[k] ∈ {0,1,2,3}`. Klik kubus `j` menambah
`+1 (mod 4)` ke state setiap kubus `k` dengan `A[k][j] = 1`.

Z3 mencari `x[j] ≥ 0` (jumlah klik per kubus, dibatasi 0..3) sedemikian:

```
(s[k] + Σ_j A[k][j] · x[j]) mod 4 = t[k]   untuk semua k
```

dengan **minimize Σ x[j]** (total klik seminimal mungkin). Jika tidak ada
solusi → puzzle **UNSAT**.

## API

- `GET /api/cases` — daftar 5 studi kasus (s, t, A)
- `GET /api/solve/<idx>` — solve studi kasus ke-`idx` dengan Z3
  → `{"sat": true, "solution": [...], "total_clicks": N}` atau `{"sat": false}`
- `POST /api/solve_custom` — body JSON `{"s":[...], "t":[...], "A":[[...]]}`
  untuk puzzle custom

## Kontrol UI

- **Klik kubus** → toggle state (mod 4) sesuai matriks adjacency
- **Drag** → putar kamera, **Scroll** → zoom
- **Auto solve (Z3)** → minta Z3 cari solusi minimal, lalu animasikan klik-klik
- **Reset** → kembali ke state awal studi kasus
