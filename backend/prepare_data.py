"""Simple data preparation - no fancy preprocessing"""
import pandas as pd

# Load
df = pd.read_csv("../Data_latih.csv")
print(f"Loaded {len(df)} samples")

# Combine text
df['text'] = df['judul'].fillna('') + '. ' + df['narasi'].fillna('')

# Check labels
unique_labels = sorted(df['label'].unique())
print(f"Labels: {unique_labels}")

# Convert if needed (1/2 -> 0/1)
if set(unique_labels) == {1, 2}:
    df['label'] = df['label'] - 1
    print("Converted 1/2 to 0/1")

# Save
df[['text', 'label']].to_csv("dataset.csv", index=False)
print(f"Saved dataset.csv: {len(df)} samples")
print(f"Label 0: {sum(df['label']==0)}, Label 1: {sum(df['label']==1)}")
