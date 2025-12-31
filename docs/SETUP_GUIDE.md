# Setup Guide - Hoax Detection News App

## Panduan Lengkap Setup dari Awal

### 1. Persiapan Awal

#### 1.1 Install Tools
- **Python 3.10+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **Git**: [Download](https://git-scm.com/)

#### 1.2 Clone Repository
```bash
git clone <repository-url>
cd HoaxDetection
```

### 2. Setup Firebase

#### 2.1 Buat Firebase Project
1. Buka [Firebase Console](https://console.firebase.google.com/)
2. Klik "Add project" atau "Tambahkan project"
3. Beri nama project: `hoax-detection-app` (atau nama lain)
4. Nonaktifkan Google Analytics (optional)
5. Klik "Create project"

#### 2.2 Aktifkan Firestore
1. Di Firebase Console, buka menu "Firestore Database"
2. Klik "Create database"
3. Pilih mode: **Production mode**
4. Pilih location: asia-southeast2 (Jakarta) atau asia-southeast1 (Singapore)
5. Klik "Enable"

#### 2.3 Setup Security Rules
Di Firestore > Rules, gunakan rules berikut:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /news/{document=**} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

#### 2.4 Generate Service Account Key
1. Buka Project Settings (icon gear) > Service Accounts
2. Klik "Generate new private key"
3. Simpan file JSON yang didownload
4. Rename file menjadi `firebase-credentials.json`
5. Copy ke folder `backend/`

⚠️ **PENTING**: Jangan commit file ini ke Git!

### 3. Setup Backend

#### 3.1 Masuk ke folder backend
```bash
cd backend
```

#### 3.2 Buat Virtual Environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3.3 Install Dependencies
```bash
pip install -r requirements.txt
```

Proses ini akan menginstall:
- FastAPI
- Uvicorn
- Firebase Admin SDK
- Transformers (Hugging Face)
- PyTorch
- Dan dependencies lainnya

⏱️ **Catatan**: Proses ini memerlukan waktu 5-10 menit dan ~2GB download

#### 3.4 Setup Environment Variables
```bash
cp .env.example .env
```

Edit file `.env`:
```env
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
RSS_FEED_URL=https://www.antaranews.com/rss/terkini.xml
MODEL_NAME=indobenchmark/indobert-base-p1
```

#### 3.5 Test Backend
```bash
uvicorn app.main:app --reload
```

Buka browser: `http://localhost:8000`

Jika berhasil, akan muncul:
```json
{
  "message": "Hoax Detection News App API",
  "status": "running",
  "version": "1.0.0"
}
```

### 4. Setup Frontend

#### 4.1 Masuk ke folder frontend
Buka terminal baru:
```bash
cd frontend
```

#### 4.2 Install Dependencies
```bash
npm install
```

⏱️ **Catatan**: Proses ini memerlukan waktu 2-5 menit

#### 4.3 Setup Environment Variables
```bash
cp .env.example .env
```

Edit file `.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

#### 4.4 Test Frontend
```bash
npm run dev
```

Buka browser: `http://localhost:3000`

### 5. Testing End-to-End

#### 5.1 Jalankan Backend dan Frontend
Buka 2 terminal:

**Terminal 1 - Backend:**
```bash
cd backend
# Windows
run.bat

# Linux/Mac
chmod +x run.sh
./run.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
# Windows
run.bat

# Linux/Mac
chmod +x run.sh
./run.sh
```

#### 5.2 Test Fetch RSS
1. Buka `http://localhost:3000`
2. Klik tombol "Ambil Berita Baru dari RSS"
3. Tunggu proses (bisa memakan waktu beberapa menit)
4. Berita akan muncul di halaman

#### 5.3 Verifikasi di Firebase
1. Buka Firebase Console
2. Masuk ke Firestore Database
3. Cek collection `news` - seharusnya ada data berita baru

### 6. Setup Scheduler (Optional)

#### Opsi A: Manual Run
```bash
cd backend
python scheduler.py
```

#### Opsi B: Cron Job (Linux/Mac)
```bash
crontab -e
```

Tambahkan:
```bash
0 */6 * * * cd /path/to/HoaxDetection/backend && python3 scheduler.py >> /var/log/hoax-detection.log 2>&1
```

#### Opsi C: Windows Task Scheduler
Lihat [CRON_SETUP.md](CRON_SETUP.md) untuk detail

#### Opsi D: GitHub Actions
1. Push code ke GitHub
2. Setup secrets di repository
3. GitHub Actions akan jalan otomatis

### 7. Troubleshooting

#### Error: Firebase credentials not found
```bash
# Pastikan file ada di lokasi yang benar
ls backend/firebase-credentials.json

# Periksa .env
cat backend/.env
```

#### Error: Module not found
```bash
# Re-install dependencies
cd backend
pip install -r requirements.txt
```

#### Error: CORS
Pastikan frontend URL sudah terdaftar di `backend/app/main.py`:
```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

#### Frontend tidak bisa fetch data
```bash
# Periksa backend berjalan
curl http://localhost:8000

# Periksa .env frontend
cat frontend/.env
```

#### Model download error
- Pastikan koneksi internet stabil
- Model akan auto-download saat pertama kali digunakan
- Ukuran: ~500MB
- Lokasi cache: `~/.cache/huggingface/`

### 8. Development Workflow

#### Setiap kali mulai development:
```bash
# Terminal 1
cd backend
# Windows: run.bat | Linux/Mac: ./run.sh

# Terminal 2
cd frontend
# Windows: run.bat | Linux/Mac: ./run.sh
```

#### Update dependencies:
```bash
# Backend
cd backend
pip install <package-name>
pip freeze > requirements.txt

# Frontend
cd frontend
npm install <package-name>
```

### 9. Production Deployment

#### Backend (FastAPI)
Bisa di-deploy ke:
- **Google Cloud Run**
- **Heroku**
- **Railway**
- **DigitalOcean App Platform**

#### Frontend (React)
Bisa di-deploy ke:
- **Vercel** (Recommended)
- **Netlify**
- **Firebase Hosting**
- **GitHub Pages**

#### Catatan Deploy:
- Ubah `VITE_API_URL` ke URL production backend
- Setup environment variables di platform hosting
- Untuk backend, gunakan `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 10. Next Steps

Setelah setup berhasil:
1. Fine-tune model dengan dataset hoaks Indonesia
2. Tambahkan lebih banyak sumber RSS
3. Improve content extraction untuk berbagai media
4. Tambahkan fitur analytics
5. Deploy ke production

---

## Checklist Setup

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Firebase project created
- [ ] Firestore enabled
- [ ] Service account key downloaded
- [ ] Backend dependencies installed
- [ ] Backend .env configured
- [ ] Backend running successfully
- [ ] Frontend dependencies installed
- [ ] Frontend .env configured
- [ ] Frontend running successfully
- [ ] End-to-end test passed
- [ ] Data muncul di Firestore
- [ ] Scheduler tested (optional)

---

**Selamat! Aplikasi Anda sudah siap digunakan! 🎉**
