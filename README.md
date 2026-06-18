# Inazuma Cube Device — Z3 + Three.js (Themed UI)

Versi UI bertema "Inazuma Cube Device" (night-scene, torii gate, ornamen
emas/ungu) — mekanisme puzzle dan solver **sama persis** dengan versi
sebelumnya, hanya tampilan frontend yang diubah.

## Struktur

```
inazuma_z3_v2/
├── solver.py            # Flask app + model Z3 (sama seperti versi sebelumnya)
├── sanity_check.py       # brute-force cross-check tanpa Z3
├── requirements.txt
├── Procfile
├── .gitignore
└── templates/
    └── index.html        # UI baru bertema Inazuma Cube Device
```

## Jalankan lokal

```bash
cd inazuma_z3_v2
pip install -r requirements.txt
python solver.py
```

Buka **http://localhost:5000/**.

## Yang berubah dari versi sebelumnya

- **Layout** disusun mengikuti referensi: panel judul + "Pola Pengaruh" di
  kiri, panel "Target" di kanan atas, viewport 3D kubus di tengah, lalu
  baris bawah: "Cara Kerja", "Klik Kubus untuk Memutar" (kartu per kubus
  dengan counter ×N), dan "Jumlah Langkah" + tombol Reset.
- **Tema visual**: latar malam ungu dengan siluet gerbang torii, lentera,
  dan bunga sakura yang melayang (CSS/SVG, tanpa aset berlisensi),
  font Cinzel untuk judul bergaya ornamen, panel dengan sudut emas.
- **Diagram "Pola Pengaruh"** digambar otomatis berdasarkan matriks adjacency
  `A` dari studi kasus yang sedang aktif (self-loop = lingkaran terisi,
  pengaruh ke kubus lain = anak panah).
- **Auto Solve (Z3)** dan **Reset** tetap memanggil endpoint Flask yang sama
  (`/api/cases`, `/api/solve/<idx>`).
- Counter "Jumlah Langkah" total dan counter ×N per kubus ditambahkan,
  mengikuti referensi desain.

## Deploy online

Sama seperti versi sebelumnya — lihat README versi pertama untuk langkah
lengkap deploy ke Render.com (Procfile sudah disiapkan: `gunicorn solver:app`).
