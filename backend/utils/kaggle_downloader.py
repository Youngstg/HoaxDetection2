"""
Download dataset from Kaggle using API
"""

import os
import sys
import zipfile
import shutil


def download_kaggle_dataset(dataset_name, output_dir="./datasets/kaggle"):
    """
    Download dataset from Kaggle

    Args:
        dataset_name: Kaggle dataset (e.g., "username/dataset-name")
        output_dir: Where to extract files
    """
    print("=" * 60)
    print("Kaggle Dataset Downloader")
    print("=" * 60)

    # Check if kaggle is installed
    try:
        import kaggle
    except ImportError:
        print("❌ Kaggle library not found!")
        print("\nInstall with: pip install kaggle")
        print("\nThen setup API token:")
        print("1. Go to kaggle.com → Account → Create API Token")
        print("2. Save kaggle.json to ~/.kaggle/ (or C:\\Users\\YourName\\.kaggle\\)")
        return

    # Check API token
    kaggle_config = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_config):
        print(f"❌ Kaggle API token not found at: {kaggle_config}")
        print("\nSetup:")
        print("1. Go to kaggle.com → Account → Create API Token")
        print(f"2. Save kaggle.json to {kaggle_config}")
        return

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📥 Downloading: {dataset_name}")
    print(f"📁 Output directory: {output_dir}")

    try:
        # Download
        print("\n⏳ Downloading...")
        kaggle.api.dataset_download_files(
            dataset_name,
            path=output_dir,
            unzip=True
        )

        print(f"\n✅ Download complete!")

        # List files
        print(f"\n📂 Files in {output_dir}:")
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath) / 1024  # KB
                print(f"   - {file} ({size:.1f} KB)")

        print(f"\n📝 Next steps:")
        print(f"1. Check files in: {output_dir}")
        print(f"2. If CSV, use: python train_model.py --dataset {output_dir}/train.csv")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kaggle_downloader.py <dataset-name> [output-dir]")
        print("\nExamples:")
        print("  python kaggle_downloader.py username/dataset-name")
        print("  python kaggle_downloader.py username/dataset-name ./my_datasets")
        print("\nTo find datasets:")
        print("  kaggle datasets list -s \"indonesian fake news\"")
        sys.exit(1)

    dataset_name = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./datasets/kaggle"

    download_kaggle_dataset(dataset_name, output_dir)
