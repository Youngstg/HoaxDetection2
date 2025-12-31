# Setup Cron Job untuk Scheduler

## Linux/Mac

### 1. Buka crontab editor
```bash
crontab -e
```

### 2. Tambahkan cron job

Untuk menjalankan setiap 6 jam:
```bash
0 */6 * * * cd /path/to/HoaxDetection/backend && /usr/bin/python3 scheduler.py >> /var/log/hoax-detection.log 2>&1
```

Untuk menjalankan setiap hari pukul 08:00:
```bash
0 8 * * * cd /path/to/HoaxDetection/backend && /usr/bin/python3 scheduler.py >> /var/log/hoax-detection.log 2>&1
```

### 3. Verifikasi cron job
```bash
crontab -l
```

## Windows (Task Scheduler)

### 1. Buat batch script

Buat file `run_scheduler.bat`:
```batch
@echo off
cd /d D:\HoaxDetection\backend
python scheduler.py >> scheduler.log 2>&1
```

### 2. Setup Task Scheduler
1. Buka Task Scheduler
2. Klik "Create Basic Task"
3. Nama: "Hoax Detection News Scheduler"
4. Trigger: Daily atau sesuai kebutuhan
5. Action: Start a program
6. Program: `D:\HoaxDetection\backend\run_scheduler.bat`

## GitHub Actions

Scheduler juga sudah dikonfigurasi di `.github/workflows/fetch-news.yml` untuk berjalan otomatis setiap 6 jam.

### Setup GitHub Actions:
1. Tambahkan secrets di GitHub repository:
   - `FIREBASE_CREDENTIALS`: Isi file firebase-credentials.json
   - `RSS_FEED_URL`: URL RSS feed
   - `MODEL_NAME`: Nama model (optional, default: indobenchmark/indobert-base-p1)

2. GitHub Actions akan otomatis menjalankan scheduler sesuai jadwal

## Manual Execution

Untuk menjalankan scheduler secara manual:

```bash
cd backend
python scheduler.py
```
