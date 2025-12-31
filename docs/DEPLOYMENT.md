# Deployment Guide

Panduan deployment aplikasi Hoax Detection News App ke production.

## Overview

Aplikasi ini terdiri dari 2 bagian yang bisa di-deploy terpisah:
1. **Backend** (FastAPI) - Bisa deploy ke Google Cloud Run, Heroku, Railway, dll
2. **Frontend** (React) - Bisa deploy ke Vercel, Netlify, Firebase Hosting, dll

## Backend Deployment

### Option 1: Google Cloud Run (Recommended)

#### Prerequisites
- Google Cloud account
- gcloud CLI installed
- Docker installed

#### Steps

1. **Buat Dockerfile** di folder `backend/`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
ENV PORT=8080
EXPOSE 8080

# Run application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. **Buat `.dockerignore`**:

```
__pycache__
*.pyc
venv/
.env
firebase-credentials.json
.git
```

3. **Build & Deploy**:

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/hoax-detection-backend

# Deploy to Cloud Run
gcloud run deploy hoax-detection-backend \
  --image gcr.io/YOUR_PROJECT_ID/hoax-detection-backend \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json \
  --set-env-vars RSS_FEED_URL=https://www.antaranews.com/rss/terkini.xml \
  --set-env-vars MODEL_NAME=indobenchmark/indobert-base-p1 \
  --memory 2Gi \
  --timeout 300
```

4. **Add Firebase Credentials as Secret**:

```bash
# Create secret
echo -n "$(cat firebase-credentials.json)" | \
  gcloud secrets create firebase-credentials --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding firebase-credentials \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run to use secret
gcloud run services update hoax-detection-backend \
  --update-secrets=FIREBASE_CREDENTIALS=/app/firebase-credentials.json=firebase-credentials:latest
```

5. **Get deployed URL**:
```bash
gcloud run services describe hoax-detection-backend --format 'value(status.url)'
```

---

### Option 2: Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Steps

1. **Buat `Procfile`** di folder `backend/`:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. **Buat `runtime.txt`**:

```
python-3.10.13
```

3. **Deploy**:

```bash
# Login
heroku login

# Create app
heroku create hoax-detection-backend

# Set environment variables
heroku config:set FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
heroku config:set RSS_FEED_URL=https://www.antaranews.com/rss/terkini.xml
heroku config:set MODEL_NAME=indobenchmark/indobert-base-p1

# Deploy
git push heroku main

# Open app
heroku open
```

⚠️ **Note**: Heroku free tier mungkin tidak cukup untuk model AI. Pertimbangkan paid tier.

---

### Option 3: Railway

#### Prerequisites
- Railway account

#### Steps

1. **Connect GitHub repository** di Railway dashboard
2. **Select backend folder** as root
3. **Set environment variables**:
   - `FIREBASE_CREDENTIALS`: Paste isi file JSON
   - `RSS_FEED_URL`: URL RSS feed
   - `MODEL_NAME`: indobenchmark/indobert-base-p1

4. **Deploy** akan otomatis

---

## Frontend Deployment

### Option 1: Vercel (Recommended)

#### Prerequisites
- Vercel account
- GitHub repository

#### Steps

1. **Update `frontend/.env.production`**:

```env
VITE_API_URL=https://your-backend-url.com/api
```

2. **Deploy via Vercel Dashboard**:
   - Import GitHub repository
   - Set Root Directory: `frontend`
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Environment Variables: Add `VITE_API_URL`

3. **Or deploy via CLI**:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

---

### Option 2: Netlify

#### Steps

1. **Buat `netlify.toml`** di folder `frontend/`:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **Deploy via Netlify Dashboard**:
   - Connect GitHub repository
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
   - Environment: `VITE_API_URL=https://your-backend-url.com/api`

3. **Or deploy via CLI**:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod
```

---

### Option 3: Firebase Hosting

#### Steps

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
cd frontend
firebase init hosting

# Build
npm run build

# Deploy
firebase deploy --only hosting
```

**firebase.json**:
```json
{
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

---

## Environment Variables

### Backend (Production)

| Variable | Description | Example |
|----------|-------------|---------|
| FIREBASE_CREDENTIALS_PATH | Path to credentials | /app/firebase-credentials.json |
| FIREBASE_CREDENTIALS | JSON string (alternative) | {"type":"service_account",...} |
| RSS_FEED_URL | RSS feed URL | https://... |
| MODEL_NAME | Hugging Face model | indobenchmark/indobert-base-p1 |
| PORT | Server port | 8080 |

### Frontend (Production)

| Variable | Description | Example |
|----------|-------------|---------|
| VITE_API_URL | Backend API URL | https://api.example.com/api |

---

## Scheduler Deployment

### GitHub Actions (Free)

Already configured in `.github/workflows/fetch-news.yml`

**Setup**:
1. Push code to GitHub
2. Go to repository Settings > Secrets
3. Add secrets:
   - `FIREBASE_CREDENTIALS`: Content of firebase-credentials.json
   - `RSS_FEED_URL`: RSS feed URL
   - `MODEL_NAME`: Model name (optional)

**Schedule**: Runs every 6 hours automatically

---

### Google Cloud Scheduler

```bash
# Create Cloud Scheduler job
gcloud scheduler jobs create http fetch-news-job \
  --schedule="0 */6 * * *" \
  --uri="https://your-backend-url.com/api/news/fetch-rss" \
  --http-method=POST \
  --location=asia-southeast1
```

---

### Cron Job (VPS/Server)

If you have a VPS:

```bash
# Edit crontab
crontab -e

# Add job (every 6 hours)
0 */6 * * * cd /path/to/backend && /usr/bin/python3 scheduler.py >> /var/log/hoax-detection.log 2>&1
```

---

## Database Setup

Firestore sudah di-setup saat development. Untuk production:

### Security Rules

Update Firestore Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /news/{document=**} {
      // Allow read from anywhere
      allow read: if true;

      // Only allow write from backend service account
      allow write: if false;
    }
  }
}
```

### Indexes

Create composite index if needed:

```bash
# Via Firebase Console
# Firestore > Indexes > Create Index
# Collection: news
# Fields: created_at (Descending)
```

---

## Post-Deployment Checklist

### Backend
- [ ] API endpoint accessible
- [ ] Health check returns 200
- [ ] Swagger docs available at /docs
- [ ] Firebase connection working
- [ ] Environment variables set correctly
- [ ] CORS configured for frontend domain
- [ ] Model loads successfully
- [ ] RSS fetch works

### Frontend
- [ ] Website accessible
- [ ] API calls working
- [ ] News displayed correctly
- [ ] Hoax labels showing
- [ ] Mobile responsive
- [ ] No console errors

### Scheduler
- [ ] First run successful
- [ ] Cron/GitHub Actions configured
- [ ] Logs accessible
- [ ] Error notifications setup

---

## Monitoring & Logging

### Backend Logging

Add logging to `app/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Application started")
```

### Error Tracking

Consider adding:
- **Sentry** for error tracking
- **Google Cloud Logging** for Cloud Run
- **Datadog** for comprehensive monitoring

---

## Performance Optimization

### Backend
- Enable response caching
- Use connection pooling for Firestore
- Lazy load AI model
- Implement rate limiting

### Frontend
- Enable CDN
- Optimize images
- Code splitting
- Enable compression

---

## Security Considerations

### Backend
- [ ] Don't commit credentials
- [ ] Use environment variables
- [ ] Enable HTTPS only
- [ ] Implement rate limiting
- [ ] Validate input data
- [ ] Use CORS whitelist

### Frontend
- [ ] Use environment variables
- [ ] Don't expose API keys
- [ ] Sanitize user input
- [ ] Enable CSP headers

---

## Cost Estimation

### Free Tier (Development/Small Scale)
- **Firebase**: Free tier (50K reads/day)
- **Vercel**: Free tier (100GB bandwidth)
- **GitHub Actions**: 2000 minutes/month

### Paid (Production Scale)
- **Cloud Run**: ~$5-20/month (depends on traffic)
- **Firestore**: ~$1-10/month (depends on usage)
- **Vercel Pro**: $20/month
- **Total**: ~$25-50/month for small-medium traffic

---

## Troubleshooting

### Build Errors
```bash
# Clear cache
rm -rf node_modules dist .next
npm install
npm run build
```

### CORS Errors
Update backend `app/main.py`:
```python
allow_origins=["https://your-frontend-domain.com"]
```

### Model Loading Timeout
Increase timeout in deployment config:
```bash
--timeout 300  # 5 minutes
```

### Firebase Permission Denied
Check Firestore security rules and service account permissions.

---

## Rollback Strategy

If deployment fails:

1. **Vercel/Netlify**: Use dashboard to rollback to previous deployment
2. **Cloud Run**:
```bash
gcloud run services update-traffic hoax-detection-backend \
  --to-revisions=PREVIOUS_REVISION=100
```

---

## Support

Jika ada masalah saat deployment:
1. Check logs di platform hosting
2. Review environment variables
3. Test API endpoints dengan curl/Postman
4. Check Firebase Console untuk errors

---

**Good luck with deployment! 🚀**
