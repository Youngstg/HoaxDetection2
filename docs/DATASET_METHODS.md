# Dataset Methods untuk Local Training

Panduan lengkap menggunakan berbagai sumber dataset untuk training model hoax detection lokal.

---

## 🎯 Metode Dataset yang Didukung

### ✅ 1. **CSV File** (Paling Simple)

#### Format:
```csv
text,label
"Berita normal dari Kompas...",0
"WAJIB SHARE! Hoax content...",1
```

#### Usage:
```bash
python train_model.py --dataset path/to/dataset.csv
```

#### Lokasi File Bisa:
- ✅ Lokal: `D:\datasets\hoax_dataset.csv`
- ✅ Network drive: `\\server\datasets\hoax.csv`
- ✅ External drive: `E:\my_datasets\hoax.csv`
- ✅ Google Drive (mounted): `G:\My Drive\datasets\hoax.csv`

---

### ✅ 2. **Kaggle Dataset**

#### Option A: Download Manual

1. **Download dari Kaggle**:
   - Go to dataset page
   - Click "Download"
   - Extract ZIP file

2. **Simpan di Lokal**:
   ```
   D:\datasets\kaggle\
   ├── train.csv
   ├── test.csv
   └── validation.csv
   ```

3. **Use in Training**:
   ```bash
   python train_model.py --dataset D:\datasets\kaggle\train.csv
   ```

#### Option B: Kaggle API (Automated)

**Install Kaggle CLI**:
```bash
pip install kaggle
```

**Setup API Token**:
1. Go to Kaggle → Account → Create API Token
2. Save `kaggle.json` to `~/.kaggle/` (or `C:\Users\YourName\.kaggle\`)

**Download Dataset**:
```bash
# List datasets
kaggle datasets list -s "indonesian fake news"

# Download specific dataset
kaggle datasets download -d username/dataset-name

# Extract
unzip dataset-name.zip -d D:\datasets\kaggle\
```

**Use in Code**:
```python
# train_model.py supports this
python train_model.py --dataset D:\datasets\kaggle\train.csv
```

---

### ✅ 3. **Google Drive**

#### Option A: Download ke Lokal

1. **Download dari Google Drive** (via browser)
2. **Simpan ke lokal**:
   ```
   D:\datasets\gdrive\hoax_dataset.csv
   ```
3. **Use**:
   ```bash
   python train_model.py --dataset D:\datasets\gdrive\hoax_dataset.csv
   ```

#### Option B: Mount Google Drive (Windows)

**Using Google Drive Desktop**:
1. Install [Google Drive for Desktop](https://www.google.com/drive/download/)
2. Mount as drive letter (e.g., `G:`)
3. Access directly:
   ```bash
   python train_model.py --dataset "G:\My Drive\datasets\hoax.csv"
   ```

#### Option C: gdown (CLI Download)

```bash
pip install gdown

# Download file
gdown https://drive.google.com/uc?id=FILE_ID

# Or download folder
gdown --folder https://drive.google.com/drive/folders/FOLDER_ID
```

---

### ✅ 4. **Hugging Face Datasets**

#### Load dari Hugging Face Hub:

```python
# train_model.py - modify load_dataset method
from datasets import load_dataset

# Load dari Hub
dataset = load_dataset("indonesian_hoax", split="train")

# Save to local CSV
dataset.to_csv("local_dataset.csv")

# Train
python train_model.py --dataset local_dataset.csv
```

#### Download & Cache Lokal:

```python
from datasets import load_dataset

# First load akan download & cache
dataset = load_dataset("dataset_name")

# Cache location: ~/.cache/huggingface/datasets/
# Next load akan pakai cache (offline)
```

---

### ✅ 5. **Multiple CSV Files**

Jika punya banyak file CSV:

```
D:\datasets\
├── dataset1.csv
├── dataset2.csv
└── dataset3.csv
```

**Combine them**:

#### Option A: Manual Combine
```bash
# Windows PowerShell
Get-Content D:\datasets\*.csv | Set-Content combined.csv

# Or Python
python -c "
import pandas as pd
import glob

files = glob.glob('D:/datasets/*.csv')
df_list = [pd.read_csv(f) for f in files]
combined = pd.concat(df_list, ignore_index=True)
combined.to_csv('combined.csv', index=False)
"
```

#### Option B: Modify train_model.py

Saya buatkan helper script:

```python
# combine_datasets.py
import pandas as pd
import glob
import sys

def combine_csv_files(pattern, output):
    files = glob.glob(pattern)
    print(f"Found {len(files)} files")

    df_list = []
    for f in files:
        print(f"Reading {f}...")
        df_list.append(pd.read_csv(f))

    combined = pd.concat(df_list, ignore_index=True)
    combined.to_csv(output, index=False)
    print(f"Combined dataset saved to {output}")
    print(f"Total samples: {len(combined)}")

if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else "*.csv"
    output = sys.argv[2] if len(sys.argv) > 2 else "combined.csv"
    combine_csv_files(pattern, output)
```

**Usage**:
```bash
python combine_datasets.py "D:/datasets/*.csv" combined.csv
python train_model.py --dataset combined.csv
```

---

### ✅ 6. **Database (SQL)**

Jika data ada di database:

```python
# export_from_db.py
import pandas as pd
import sqlite3  # or pymysql, psycopg2, etc.

# Connect to database
conn = sqlite3.connect('hoax_database.db')

# Query data
query = "SELECT text, label FROM news WHERE label IS NOT NULL"
df = pd.read_sql_query(query, conn)

# Save to CSV
df.to_csv('dataset_from_db.csv', index=False)

# Train
# python train_model.py --dataset dataset_from_db.csv
```

---

### ✅ 7. **Excel Files**

Jika dataset dalam format Excel:

```python
# excel_to_csv.py
import pandas as pd

# Read Excel
df = pd.read_excel('dataset.xlsx', sheet_name='Sheet1')

# Save as CSV
df.to_csv('dataset.csv', index=False)

# Train
# python train_model.py --dataset dataset.csv
```

**Or update train_model.py** untuk support Excel:

```python
# train_model.py - modify load_dataset
if dataset_path.endswith('.xlsx'):
    df = pd.read_excel(dataset_path)
elif dataset_path.endswith('.csv'):
    df = pd.read_csv(dataset_path)
```

---

### ✅ 8. **JSON/JSONL Files**

```python
# json_to_csv.py
import pandas as pd
import json

# Read JSON
with open('dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Or JSONL (line-delimited)
df = pd.read_json('dataset.jsonl', lines=True)

# Save as CSV
df.to_csv('dataset.csv', index=False)
```

---

## 🗂️ Recommended Dataset Structure

### Lokasi Penyimpanan:

```
D:\
└── HoaxDetection\
    ├── backend\
    │   ├── datasets\           ← Recommended location
    │   │   ├── raw\           ← Original downloads
    │   │   ├── processed\     ← Cleaned datasets
    │   │   └── final\         ← Ready for training
    │   └── train_model.py
    └── ...
```

### Format CSV Standard:

```csv
text,label,source,confidence
"Full article text...",0,"Kompas",0.95
"Hoax content...",1,"Manual",1.0
```

**Required columns**:
- `text`: Full article text
- `label`: 0 (non-hoax) or 1 (hoax)

**Optional columns**:
- `source`: Source name
- `confidence`: Label confidence (0-1)
- `url`: Original URL
- `title`: Article title
- `collected_at`: Timestamp

---

## 🔍 Dataset dari Kaggle - Contoh Nyata

### 1. **Indonesian Fake News Dataset**

**Kaggle**: [Indonesian Fake News](https://www.kaggle.com/datasets/saurabhshahane/fake-news-classification)

**Download**:
```bash
kaggle datasets download -d saurabhshahane/fake-news-classification
unzip fake-news-classification.zip -d D:\datasets\kaggle\
```

**Use**:
```bash
python train_model.py --dataset D:\datasets\kaggle\train.csv
```

### 2. **Preprocessed Indonesian News**

**Kaggle**: Search "indonesian news dataset"

**Steps**:
1. Download ZIP
2. Extract to `D:\datasets\`
3. Check CSV format (text, label columns)
4. If different format, convert:

```python
# convert_format.py
import pandas as pd

df = pd.read_csv('original.csv')

# Rename columns to match expected format
df_new = df.rename(columns={
    'content': 'text',  # or 'article', 'body'
    'is_fake': 'label'   # or 'class', 'category'
})

# Convert labels to 0/1 if needed
df_new['label'] = df_new['label'].map({'fake': 1, 'real': 0})

df_new[['text', 'label']].to_csv('formatted_dataset.csv', index=False)
```

---

## 💾 Google Drive Access - Step by Step

### Method 1: Google Drive Desktop (Recommended)

**Install**:
1. Download [Google Drive for Desktop](https://www.google.com/drive/download/)
2. Install & login
3. Choose sync location

**Access**:
```bash
# Drive akan mount sebagai G:\ (atau drive letter lain)
python train_model.py --dataset "G:\My Drive\datasets\hoax.csv"
```

**Advantages**:
- ✅ Real-time sync
- ✅ Offline access (cached)
- ✅ No manual download

### Method 2: Manual Download

**Steps**:
1. Open Google Drive in browser
2. Right-click file → Download
3. Save to local (e.g., `D:\datasets\`)
4. Use normally

**Advantages**:
- ✅ Full control
- ✅ No sync overhead
- ✅ Works on any OS

### Method 3: gdown CLI

**Install**:
```bash
pip install gdown
```

**Get File ID**:
- URL: `https://drive.google.com/file/d/1A2B3C4D5E6F7/view`
- ID: `1A2B3C4D5E6F7`

**Download**:
```bash
gdown 1A2B3C4D5E6F7 -O dataset.csv
```

**Advantages**:
- ✅ Scriptable
- ✅ Good for large files
- ✅ Resume support

---

## 🚀 Training dengan Dataset Lokal

### Basic Usage:

```bash
# Simple
python train_model.py --dataset D:\datasets\hoax.csv

# With options
python train_model.py \
  --dataset D:\datasets\hoax.csv \
  --epochs 5 \
  --batch-size 16 \
  --output ./my_model
```

### Absolute vs Relative Path:

**Absolute** (Recommended):
```bash
python train_model.py --dataset D:\datasets\hoax.csv
```

**Relative**:
```bash
# From backend folder
python train_model.py --dataset ../datasets/hoax.csv
```

### Path dengan Spasi:

```bash
# Use quotes
python train_model.py --dataset "D:\My Datasets\hoax dataset.csv"
```

---

## ⚡ Performance Tips

### 1. **SSD vs HDD**

| Storage | Read Speed | Training Time |
|---------|-----------|---------------|
| SSD | Fast | Baseline |
| HDD | Slow | +20-30% slower |
| Network | Variable | +50-100% slower |

**Recommendation**: Copy dataset ke SSD lokal untuk training.

### 2. **Dataset Size**

| Size | Loading Time | Recommendation |
|------|-------------|----------------|
| <100 MB | <5 sec | Load directly |
| 100-500 MB | 5-30 sec | Fine |
| 500 MB-2 GB | 30-120 sec | Consider chunking |
| >2 GB | >2 min | Use Datasets library streaming |

### 3. **Caching**

Training script otomatis cache tokenized data:

```python
# First run: slow (tokenize)
python train_model.py --dataset data.csv  # 10 min

# Second run: fast (use cache)
python train_model.py --dataset data.csv  # 2 min
```

---

## 🛠️ Helper Scripts

Saya buatkan beberapa helper scripts:

