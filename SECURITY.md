# Security Guidelines

## Sensitive Files - NEVER Commit These!

The following files contain sensitive information and should **NEVER** be committed to the repository:

### 1. Environment Variables (`.env`)
```
backend/.env          # Contains Firebase config, API settings
frontend/.env         # Contains API URLs
```

**What's inside:**
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase credentials
- `MODEL_PATH` - Path to ML model
- `USE_ML_MODEL` - ML configuration

**Safe alternative:** Use `.env.example` as template (already in repo)

### 2. Firebase Credentials
```
backend/firebase-credentials.json
*-credentials.json
serviceAccount*.json
```

**What's inside:**
- `project_id` - Your Firebase project ID
- `private_key` - RSA private key (VERY SENSITIVE!)
- `client_email` - Service account email

**How to get:** Download from Firebase Console > Project Settings > Service Accounts

### 3. Trained Model Files
```
backend/hoax_model/
*.safetensors
*.pth
*.pt
```

**Why ignored:**
- Too large for GitHub (500MB+)
- Can be regenerated from training data

**How to share:** Use Git LFS or cloud storage (Google Drive, S3)

---

## Setting Up Securely

### For Development

1. **Copy example files:**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

2. **Get Firebase credentials:**
   - Go to Firebase Console
   - Project Settings > Service Accounts
   - Generate new private key
   - Save as `backend/firebase-credentials.json`

3. **Train or download model:**
   ```bash
   cd backend
   python train_model.py --dataset dataset.csv
   ```

### For Production

1. **Use environment variables** instead of `.env` files
2. **Use Secret Manager** (GCP, AWS, Azure) for credentials
3. **Never expose credentials in logs or error messages**

---

## Git Safety Checklist

Before pushing to GitHub, verify:

```bash
# Check no sensitive files are staged
git status

# Verify .gitignore is working
git ls-files | findstr -i "credential env secret"
# Should only show .env.example files

# Check for accidental commits
git log --oneline --all -- "*.json" "*credential*" "*.env"
# Should return nothing for sensitive files
```

---

## If You Accidentally Committed Secrets

### Option 1: Remove from history (if not pushed)
```bash
git reset --soft HEAD~1
git restore --staged <sensitive-file>
```

### Option 2: Use BFG Repo-Cleaner (if pushed)
```bash
# Install BFG
# Then run:
bfg --delete-files firebase-credentials.json
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

### Option 3: Rotate credentials immediately
1. Go to Firebase Console
2. Generate new service account key
3. Delete old key
4. Update your local `.env` and credentials file

---

## Environment Variables Reference

### Backend (`backend/.env`)
```env
# Firebase (REQUIRED)
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# RSS Feed
RSS_FEED_URL=https://www.antaranews.com/rss/terkini.xml

# ML Model
MODEL_NAME=indobenchmark/indobert-base-p1
MODEL_PATH=./hoax_model
USE_ML_MODEL=true

# Auto-Retrain
TRAINING_THRESHOLD=50
TRAINING_DATASET_PATH=./training_data
```

### Frontend (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000/api
```

---

## Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Contact the maintainers privately
3. Provide details about the vulnerability
4. Allow time for a fix before disclosure

---

## Security Best Practices

1. **Rotate credentials regularly**
2. **Use least-privilege access** for service accounts
3. **Enable Firebase Security Rules**
4. **Monitor for unauthorized access**
5. **Keep dependencies updated**
