"""
Combine multiple CSV datasets into one
"""

import pandas as pd
import glob
import sys
import os


def combine_csv_files(pattern, output="combined_dataset.csv"):
    """
    Combine multiple CSV files matching pattern

    Args:
        pattern: Glob pattern (e.g., "D:/datasets/*.csv")
        output: Output filename
    """
    print("=" * 60)
    print("Dataset Combiner")
    print("=" * 60)

    # Find files
    files = glob.glob(pattern)

    if not files:
        print(f"❌ No files found matching pattern: {pattern}")
        return

    print(f"✅ Found {len(files)} files:")
    for f in files:
        size = os.path.getsize(f) / 1024  # KB
        print(f"   - {f} ({size:.1f} KB)")

    # Read and combine
    df_list = []
    total_rows = 0

    for f in files:
        try:
            df = pd.read_csv(f)
            rows = len(df)
            total_rows += rows
            df_list.append(df)
            print(f"   ✅ Read {rows} rows from {os.path.basename(f)}")
        except Exception as e:
            print(f"   ❌ Error reading {f}: {e}")

    if not df_list:
        print("❌ No data loaded")
        return

    # Combine
    print("\n📊 Combining datasets...")
    combined = pd.concat(df_list, ignore_index=True)

    # Remove duplicates if any
    original_len = len(combined)
    combined = combined.drop_duplicates(subset=['text'], keep='first')
    duplicates_removed = original_len - len(combined)

    # Analysis
    print(f"\n📈 Combined Dataset Statistics:")
    print(f"   Total samples: {len(combined)}")
    print(f"   Duplicates removed: {duplicates_removed}")

    if 'label' in combined.columns:
        non_hoax = sum(combined['label'] == 0)
        hoax = sum(combined['label'] == 1)
        print(f"   Non-hoax: {non_hoax} ({non_hoax/len(combined)*100:.1f}%)")
        print(f"   Hoax: {hoax} ({hoax/len(combined)*100:.1f}%)")

    # Save
    combined.to_csv(output, index=False)
    print(f"\n✅ Combined dataset saved to: {output}")
    print(f"   File size: {os.path.getsize(output) / 1024:.1f} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python combine_datasets.py <pattern> [output]")
        print("\nExamples:")
        print("  python combine_datasets.py \"*.csv\"")
        print("  python combine_datasets.py \"D:/datasets/*.csv\" combined.csv")
        sys.exit(1)

    pattern = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "combined_dataset.csv"

    combine_csv_files(pattern, output)
