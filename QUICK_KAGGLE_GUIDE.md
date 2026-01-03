# Quick Guide: Using Kaggle Indonesia False News Dataset

Step-by-step menggunakan dataset Kaggle yang sudah Anda download.

---

## 📋 Yang Anda Punya Sekarang:

✅ File metadata: `indonesiafalsenews-metadata.json`

**Yang dibutuhkan**:
- `Data_latih.csv` (Training data)
- `Data_uji.csv` (Test data - optional)

---

## 🚀 Langkah-langkah:

### Step 1: Extract Dataset

Jika Anda download dari Kaggle, biasanya dalam format **ZIP**.

**Cari file ZIP** di folder Downloads:
```
C:\Users\YourName\Downloads\indonesiafalsenews.zip
```

atau

```
C:\Users\YourName\Downloads\archive.zip
```

**Extract ZIP**:
1. Right-click pada file ZIP
2. Extract All → pilih lokasi: `D:\HoaxDetection\backend\datasets\`
3. Atau via command:

```powershell
# PowerShell
Expand-Archive -Path "C:\Users\YourName\Downloads\indonesiafalsenews.zip" -DestinationPath "D:\HoaxDetection\backend\datasets\kaggle"
```

Setelah extract, harusnya ada:
```
D:\HoaxDetection\backend\datasets\kaggle\
├── Data_latih.csv
└── Data_uji.csv
```

---

### Step 2: Convert Dataset ke Format Training

Jalankan converter script:

```bash
cd D:\HoaxDetection\backend

# Otomatis detect files
python utils/convert_kaggle_dataset.py datasets/kaggle/Data_latih.csv datasets/kaggle/Data_uji.csv

# Output: dataset.csv
```

**Atau jika di folder yang sama**:
```bash
cd datasets/kaggle
python ../../utils/convert_kaggle_dataset.py Data_latih.csv Data_uji.csv dataset.csv
```

---

### Step 3: Review Converted Dataset

Buka `dataset.csv` di Excel atau text editor.

**Format yang benar**:
```csv
text,label
"Judul berita. Isi lengkap berita...",0
"Hoax title. Hoax content...",1
```

**Kolom**:
- `text`: Gabungan judul + narasi
- `label`: 0 = non-hoax, 1 = hoax

---

### Step 4: Train Model

```bash
cd D:\HoaxDetection\backend

# Basic training
python train_model.py --dataset dataset.csv --epochs 5

# With options
python train_model.py \
  --dataset dataset.csv \
  --epochs 10 \
  --batch-size 16 \
  --output ./indonesia_hoax_model
```

**Training time**:
- CPU: 20-40 menit
- GPU: 5-10 menit

---

### Step 5: Use Trained Model

Update `.env`:
```env
USE_ML_MODEL=true
MODEL_NAME=./indonesia_hoax_model
```

Restart backend:
```bash
uvicorn app.main:app --reload
```

Test di frontend!

---

## 🐛 Troubleshooting

### ❌ "Data_latih.csv not found"

**Penyebab**: File CSV belum di-extract atau lokasi salah

**Solusi**:
1. Cari file `indonesiafalsenews.zip` atau `archive.zip`
2. Extract ke folder yang jelas
3. Catat lokasi file CSV
4. Run script dengan path lengkap:
   ```bash
   python utils/convert_kaggle_dataset.py "C:\path\to\Data_latih.csv"
   ```

### ❌ "Unexpected labels"

**Penyebab**: Label format berbeda dari expected (0/1)

**Solusi**: Script sudah auto-handle conversion:
- Labels 1/2 → converted to 0/1
- Labels 0/1 → used as-is

### ❌ Dataset imbalanced

**Output**:
```
Non-hoax: 800 (80%)
Hoax: 200 (20%)
⚠️  WARNING: Dataset imbalanced
```

**Solusi**: Use class weights saat training
```bash
python train_model.py --dataset dataset.csv --use-class-weights
```

---

## 📊 Expected Output

### Conversion Output:
```
============================================================
Indonesia False News Dataset Converter
============================================================

📂 Loading training data: Data_latih.csv
   ✅ Loaded 1000 rows

📋 Columns: ['ID', 'label', 'tanggal', 'judul', 'narasi', 'nama file gambar']

📈 Label distribution:
1    600
2    400

🏷️  Unique labels: [1 2]
   Labels are 1/2, converting to 0/1...

📊 Converted Dataset Statistics:
   Total samples: 1000
   Non-hoax (label=0): 600 (60.0%)
   Hoax (label=1): 400 (40.0%)

✅ Converted dataset saved to: dataset.csv
```

### Training Output:
```
Loading dataset from dataset.csv...
Total samples: 1000
Non-hoax: 600 (60.0%)
Hoax: 400 (40.0%)

Splitting dataset...
Train: 700 samples
Validation: 150 samples
Test: 150 samples

Training model...
Epoch 1/5: loss=0.45, accuracy=0.82
Epoch 2/5: loss=0.32, accuracy=0.87
...

Test Results:
  accuracy: 0.8867
  precision: 0.8654
  recall: 0.9100
  f1: 0.8871

✅ Training completed!
Model saved to: ./hoax_model
```

---

## 💡 Tips

### Tip 1: Check CSV Encoding

Jika ada error saat load CSV (karakter aneh):

```python
# Read with different encoding
df = pd.read_csv('Data_latih.csv', encoding='utf-8')
# or
df = pd.read_csv('Data_latih.csv', encoding='latin-1')
# or
df = pd.read_csv('Data_latih.csv', encoding='cp1252')
```

Script sudah handle ini secara otomatis.

### Tip 2: Preview Data Before Training

```bash
# First 10 rows
head -10 dataset.csv

# Or in Python
python -c "import pandas as pd; print(pd.read_csv('dataset.csv').head())"
```

### Tip 3: Start Small

Test dengan dataset kecil dulu:

```python
# Sample 100 rows for quick test
import pandas as pd
df = pd.read_csv('dataset.csv')
df_sample = df.sample(100)
df_sample.to_csv('dataset_small.csv', index=False)
```

```bash
# Quick training test
python train_model.py --dataset dataset_small.csv --epochs 2
```

---

## 📚 Dataset Info

**Source**: https://www.kaggle.com/datasets/muhammadghazimuharam/indonesiafalsenews

**Description**: Indonesia False News (Hoax) Dataset untuk text classification

**Size**: ~547 KB

**Language**: Bahasa Indonesia

**Columns**:
- ID: Unique identifier
- label: Hoax label (1/2 or 0/1)
- tanggal: Date
- judul: News title
- narasi: News content
- nama file gambar: Image filename (not used)

---

## ✅ Checklist

Sebelum training, pastikan:

- [ ] Dataset ZIP sudah di-extract
- [ ] File `Data_latih.csv` ada dan bisa dibuka
- [ ] Converter script sudah dijalankan
- [ ] File `dataset.csv` ter-generate dengan benar
- [ ] Preview dataset (pastikan text + label valid)
- [ ] Backend dependencies sudah installed
- [ ] Ready untuk training!

---

**Last Updated**: 2024-12-31
