# Hoax Detection News App Indonesia

## DESKRIPSI
Aplikasi web untuk mendeteksi potensi hoaks pada berita online Indonesia. Sistem mengambil berita otomatis dari RSS, menyimpan arsip berita lama dan baru, lalu melakukan klasifikasi hoaks menggunakan model NLP dari Hugging Face.

## TUJUAN
- Menyediakan demo sistem deteksi hoaks end to end
- Mengarsipkan berita secara otomatis
- Menampilkan hasil analisis ke pengguna

## FITUR UTAMA
- Pengambilan berita otomatis dari RSS
- Penyimpanan berita ke Firestore
- Deteksi hoaks berbasis AI
- Confidence score hasil prediksi
- Tampilan web sederhana dengan React

## ARSITEKTUR
- **Frontend**: React + Vite
- **Backend**: FastAPI berbasis REST
- **AI Model**: IndoBERT dari Hugging Face
- **Database**: Cloud Firestore
- **Scheduler**: Cron atau GitHub Actions

## ALUR SISTEM
1. Scheduler mengambil RSS secara berkala
2. Backend memeriksa berita baru
3. Isi berita diambil dari URL
4. Teks diproses dan dianalisis model
5. Hasil disimpan ke Firestore
6. Frontend menampilkan data berita

## STRUKTUR DATA

### Collection: `news`
```
{
  id: string,
  title: string,
  link: string,
  content: string,
  source: string,
  published_time: datetime,
  hoax_label: string,  // "hoax" atau "non-hoax"
  confidence: float,    // 0.0 - 1.0
  created_at: datetime
}
```

## STRUKTUR PROYEK
```
HoaxDetection/
├── backend/
│   ├── app/
│   │   ├── models/         # Pydantic models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── utils/          # Helper functions
│   ├── requirements.txt
│   ├── scheduler.py        # Standalone scheduler
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API calls
│   │   └── styles/         # CSS files
│   ├── package.json
│   └── .env.example
├── docs/
│   └── CRON_SETUP.md      # Scheduler documentation
├── .github/
│   └── workflows/
│       └── fetch-news.yml  # GitHub Actions workflow
└── README.md
```

## CARA MENJALANKAN

### Prasyarat
- Python 3.10+
- Node.js 18+
- Firebase Project (dengan Firestore enabled)
- Git

### Setup Firebase
1. Buat project di [Firebase Console](https://console.firebase.google.com/)
2. Aktifkan Firestore Database
3. Generate service account key:
   - Project Settings > Service Accounts
   - Generate new private key
   - Simpan sebagai `backend/firebase-credentials.json`

### Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Setup environment variables:
```bash
cp .env.example .env
```

Edit `.env`:
```env
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
RSS_FEED_URL=https://www.antaranews.com/rss/terkini.xml
MODEL_NAME=indobenchmark/indobert-base-p1
```

3. Jalankan server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Setup environment variables:
```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

3. Jalankan development server:
```bash
npm run dev
```

Frontend akan berjalan di `http://localhost:3000`

### Setup Scheduler

#### Opsi 1: Manual Execution
```bash
cd backend
python scheduler.py
```

#### Opsi 2: Cron Job (Linux/Mac)
```bash
crontab -e
```

Tambahkan:
```bash
0 */6 * * * cd /path/to/HoaxDetection/backend && python3 scheduler.py >> /var/log/hoax-detection.log 2>&1
```

#### Opsi 3: GitHub Actions
1. Push repository ke GitHub
2. Tambahkan secrets di repository settings:
   - `FIREBASE_CREDENTIALS`: Isi file firebase-credentials.json
   - `RSS_FEED_URL`: URL RSS feed
   - `MODEL_NAME`: Nama model (optional)

Lihat [docs/CRON_SETUP.md](docs/CRON_SETUP.md) untuk detail lengkap.

## API ENDPOINTS

### GET `/`
Health check endpoint
```json
{
  "message": "Hoax Detection News App API",
  "status": "running",
  "version": "1.0.0"
}
```

### GET `/api/news/`
Mengambil semua berita
- Query params: `limit` (default: 50)
```json
{
  "total": 10,
  "news": [...]
}
```

### GET `/api/news/{id}`
Mengambil berita berdasarkan ID

### POST `/api/news/fetch-rss`
Mengambil berita baru dari RSS dan memproses dengan AI
```json
{
  "status": "success",
  "message": "Processed 5 articles, skipped 2 existing articles",
  "processed": 5,
  "skipped": 2,
  "total": 7
}
```

## CATATAN PENTING

### Model AI
Aplikasi ini menggunakan model IndoBERT base yang **belum di-fine-tune** untuk deteksi hoaks. Untuk produksi, Anda perlu:
1. Mengumpulkan dataset berita hoaks dan non-hoaks Indonesia
2. Fine-tune model IndoBERT dengan dataset tersebut
3. Replace model di `app/services/hoax_detector.py`

### RSS Feed
Default menggunakan Antara News RSS. Anda bisa mengganti dengan sumber lain di `.env`:
- Detik: `https://rss.detik.com/index.php/detikcom`
- Kompas: `https://rss.kompas.com/nasional`
- CNN Indonesia: `https://www.cnnindonesia.com/rss`

### Content Extraction
Web scraper mungkin perlu disesuaikan untuk setiap media berbeda. Edit `app/services/rss_fetcher.py` untuk kustomisasi.

## BATASAN SISTEM
- Fokus satu sumber RSS (dapat dikembangkan untuk multi-source)
- Klasifikasi hoaks biner (hoax/non-hoax)
- Tidak menggantikan pemeriksaan fakta manual
- Model belum di-fine-tune untuk deteksi hoaks
- Akurasi tergantung kualitas model dan data training

## PENGEMBANGAN LEBIH LANJUT

### Roadmap
- [ ] Multi-source RSS feeds
- [ ] Fine-tune model dengan dataset hoaks Indonesia
- [ ] User authentication dan personalisasi
- [ ] Fact-checking verification system
- [ ] Export data (CSV, JSON)
- [ ] Analytics dashboard
- [ ] Mobile app
- [ ] Real-time notifications

## LICENSE
Proyek ini dibuat untuk keperluan pembelajaran dan portofolio.

## CATATAN
Aplikasi ini ditujukan untuk pembelajaran dan portofolio. Hasil prediksi bersifat probabilistik dan tidak mewakili kebenaran absolut. Selalu verifikasi informasi dari sumber terpercaya.

## STATUS
✅ MVP siap demo
✅ Siap dikembangkan lebih lanjut
⚠️ Model perlu fine-tuning untuk akurasi optimal

## KONTAK
Dikembangkan sebagai proyek pembelajaran AI dan Web Development.

---

**Happy Coding!** 🚀
