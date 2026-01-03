# Auto-Labeling Pipeline Guide

Panduan lengkap menggunakan auto-labeling untuk generate dataset hoax detection.

---

## 🎯 Konsep

**Auto-Labeling** = Menggunakan rule-based detector untuk otomatis melabeli data, kemudian data tersebut digunakan untuk training ML model.

```
┌─────────────┐
│ RSS Sources │ (Antara, Kompas, Detik, dll)
└──────┬──────┘
       │ scrape
       ▼
┌─────────────────┐
│ Text Extraction │ (BeautifulSoup)
└──────┬──────────┘
       │ extract
       ▼
┌──────────────────────┐
│ Rule-Based Labeling  │ (Auto-label hoax/non-hoax)
└──────┬───────────────┘
       │ confidence filter (≥0.6)
       ▼
┌─────────────────┐
│ Dataset (CSV)   │ (Ready for training)
└──────┬──────────┘
       │ train
       ▼
┌─────────────────┐
│ ML Model        │ (Fine-tuned IndoBERT)
└─────────────────┘
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Run Auto-Labeling Pipeline

```bash
python auto_labeling_pipeline.py
```

**Default behavior**:
- Scrape 50 articles per RSS source
- Filter dengan confidence ≥ 0.6
- Output: `auto_labeled_dataset.csv`

### Step 3: Review Quality

Buka `review_sample.csv` dan check apakah labeling sudah benar:

```csv
text,label,confidence,source,is_correct
"Presiden resmikan...",non-hoax,0.85,Kompas,yes
"WAJIB SHARE! Vaksin...",hoax,0.92,Unknown,yes
```

Tandai kolom `is_correct` dengan `yes` atau `no`.

### Step 4: Train Model

Jika quality check bagus (>80% correct):

```bash
python train_model.py --dataset auto_labeled_dataset.csv --epochs 5
```

### Step 5: Use Trained Model

Update `.env`:
```env
USE_ML_MODEL=true
MODEL_NAME=./hoax_model
```

Restart backend server!

---

## ⚙️ Configuration

### Confidence Threshold

Threshold menentukan kualitas vs kuantitas data:

| Threshold | Data Quality | Data Quantity | Use Case |
|-----------|-------------|---------------|----------|
| 0.9 | Sangat tinggi | Sangat sedikit | High-precision needed |
| 0.7 | Tinggi | Sedang | **Recommended** |
| 0.6 | Sedang | Banyak | Quick training |
| 0.5 | Rendah | Sangat banyak | Not recommended |

**Adjust threshold**:
```bash
python auto_labeling_pipeline.py --confidence 0.7
```

### Max Articles per Source

**Default**: 50 articles per RSS feed

**Adjust**:
```bash
python auto_labeling_pipeline.py --max-per-source 100
```

**Recommended**:
- Development/Testing: 20-50
- Training: 100-200
- Production: 500+

---

## 📊 Expected Results

### Good Dataset

```
📊 DATASET ANALYSIS
=================================================================
Total samples: 347
   Non-Hoax: 312 (89.9%)
   Hoax: 35 (10.1%)
Average confidence: 0.78

🔍 Quality Check:
   ✅ OK: Dataset size acceptable
   ⚠️  WARNING: Dataset imbalanced (difference >30%)
      Recommendation: Balance dataset atau use class weights
```

### What to Do

**If Imbalanced**:
1. Collect more hoax samples manually
2. Use class weights dalam training:
   ```bash
   python train_model.py --use-class-weights
   ```
3. Or use oversampling/undersampling

**If Too Small** (<200 samples):
1. Lower confidence threshold: `--confidence 0.5`
2. Add more RSS sources
3. Increase max per source: `--max-per-source 100`

---

## 🔧 Advanced Usage

### Add Custom RSS Sources

Edit `auto_labeling_pipeline.py`:

```python
self.rss_feeds = {
    "trusted": [
        {"url": "https://example.com/rss", "source": "Example News"},
        # Add more...
    ],
}
```

### Custom Confidence per Source

Untuk media super terpercaya, bisa lower threshold:

```python
# In scrape_rss_feed method
if source_name == "Kompas":
    threshold = 0.5  # Lower threshold for trusted source
else:
    threshold = self.confidence_threshold
```

### Batch Processing

Process multiple batches dengan different thresholds:

```bash
# High confidence (quality)
python auto_labeling_pipeline.py --confidence 0.8 --max-per-source 100

# Medium confidence (balance)
python auto_labeling_pipeline.py --confidence 0.6 --max-per-source 200

# Combine datasets
cat auto_labeled_dataset*.csv > combined_dataset.csv
```

---

## 🎓 Quality Assurance

### 1. Manual Review

**Always review** random sample (50-100 articles):

```python
pipeline.export_for_review(sample_size=100, filename="review.csv")
```

Calculate accuracy:
```
Correct predictions / Total reviewed
```

**Target**: >80% accuracy

### 2. Source Distribution

Check jika data didominasi satu source:

```
Distribution by source:
   Kompas: 180 samples  ← Good diversity
   Detik: 120 samples
   Antara: 47 samples
```

**Bad**:
```
Distribution by source:
   Kompas: 320 samples  ← Too dominant
   Others: 27 samples
```

### 3. Confidence Distribution

Analyze confidence scores:

```python
import pandas as pd

df = pd.read_csv('auto_labeled_dataset.csv')
print(df['confidence'].describe())
```

**Good**:
```
mean    0.78
std     0.12
min     0.60
25%     0.70
50%     0.78
75%     0.87
max     0.95
```

High mean + low std = consistent labeling

---

## ⚠️ Limitations

### 1. Label Noise

Rule-based detector bisa salah → ML model belajar dari kesalahan

**Mitigasi**:
- High confidence threshold
- Manual review sample
- Iterative improvement

### 2. Bias Propagation

ML model inherit bias dari rule-based

**Example**:
- Rule: Semua dari Kompas.com = non-hoax
- ML learn: Domain = Kompas → non-hoax
- Problem: Jika ada hoax dari Kompas, ML bias

**Mitigasi**:
- Diverse sources
- Don't rely only on source domain
- Add negative examples

### 3. Distribution Shift

Training data != Real-world data

**Example**:
- Training: 90% Kompas (formal language)
- Real-world: Social media (informal language)
- Result: Poor performance on social media text

**Mitigasi**:
- Collect diverse data
- Include social media text
- Regular retraining

---

## 🔄 Iterative Improvement

### Iteration 1: Bootstrap

```bash
# Quick start dengan low threshold
python auto_labeling_pipeline.py --confidence 0.5 --max-per-source 50
python train_model.py --dataset auto_labeled_dataset.csv --epochs 3
```

Result: Baseline model (accuracy ~70%)

### Iteration 2: Quality

```bash
# Higher threshold, more data
python auto_labeling_pipeline.py --confidence 0.7 --max-per-source 100
python train_model.py --dataset auto_labeled_dataset.csv --epochs 5
```

Result: Better model (accuracy ~75-80%)

### Iteration 3: Refinement

```bash
# Manual review & correction
# Edit dataset, remove bad samples
# Add manual hoax samples
python train_model.py --dataset curated_dataset.csv --epochs 10
```

Result: Production model (accuracy ~85-90%)

---

## 📈 Performance Expectations

| Dataset Size | Confidence | Expected Accuracy | Training Time |
|-------------|-----------|-------------------|---------------|
| 200 | 0.6 | 70-75% | 5-10 min |
| 500 | 0.7 | 75-80% | 10-20 min |
| 1000 | 0.7 | 80-85% | 20-40 min |
| 2000+ | 0.8 | 85-90% | 40-60 min |

*Assuming GPU available. CPU training 5-10x slower.

---

## 💡 Tips & Tricks

### Tip 1: Start Small

```bash
# Test with small dataset first
python auto_labeling_pipeline.py --max-per-source 10
# Review quality
# If good, scale up
python auto_labeling_pipeline.py --max-per-source 100
```

### Tip 2: Monitor Progress

Use `tqdm` progress bars (already included):
```
📰 Fetching: Kompas
Processing: 100%|████████████| 50/50 [02:30<00:00,  3.00s/it]
   ✅ Collected: 42 articles (confidence >= 0.6)
```

### Tip 3: Incremental Collection

Collect data incrementally:

```bash
# Day 1
python auto_labeling_pipeline.py --max-per-source 50
mv auto_labeled_dataset.csv dataset_day1.csv

# Day 2
python auto_labeling_pipeline.py --max-per-source 50
mv auto_labeled_dataset.csv dataset_day2.csv

# Combine
cat dataset_day*.csv > combined.csv
```

### Tip 4: A/B Testing

Train 2 models, compare:

```bash
# Model A: Auto-labeled
python train_model.py --dataset auto_labeled.csv --output modelA

# Model B: Manual + Auto
python train_model.py --dataset combined.csv --output modelB

# Compare evaluation metrics
```

---

## 🐛 Troubleshooting

### Error: "No samples collected"

**Cause**: All articles filtered out (low confidence)

**Solution**:
```bash
# Lower threshold
python auto_labeling_pipeline.py --confidence 0.4
```

### Error: "RSS feed timeout"

**Cause**: Network issue or feed down

**Solution**:
- Check internet connection
- Verify RSS URL still active
- Increase timeout in code

### Warning: "Dataset imbalanced"

**Cause**: Too many non-hoax, too few hoax

**Solution**:
1. Manual hoax collection
2. Use class weights: `--use-class-weights`
3. Oversample minority class

---

## 📚 References

### Academic Papers
- **"Snorkel: Rapid Training Data Creation with Weak Supervision"** (Stanford, 2017)
- **"Learning from Noisy Labels with Deep Neural Networks"** (Various)

### Tutorials
- [Weak Supervision Tutorial](https://www.snorkel.org/get-started/)
- [Active Learning Guide](https://modal-python.readthedocs.io/)

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
