# Backend - Hoax Detection News App

FastAPI backend untuk sistem deteksi hoaks berita Indonesia.

## Features

- RESTful API dengan FastAPI
- Integrasi Firebase Firestore
- RSS Feed Parser
- Web Content Scraper
- AI-based Hoax Detection (IndoBERT)
- Automatic News Processing

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env`:
```env
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
RSS_FEED_URL=https://www.antaranews.com/rss/terkini.xml
MODEL_NAME=indobenchmark/indobert-base-p1
```

3. Download Firebase credentials:
   - Go to Firebase Console
   - Project Settings > Service Accounts
   - Generate new private key
   - Save as `firebase-credentials.json` in backend folder

## Running

### Development
```bash
uvicorn app.main:app --reload
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Scripts
```bash
# Windows
run.bat

# Linux/Mac
chmod +x run.sh
./run.sh
```

## API Endpoints

- `GET /` - Health check
- `GET /api/news/` - Get all news
- `GET /api/news/{id}` - Get news by ID
- `POST /api/news/fetch-rss` - Fetch and process new RSS articles

See [API Documentation](../docs/API_DOCUMENTATION.md) for details.

## Project Structure

```
backend/
├── app/
│   ├── models/        # Pydantic models
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic
│   │   ├── hoax_detector.py    # AI model
│   │   ├── rss_fetcher.py      # RSS parser
│   │   └── news_service.py     # News management
│   └── utils/         # Utilities
│       └── firebase_config.py  # Firebase setup
├── requirements.txt
├── scheduler.py       # Standalone scheduler
└── .env
```

## Scheduler

Run scheduler manually:
```bash
python scheduler.py
```

See [CRON_SETUP.md](../docs/CRON_SETUP.md) for automation.

## Testing

```bash
# Test API
curl http://localhost:8000

# Interactive docs
# Open browser: http://localhost:8000/docs
```

## Dependencies

Main dependencies:
- FastAPI - Web framework
- Uvicorn - ASGI server
- Firebase Admin - Firestore integration
- Transformers - Hugging Face models
- PyTorch - Deep learning framework
- Feedparser - RSS parsing
- BeautifulSoup4 - Web scraping

## Notes

- First run will download IndoBERT model (~500MB)
- Model loading takes 10-30 seconds
- Requires ~2GB RAM for model inference
- Fine-tune model for production use

## License

Educational project
