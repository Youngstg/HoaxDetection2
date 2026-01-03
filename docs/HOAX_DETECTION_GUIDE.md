# Hoax Detection Implementation Guide

Panduan lengkap untuk implementasi deteksi hoax dengan rule-based dan ML model.

---

## 🎯 Sistem Deteksi Saat Ini

### **Rule-Based Detector** (Default - AKTIF)

Menggunakan pattern matching dan keyword analysis:

#### Parameter yang Digunakan:

| Parameter | Bobot | Deskripsi |
|-----------|-------|-----------|
| **Keyword Score** | 30% | Deteksi kata-kata sensasional ("WAJIB SHARE!", "VIRAL", dll) |
| **Pattern Score** | 25% | Regex pattern untuk clickbait dan klaim absolut |
| **Source Score** | 25% | Kredibilitas sumber (media terpercaya vs tidak dikenal) |
| **Caps Score** | 10% | Penggunaan huruf kapital berlebihan |
| **Punctuation Score** | 10% | Tanda seru berlebihan (!!!) |

#### Threshold:
- **Hoax probability > 0.4** → Label: "hoax"
- **Hoax probability ≤ 0.4** → Label: "non-hoax"
- **Confidence max**: 95% (untuk rule-based)

#### Media Terpercaya (Auto non-hoax):
- kompas.com
- tempo.co
- detik.com
- antaranews.com
- cnn.com
- bbc.com
- liputan6.com
- dll (lihat `rule_based_detector.py`)

---

## 🚀 Cara Menggunakan

### Opsi 1: Rule-Based (Default - Sudah Aktif)

Sudah berjalan otomatis! Setiap kali fetch RSS, sistem akan:
1. Analyze text dengan 5 parameter
2. Calculate weighted score
3. Return label + confidence

**Tidak perlu setup tambahan!**

---

### Opsi 2: Train Model ML (Recommended untuk Akurasi Lebih Baik)

#### Step 1: Collect Dataset

```bash
cd backend
python dataset_collector.py
```

**Output**: `dataset.csv`

Script akan:
- ✅ Auto-collect 100 berita dari media terpercaya (non-hoax)
- ⚠️ Perlu manual input untuk hoax samples

#### Step 2: Tambahkan Hoax Samples Manual

Buat file `backend/hoax_samples.txt`:

```
WAJIB SHARE! Vaksin COVID menyebabkan autisme, kata dokter
VIRAL! Air putih hangat bisa menyembuhkan kanker 100% terbukti
BREAKING NEWS! Pemerintah menyembunyikan fakta tentang...
Rahasia mengejutkan yang DILARANG disebarkan!!!
```

**Sumber hoax samples**:
- [TurnBackHoax](https://turnbackhoax.id/)
- [Cek Fakta Tempo](https://cekfakta.tempo.co/)
- [Liputan6 Cek Fakta](https://www.liputan6.com/cek-fakta)
- [Mafindo](https://www.mafindo.or.id/)

Kemudian load:

```bash
python dataset_collector.py --load-hoax
```

#### Step 3: Review Dataset

Buka `dataset.csv` dan pastikan:
- ✅ Minimal 100 samples per class (non-hoax dan hoax)
- ✅ Balance antara kedua class
- ✅ Text quality bagus (tidak ada duplikat, dll)

#### Step 4: Train Model

```bash
python train_model.py --epochs 5 --batch-size 8
```

**Parameter training**:
- `--epochs`: Jumlah epoch (default: 3, recommended: 5-10)
- `--batch-size`: Batch size (default: 8, adjust sesuai RAM/GPU)
- `--dataset`: Path ke dataset (default: dataset.csv)
- `--output`: Output directory (default: ./hoax_model)

**Training time**:
- CPU: 30-60 menit (tergantung dataset size)
- GPU: 5-15 menit

#### Step 5: Gunakan Trained Model

Update `backend/.env`:

```env
USE_ML_MODEL=true
MODEL_NAME=./hoax_model
```

Restart backend server:

```bash
uvicorn app.main:app --reload
```

Sekarang sistem akan menggunakan ML model Anda!

---

## 📊 Perbandingan Metode

| Aspect | Rule-Based | ML Model (Fine-tuned) |
|--------|------------|----------------------|
| **Setup Time** | ✅ Instant | ❌ 1-2 jam (collect + train) |
| **Accuracy** | ⚠️ Sedang (70-80%) | ✅ Tinggi (85-95%) |
| **Maintenance** | ❌ Perlu update manual | ✅ Auto-learn dari data |
| **Interpretability** | ✅ Jelas (rule-based) | ⚠️ Black box |
| **Resource** | ✅ Ringan | ⚠️ Butuh GPU (optional) |
| **Best For** | MVP, Demo, Quick start | Production, High accuracy |

---

## 🎓 Training Tips

### 1. Dataset Quality

**DO**:
- ✅ Collect 500-1000+ samples per class
- ✅ Balance dataset (50% hoax, 50% non-hoax)
- ✅ Diverse sources
- ✅ Real-world examples

**DON'T**:
- ❌ Copy-paste same text
- ❌ Imbalanced dataset (95% non-hoax, 5% hoax)
- ❌ Low-quality text (incomplete, corrupt)
- ❌ Biased samples

### 2. Hyperparameter Tuning

Start with defaults:
```bash
python train_model.py --epochs 5 --batch-size 8
```

If underfitting (low accuracy):
- Increase epochs: `--epochs 10`
- Decrease learning rate
- Add more data

If overfitting (train acc high, val acc low):
- Decrease epochs
- Add dropout
- Add more validation data

### 3. Evaluation Metrics

Fokus pada:
- **F1 Score**: Balance precision & recall
- **Precision**: Berapa banyak prediksi "hoax" yang benar
- **Recall**: Berapa banyak hoax sebenarnya yang ter-detect

Target:
- F1 Score: > 0.85
- Precision: > 0.80
- Recall: > 0.80

---

## 📈 Dataset Sources

### Non-Hoax (Berita Valid)

**RSS Feeds** (Auto):
- Antara News: `https://www.antaranews.com/rss/terkini.xml`
- Kompas: `https://rss.kompas.com/nasional`
- Detik: `https://rss.detik.com/index.php/detikcom`
- Tempo: `https://www.tempo.co/rss/terkini`

### Hoax Samples (Manual/Scraping)

**Fact-Checking Sites**:
1. **Tempo Cek Fakta**
   - URL: https://cekfakta.tempo.co/
   - Label: Sesuai verifikasi mereka

2. **TurnBackHoax**
   - Twitter: @TurnBackHoax
   - Database hoax yang sudah terverifikasi

3. **Mafindo**
   - URL: https://www.mafindo.or.id/
   - Koleksi hoax Indonesia

4. **Liputan6 Cek Fakta**
   - URL: https://www.liputan6.com/cek-fakta
   - Verifikasi hoax dari tim Liputan6

---

## 🔧 Troubleshooting

### Error: "No samples collected"

**Solusi**:
- Check internet connection
- Verify RSS URLs masih aktif
- Increase timeout di `dataset_collector.py`

### Error: "CUDA out of memory"

**Solusi**:
```bash
# Reduce batch size
python train_model.py --batch-size 4
```

Atau train di CPU (lebih lambat):
```python
# train_model.py, line ~140
fp16=False  # Disable mixed precision
```

### Low Accuracy (<70%)

**Solusi**:
1. Collect more data (minimal 500 per class)
2. Check dataset balance
3. Review data quality
4. Increase epochs
5. Try different model: `--model cahya/bert-base-indonesian-522M`

---

## 📝 Example: Complete Workflow

```bash
# 1. Collect dataset
cd backend
python dataset_collector.py

# 2. Manually add hoax to hoax_samples.txt (copy dari TurnBackHoax, dll)

# 3. Load hoax samples
python dataset_collector.py --load-hoax

# 4. Review dataset
# Buka dataset.csv, pastikan ada >200 samples total

# 5. Train model
python train_model.py --epochs 5

# 6. Update .env
echo "USE_ML_MODEL=true" >> .env
echo "MODEL_NAME=./hoax_model" >> .env

# 7. Restart server
uvicorn app.main:app --reload

# 8. Test di frontend!
```

---

## 🎯 Next Steps

### Short-term
- [ ] Collect 500+ hoax samples
- [ ] Train initial model
- [ ] Evaluate & iterate
- [ ] Add more RSS sources

### Long-term
- [ ] Continuous learning pipeline
- [ ] A/B testing rule-based vs ML
- [ ] Multi-class classification (hoax types)
- [ ] Explainability (why hoax?)

---

## 📚 Resources

### Learning
- [Hugging Face Course](https://huggingface.co/course)
- [IndoBERT Paper](https://arxiv.org/abs/2009.05387)
- [Text Classification Tutorial](https://huggingface.co/docs/transformers/tasks/sequence_classification)

### Datasets
- [Indonesian Fake News Dataset](https://github.com/several/datasets)
- Research papers dengan Indonesian hoax datasets

### Tools
- [Weights & Biases](https://wandb.ai/) - Experiment tracking
- [TensorBoard](https://www.tensorflow.org/tensorboard) - Visualization

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
