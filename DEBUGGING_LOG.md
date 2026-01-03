# Debugging Log - Hoax Detection News App

Log dokumentasi masalah dan solusi yang ditemukan selama development.

---

## 2024-12-31 (Setup & Initial Development)

### 1. Git Line Ending Warning (CRLF vs LF)

**Tanggal**: 2024-12-31 21:10
**Masalah**:
```
Git: warning: in the working copy of '.github/CONTRIBUTING.md', LF will be replaced by CRLF the next time Git touches it
```

**Penyebab**:
- File dibuat di Unix-style environment (LF)
- Git di Windows expect CRLF
- Konflik line ending antara OS

**Solusi**:
1. Buat file `.gitattributes`:
   ```
   # Disable auto line ending conversion
   * -text
   ```
2. Set Git config:
   ```bash
   git config core.autocrlf false
   ```

**Status**: ✅ Resolved

---

### 2. Git Error: Unable to Index File 'nul'

**Tanggal**: 2024-12-31 21:10
**Masalah**:
```
error: short read while indexing nul
error: nul: failed to insert into database
error: unable to index file 'nul'
fatal: adding files failed
```

**Penyebab**:
- File `nul` ter-create di repository
- `nul` adalah reserved device name di Windows (seperti CON, PRN, AUX)
- Git tidak bisa index file dengan nama reserved

**Solusi**:
1. Tambahkan `nul` ke `.gitignore`:
   ```
   # Ignore nul file
   nul
   ```
2. Fresh start Git repository:
   ```bash
   Remove-Item -Recurse -Force .git
   git init
   git add .
   git commit -m "Initial commit"
   ```

**Status**: ✅ Resolved

---

### 3. PyTorch Version Incompatibility

**Tanggal**: 2024-12-31 ~21:30
**Masalah**:
```
ERROR: Could not find a version that satisfies the requirement torch==2.1.2
(from versions: 2.2.0, 2.2.1, 2.2.2, 2.3.0, 2.3.1, 2.4.0, 2.4.1, 2.5.0, 2.5.1, 2.6.0, 2.7.0, 2.7.1, 2.8.0, 2.9.0, 2.9.1)
ERROR: No matching distribution found for torch==2.1.2
```

**Penyebab**:
- PyTorch 2.1.2 tidak tersedia untuk Python 3.12
- `requirements.txt` menggunakan versi yang terlalu lama

**Solusi**:
Update `backend/requirements.txt`:
```diff
- torch==2.1.2
+ torch>=2.2.0
```

**Status**: ✅ Resolved

---

### 4. RSS Feed URL Not Configured

**Tanggal**: 2024-12-31 ~21:45
**Masalah**:
```
No RSS feed URL configured
INFO:     127.0.0.1:64271 - "POST /api/news/fetch-rss HTTP/1.1" 200 OK
```

Frontend menampilkan: "No articles fetched"

**Penyebab**:
- File `.env` belum dibuat atau belum dibaca
- Global instance `rss_fetcher` di-inisialisasi sebelum `.env` di-load
- Environment variable tidak terbaca saat runtime

**Diagnosis**:
- Backend server sudah running
- Frontend sudah running
- Firebase initialized successfully
- Tapi RSS_FEED_URL tidak terbaca

**Solusi**:
1. Pastikan file `backend/.env` ada dan berisi:
   ```env
   FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
   RSS_FEED_URL=https://www.antaranews.com/rss/terkini.xml
   MODEL_NAME=indobenchmark/indobert-base-p1
   ```

2. Update `backend/app/services/rss_fetcher.py` untuk re-read environment variable:
   ```python
   def fetch_rss(self) -> List[Dict]:
       # Re-read from environment in case it changed
       if not self.rss_url:
           self.rss_url = os.getenv("RSS_FEED_URL", "")

       if not self.rss_url:
           print("No RSS feed URL configured")
           print(f"Environment variables: {os.environ.get('RSS_FEED_URL', 'NOT SET')}")
           return []
   ```

3. Restart backend server (Ctrl+C, lalu `uvicorn app.main:app --reload`)

**Status**: ✅ Resolved

---

## Common Issues & Solutions

### Issue: Backend tidak bisa start

**Solusi**:
1. Check virtual environment aktif:
   ```bash
   venv\Scripts\activate
   ```
2. Check dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Check Firebase credentials file exists:
   ```bash
   ls firebase-credentials.json
   ```

---

### Issue: Frontend tidak bisa connect ke backend

**Solusi**:
1. Check backend running di `http://localhost:8000`
2. Check `frontend/.env`:
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```
3. Check CORS settings di `backend/app/main.py`

---

### Issue: CORS Error

**Solusi**:
Update `backend/app/main.py`:
```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

---

### Issue: Firebase Permission Denied

**Solusi**:
1. Check Firestore Security Rules:
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
2. Check service account key valid

---

### Issue: Model Download Error

**Solusi**:
1. Pastikan koneksi internet stabil
2. Model akan auto-download saat first run (~500MB)
3. Check disk space (butuh minimal 2GB)
4. Lokasi cache: `~/.cache/huggingface/`

---

## Development Timeline

| Date | Milestone | Status |
|------|-----------|--------|
| 2024-12-31 | Project structure created | ✅ |
| 2024-12-31 | Backend FastAPI setup | ✅ |
| 2024-12-31 | Frontend React setup | ✅ |
| 2024-12-31 | Firebase integration | ✅ |
| 2024-12-31 | RSS fetcher implemented | ✅ |
| 2024-12-31 | Hoax detector (base model) | ✅ |
| 2024-12-31 | Git repository setup | ✅ |
| 2024-12-31 | First successful run | ✅ |
| TBD | Model fine-tuning | ⏳ |
| TBD | Production deployment | ⏳ |

---

## Environment Setup Checklist

- [x] Python 3.10+ installed
- [x] Node.js 18+ installed
- [x] Firebase project created
- [x] Firestore enabled
- [x] Service account key downloaded
- [x] Backend `.env` configured
- [x] Frontend `.env` configured
- [x] Backend dependencies installed
- [x] Frontend dependencies installed
- [x] Backend running successfully
- [x] Frontend running successfully
- [x] End-to-end test passed
- [x] RSS fetch working
- [ ] Model fine-tuning (optional)
- [ ] Production deployment (future)

---

## Known Limitations

1. **Model Accuracy**: Using base IndoBERT model without fine-tuning. Needs dataset hoaks Indonesia for better accuracy.

2. **RSS Source**: Currently only supports single RSS feed. Can be extended to multiple sources.

3. **Content Extraction**: Generic web scraper, may need customization for specific news sites.

4. **Performance**: Model inference takes 1-3 seconds per article. Can be optimized with:
   - Model quantization
   - GPU acceleration
   - Caching mechanism

5. **Error Handling**: Basic error handling. Needs improvement for production.

---

## Next Steps

### Immediate (MVP Complete)
- [x] Setup Firebase
- [x] Test RSS fetching
- [x] Verify data saved to Firestore
- [x] Test end-to-end flow

### Short-term
- [ ] Collect hoax dataset Indonesia
- [ ] Fine-tune IndoBERT model
- [ ] Add more RSS sources
- [ ] Improve content extraction
- [ ] Add unit tests

### Long-term
- [ ] User authentication
- [ ] Search & filter functionality
- [ ] Analytics dashboard
- [ ] Mobile app
- [ ] Production deployment

---

## Contact & Support

- **GitHub Issues**: [Repository Issues](https://github.com/your-username/HoaxDetection/issues)
- **Documentation**: See README.md and docs/

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0 (MVP)
**Status**: Development - First Successful Run ✅
