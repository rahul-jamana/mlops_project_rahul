"""
Verify what files are in S3
Usage: python scripts/verify_s3_files.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_utils import get_s3_client
from src.utils.s3_config import S3_BUCKET, RAW_DATA_KEY, PROCESSED_DATA_KEY, MODEL_KEY

def verify_s3_files():
    """Check which files exist in S3"""
    s3 = get_s3_client()

    print(f"\n{'='*60}")
    print(f"S3 BUCKET CONTENTS: {S3_BUCKET}")
    print(f"{'='*60}\n")

    files_to_check = [
        (RAW_DATA_KEY, "Raw Data"),
        (PROCESSED_DATA_KEY, "Processed Data"),
        (MODEL_KEY, "Trained Model"),
    ]

    found_count = 0
    missing_count = 0

    try:
        for s3_key, name in files_to_check:
            try:
                obj = s3.head_object(Bucket=S3_BUCKET, Key=s3_key)
                size_mb = obj['ContentLength'] / (1024 * 1024)
                print(f"[OK] {name}")
                print(f"     Path: s3://{S3_BUCKET}/{s3_key}")
                print(f"     Size: {size_mb:.2f} MB")
                print(f"     Modified: {obj['LastModified']}\n")
                found_count += 1
            except s3.exceptions.NoSuchKey:
                print(f"[MISSING] {name}")
                print(f"     Path: s3://{S3_BUCKET}/{s3_key}\n")
                missing_count += 1

        print(f"{'='*60}")
        print(f"SUMMARY: {found_count} found, {missing_count} missing")
        print(f"{'='*60}\n")

        return missing_count == 0

    except Exception as e:
        print(f"[ERROR] Could not connect to S3: {e}")
        print("Check AWS credentials and bucket name")
        return False

if __name__ == "__main__":
    verify_s3_files()
