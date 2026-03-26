"""
Upload all files (raw data, processed data, model) to S3
Usage: python scripts/upload_all.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_utils import upload_file
from src.utils.s3_config import (
    RAW_DATA_PATH,
    RAW_DATA_KEY,
    PROCESSED_DATA_PATH,
    PROCESSED_DATA_KEY,
    MODEL_PATH,
    MODEL_KEY,
    S3_BUCKET,
)


def upload_all():
    files_to_upload = [
        (RAW_DATA_PATH, RAW_DATA_KEY, "Raw Data"),
        (PROCESSED_DATA_PATH, PROCESSED_DATA_KEY, "Processed Data"),
        (MODEL_PATH, MODEL_KEY, "Model"),
    ]

    print("=" * 60)
    print("Uploading all files to S3...")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for local_path, s3_key, name in files_to_upload:
        try:
            if not os.path.exists(local_path):
                print(f"[SKIP] {name}: {local_path} not found (skipping)")
                failed_count += 1
                continue

            upload_file(local_path, S3_BUCKET, s3_key)
            print(f"[OK] {name}: Uploaded successfully")
            success_count += 1
        except Exception as e:
            print(f"[ERROR] {name}: Error - {e}")
            failed_count += 1

    print("=" * 60)
    print(f"Upload Summary: {success_count} succeeded, {failed_count} failed")
    print("=" * 60)

    return failed_count == 0


if __name__ == "__main__":
    success = upload_all()
    sys.exit(0 if success else 1)
