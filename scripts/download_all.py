"""
Download all files (raw data, processed data, model) from S3
Usage: python scripts/download_all.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_utils import download_file
from src.utils.s3_config import (
    RAW_DATA_PATH, RAW_DATA_KEY,
    PROCESSED_DATA_PATH, PROCESSED_DATA_KEY,
    MODEL_PATH, MODEL_KEY,
    S3_BUCKET
)

def download_all():
    files_to_download = [
        (S3_BUCKET, RAW_DATA_KEY, RAW_DATA_PATH, "Raw Data"),
        (S3_BUCKET, PROCESSED_DATA_KEY, PROCESSED_DATA_PATH, "Processed Data"),
        (S3_BUCKET, MODEL_KEY, MODEL_PATH, "Model"),
    ]

    print("=" * 60)
    print("Downloading all files from S3...")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for bucket, s3_key, local_path, name in files_to_download:
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            download_file(bucket, s3_key, local_path)
            print(f"✓ {name}: Downloaded successfully")
            success_count += 1
        except Exception as e:
            print(f"✗ {name}: Error - {e}")
            failed_count += 1

    print("=" * 60)
    print(f"Download Summary: {success_count} succeeded, {failed_count} failed")
    print("=" * 60)

    return failed_count == 0

if __name__ == "__main__":
    success = download_all()
    sys.exit(0 if success else 1)
