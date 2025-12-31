# Quick Start Guide

Panduan cepat untuk menjalankan aplikasi dalam 5 menit.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Firebase Project (dengan Firestore enabled)
- Firebase Service Account Key

## Setup Cepat

### 1. Backend

```bash
# Masuk ke folder backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env - minimal yang harus diisi:
# FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
# RSS_FEED_URL=https://www.antaranews.com/rss/terkini.xml

# Copy file firebase-credentials.json ke folder backend/
# (download dari Firebase Console)

# Jalankan server
uvicorn app.main:app --reload
```

Backend akan berjalan di: `http://localhost:8000`

### 2. Frontend

Buka terminal baru:

```bash
# Masuk ke folder frontend
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Jalankan dev server
npm run dev
```

Frontend akan berjalan di: `http://localhost:3000`

## Test Aplikasi

1. Buka browser: `http://localhost:3000`
2. Klik tombol **"Ambil Berita Baru dari RSS"**
3. Tunggu proses selesai (1-5 menit)
4. Lihat berita muncul dengan label hoax/non-hoax

## Troubleshooting

### Firebase Error
- Pastikan file `firebase-credentials.json` ada di `backend/`
- Pastikan Firestore sudah enabled di Firebase Console

### Module Not Found
```bash
cd backend
pip install -r requirements.txt
```

### CORS Error
- Pastikan backend berjalan di port 8000
- Pastikan frontend `.env` sudah benar

## Dokumentasi Lengkap

- [Setup Guide](docs/SETUP_GUIDE.md) - Panduan setup detail
- [API Documentation](docs/API_DOCUMENTATION.md) - Dokumentasi API
- [Cron Setup](docs/CRON_SETUP.md) - Setup scheduler otomatis

## Struktur Project

```
HoaxDetection/
├── backend/           # FastAPI Backend
│   ├── app/          # Source code
│   ├── requirements.txt
│   └── .env
├── frontend/         # React Frontend
│   ├── src/         # Source code
│   ├── package.json
│   └── .env
└── docs/            # Documentation
```

## Next Steps

1. Fine-tune model dengan dataset hoaks Indonesia
2. Tambahkan lebih banyak sumber RSS
3. Setup scheduler untuk automation
4. Deploy ke production

---

**Selamat mencoba! 🚀**

Jika ada masalah, lihat [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) atau [README.md](README.md)
