# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check

#### GET `/`
Health check endpoint untuk memverifikasi server berjalan.

**Response:**
```json
{
  "message": "Hoax Detection News App API",
  "status": "running",
  "version": "1.0.0"
}
```

#### GET `/health`
Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### News Endpoints

#### GET `/api/news/`
Mengambil daftar semua berita dengan pagination.

**Query Parameters:**
- `limit` (optional, default: 50): Jumlah maksimal berita yang dikembalikan

**Request:**
```bash
curl http://localhost:8000/api/news/?limit=10
```

**Response:**
```json
{
  "total": 10,
  "news": [
    {
      "id": "abc123def456",
      "title": "Judul Berita",
      "link": "https://example.com/news/article",
      "content": "Isi konten berita lengkap...",
      "source": "RSS Feed",
      "published_time": "2024-01-15T10:30:00",
      "hoax_label": "non-hoax",
      "confidence": 0.8523,
      "created_at": "2024-01-15T10:35:00"
    },
    ...
  ]
}
```

**Response Fields:**
- `total`: Jumlah berita yang dikembalikan
- `news`: Array berisi data berita
  - `id`: Unique identifier (MD5 hash dari link)
  - `title`: Judul berita
  - `link`: URL berita asli
  - `content`: Konten berita yang di-extract
  - `source`: Sumber berita
  - `published_time`: Waktu publikasi (ISO 8601)
  - `hoax_label`: Label prediksi ("hoax" atau "non-hoax")
  - `confidence`: Tingkat keyakinan prediksi (0.0 - 1.0)
  - `created_at`: Waktu data disimpan (ISO 8601)

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Server error

---

#### GET `/api/news/{news_id}`
Mengambil detail berita berdasarkan ID.

**Path Parameters:**
- `news_id`: ID berita (MD5 hash dari link)

**Request:**
```bash
curl http://localhost:8000/api/news/abc123def456
```

**Response:**
```json
{
  "id": "abc123def456",
  "title": "Judul Berita",
  "link": "https://example.com/news/article",
  "content": "Isi konten berita lengkap...",
  "source": "RSS Feed",
  "published_time": "2024-01-15T10:30:00",
  "hoax_label": "non-hoax",
  "confidence": 0.8523,
  "created_at": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Berita tidak ditemukan
- `500 Internal Server Error`: Server error

---

#### POST `/api/news/fetch-rss`
Mengambil berita baru dari RSS feed, melakukan ekstraksi konten, deteksi hoaks, dan menyimpan ke database.

**Request:**
```bash
curl -X POST http://localhost:8000/api/news/fetch-rss
```

**Response:**
```json
{
  "status": "success",
  "message": "Processed 5 articles, skipped 2 existing articles",
  "processed": 5,
  "skipped": 2,
  "total": 7
}
```

**Response Fields:**
- `status`: Status operasi ("success" atau "error")
- `message`: Pesan deskriptif
- `processed`: Jumlah artikel baru yang diproses
- `skipped`: Jumlah artikel yang sudah ada (dilewati)
- `total`: Total artikel yang ditemukan di RSS

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Server error

**Notes:**
- Proses ini bisa memakan waktu beberapa menit tergantung jumlah artikel
- Artikel yang sudah ada tidak akan diproses ulang
- Setiap artikel akan melalui tahapan:
  1. Check duplicate
  2. Extract content dari URL
  3. Hoax detection dengan AI model
  4. Save ke Firestore

---

## Error Responses

Semua endpoint akan mengembalikan error dalam format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error (Firebase, Model, etc.)

---

## Models

### NewsItem (Input Model)
```python
{
  "title": str,           # Required
  "link": str,            # Required
  "content": str,         # Required
  "source": str,          # Required
  "published_time": datetime | None,
  "hoax_label": str | None,
  "confidence": float | None,
  "created_at": datetime
}
```

### NewsResponse (Output Model)
```python
{
  "id": str,              # Generated MD5 hash
  "title": str,
  "link": str,
  "content": str,
  "source": str,
  "published_time": str | None,  # ISO 8601 format
  "hoax_label": str | None,      # "hoax" or "non-hoax"
  "confidence": float | None,    # 0.0 - 1.0
  "created_at": str              # ISO 8601 format
}
```

### NewsListResponse
```python
{
  "total": int,
  "news": List[NewsResponse]
}
```

---

## Authentication

Saat ini API tidak memerlukan authentication. Untuk production, pertimbangkan menambahkan:
- API Key authentication
- JWT tokens
- Rate limiting

---

## Rate Limiting

Saat ini tidak ada rate limiting. Untuk production, pertimbangkan:
- Request limit per IP
- Request limit per API key
- Throttling untuk `/fetch-rss` endpoint

---

## CORS

API mengizinkan CORS dari:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)

Untuk production, update di `backend/app/main.py`:
```python
allow_origins=["https://your-frontend-domain.com"]
```

---

## Examples

### Python
```python
import requests

# Get all news
response = requests.get("http://localhost:8000/api/news/")
data = response.json()
print(f"Total news: {data['total']}")

# Get specific news
news_id = "abc123def456"
response = requests.get(f"http://localhost:8000/api/news/{news_id}")
news = response.json()
print(f"Title: {news['title']}")

# Fetch new RSS
response = requests.post("http://localhost:8000/api/news/fetch-rss")
result = response.json()
print(f"Processed: {result['processed']}")
```

### JavaScript
```javascript
// Get all news
const response = await fetch('http://localhost:8000/api/news/');
const data = await response.json();
console.log(`Total news: ${data.total}`);

// Get specific news
const newsId = 'abc123def456';
const newsResponse = await fetch(`http://localhost:8000/api/news/${newsId}`);
const news = await newsResponse.json();
console.log(`Title: ${news.title}`);

// Fetch new RSS
const fetchResponse = await fetch('http://localhost:8000/api/news/fetch-rss', {
  method: 'POST'
});
const result = await fetchResponse.json();
console.log(`Processed: ${result.processed}`);
```

### cURL
```bash
# Get all news
curl http://localhost:8000/api/news/

# Get all news with limit
curl "http://localhost:8000/api/news/?limit=10"

# Get specific news
curl http://localhost:8000/api/news/abc123def456

# Fetch new RSS
curl -X POST http://localhost:8000/api/news/fetch-rss
```

---

## Testing

### Using FastAPI Docs
Buka browser: `http://localhost:8000/docs`

FastAPI menyediakan interactive API documentation (Swagger UI) dimana Anda bisa:
- Melihat semua endpoints
- Test endpoints langsung dari browser
- Melihat request/response schema

### Using ReDoc
Alternatif documentation: `http://localhost:8000/redoc`

---

## Performance Notes

### `/api/news/fetch-rss` Endpoint
- **Durasi**: 1-5 menit per request tergantung jumlah artikel
- **Resource intensive**: Download + NLP model inference
- **Recommendation**: Jangan panggil endpoint ini bersamaan (concurrent)
- **Best practice**: Gunakan scheduler untuk automasi

### Model Inference
- **First load**: 10-30 detik (download model ~500MB)
- **Subsequent calls**: 1-3 detik per artikel
- **Memory**: ~2GB RAM untuk model

---

## Future Enhancements

Planned improvements:
- [ ] WebSocket support untuk real-time updates
- [ ] Batch processing endpoint
- [ ] Export endpoint (CSV, JSON)
- [ ] Search & filter endpoints
- [ ] Statistics & analytics endpoint
- [ ] User authentication
- [ ] API versioning

---

**Last Updated**: 2024-01-15
