"""
Convert Indonesia False News Kaggle Dataset to Training Format

Dataset: https://www.kaggle.com/datasets/muhammadghazimuharam/indonesiafalsenews
Files: Data_latih.csv, Data_uji.csv
"""

import pandas as pd
import os
import sys


def convert_indonesia_false_news(train_path, test_path=None, output_path="dataset.csv"):
    """
    Convert Kaggle Indonesia False News dataset to training format

    Args:
        train_path: Path to Data_latih.csv
        test_path: Path to Data_uji.csv (optional)
        output_path: Output CSV path
    """
    print("=" * 70)
    print("Indonesia False News Dataset Converter")
    print("=" * 70)

    # Load training data
    print(f"\n📂 Loading training data: {train_path}")

    if not os.path.exists(train_path):
        print(f"❌ File not found: {train_path}")
        return

    df_train = pd.read_csv(train_path)

    print(f"   ✅ Loaded {len(df_train)} rows")
    print(f"\n📋 Columns: {list(df_train.columns)}")
    print(f"\n📊 First few rows:")
    print(df_train.head())

    # Check label distribution
    print(f"\n📈 Label distribution:")
    print(df_train['label'].value_counts())

    # Combine judul + narasi as text
    print(f"\n🔄 Combining 'judul' and 'narasi' columns...")
    df_train['text'] = df_train['judul'].fillna('') + '. ' + df_train['narasi'].fillna('')

    # Map labels
    # Check if labels are 0/1 or 1/2
    unique_labels = df_train['label'].unique()
    print(f"\n🏷️  Unique labels: {unique_labels}")

    if set(unique_labels).issubset({0, 1}):
        print("   Labels are already 0/1 (perfect!)")
        # Assuming 0=non-hoax, 1=hoax
    elif set(unique_labels).issubset({1, 2}):
        print("   Labels are 1/2, converting to 0/1...")
        # Assuming 1=non-hoax, 2=hoax → convert to 0/1
        df_train['label'] = df_train['label'] - 1
    else:
        print(f"   ⚠️  Unexpected labels: {unique_labels}")
        print("   Assuming first unique value = non-hoax (0)")
        label_map = {unique_labels[0]: 0, unique_labels[1]: 1}
        df_train['label'] = df_train['label'].map(label_map)

    # Select relevant columns
    df_converted = df_train[['text', 'label']].copy()

    # Remove empty texts
    original_len = len(df_converted)
    df_converted = df_converted[df_converted['text'].str.strip() != '']
    removed = original_len - len(df_converted)

    if removed > 0:
        print(f"   ⚠️  Removed {removed} rows with empty text")

    # Load test data if provided
    if test_path and os.path.exists(test_path):
        print(f"\n📂 Loading test data: {test_path}")
        df_test = pd.read_csv(test_path)
        print(f"   ✅ Loaded {len(df_test)} rows")

        # Note: test data might not have labels
        if 'label' not in df_test.columns:
            print("   ⚠️  Test data doesn't have labels (this is normal for test sets)")
            print("   Skipping test data (we'll only use training data)")
        else:
            # Same conversion for test data
            df_test['text'] = df_test['judul'].fillna('') + '. ' + df_test['narasi'].fillna('')

            if set(df_test['label'].unique()).issubset({1, 2}):
                df_test['label'] = df_test['label'] - 1

            df_test_converted = df_test[['text', 'label']].copy()
            df_test_converted = df_test_converted[df_test_converted['text'].str.strip() != '']

            # Combine train + test
            df_converted = pd.concat([df_converted, df_test_converted], ignore_index=True)
            print(f"   ✅ Combined with test data")

    # Final statistics
    print(f"\n📊 Converted Dataset Statistics:")
    print(f"   Total samples: {len(df_converted)}")

    non_hoax = sum(df_converted['label'] == 0)
    hoax = sum(df_converted['label'] == 1)

    print(f"   Non-hoax (label=0): {non_hoax} ({non_hoax/len(df_converted)*100:.1f}%)")
    print(f"   Hoax (label=1): {hoax} ({hoax/len(df_converted)*100:.1f}%)")

    # Check balance
    if abs(non_hoax - hoax) / len(df_converted) > 0.3:
        print(f"\n   ⚠️  WARNING: Dataset imbalanced")
        print(f"      Difference: {abs(non_hoax - hoax)} samples")
        print(f"      Consider using class weights in training")

    # Save
    df_converted.to_csv(output_path, index=False)
    print(f"\n✅ Converted dataset saved to: {output_path}")

    # Preview
    print(f"\n👀 Preview (first 3 samples):")
    print("-" * 70)
    for idx, row in df_converted.head(3).iterrows():
        label_text = "HOAX" if row['label'] == 1 else "NON-HOAX"
        print(f"\n[{label_text}] {row['text'][:150]}...")
    print("-" * 70)

    print(f"\n📝 Next steps:")
    print(f"1. Review the converted dataset: {output_path}")
    print(f"2. Train model:")
    print(f"   python train_model.py --dataset {output_path} --epochs 5")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_kaggle_dataset.py <Data_latih.csv> [Data_uji.csv] [output.csv]")
        print("\nExamples:")
        print("  python convert_kaggle_dataset.py Data_latih.csv")
        print("  python convert_kaggle_dataset.py Data_latih.csv Data_uji.csv")
        print("  python convert_kaggle_dataset.py Data_latih.csv Data_uji.csv my_dataset.csv")

        # Check if files exist in current directory
        if os.path.exists("Data_latih.csv"):
            print("\n✅ Found Data_latih.csv in current directory!")
            print("   Running auto-conversion...")
            test_path = "Data_uji.csv" if os.path.exists("Data_uji.csv") else None
            convert_indonesia_false_news("Data_latih.csv", test_path, "dataset.csv")
        else:
            print("\n❌ Data_latih.csv not found in current directory")
        sys.exit(0)

    train_path = sys.argv[1]
    test_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else "dataset.csv"

    convert_indonesia_false_news(train_path, test_path, output_path)
