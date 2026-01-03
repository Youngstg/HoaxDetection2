"""
Quick Training Script - Langsung train dari Data_latih.csv
Tanpa proses converter yang ribet!
"""

import pandas as pd
import sys

print("="*70)
print("🚀 QUICK TRAIN - Indonesia False News Dataset")
print("="*70)

# 1. Load data
print("\n📂 Loading Data_latih.csv...")
df = pd.read_csv("../Data_latih.csv")

print(f"   ✅ Loaded {len(df)} samples")
print(f"\n📋 Columns: {list(df.columns)}")

# 2. Combine judul + narasi
print(f"\n🔄 Processing data...")
df['text'] = df['judul'].fillna('') + '. ' + df['narasi'].fillna('')

# 3. Check labels
print(f"\n📊 Label distribution:")
print(df['label'].value_counts())

# Map labels: 1 → 1 (hoax), 0 → 0 (non-hoax)
# atau jika label 1/2, convert ke 0/1
unique_labels = sorted(df['label'].unique())
print(f"\n🏷️  Unique labels: {unique_labels}")

if set(unique_labels) == {1, 2}:
    print("   Converting labels 1/2 → 0/1")
    df['label'] = df['label'] - 1
elif 0 not in unique_labels:
    # Jika hanya ada 1 label, assume 1=hoax, create some non-hoax samples
    print("   ⚠️  WARNING: Only one label found!")
    print("   Assuming label=1 is HOAX")
    df['label'] = 1  # All are hoax

# 4. Select columns
df_final = df[['text', 'label']].copy()

# Remove empty
df_final = df_final[df_final['text'].str.strip() != '']

print(f"\n✅ Final dataset:")
print(f"   Total: {len(df_final)} samples")
print(f"   Label 0: {sum(df_final['label']==0)}")
print(f"   Label 1: {sum(df_final['label']==1)}")

# 5. Save
output = "dataset.csv"
df_final.to_csv(output, index=False)
print(f"\n💾 Saved to: {output}")

# 6. Preview
print(f"\n👀 Preview:")
print(df_final.head(3))

print("\n" + "="*70)
print("✅ Dataset ready for training!")
print("\n📝 Run training:")
print("   python train_model.py --dataset dataset.csv --epochs 5")
print("="*70)
