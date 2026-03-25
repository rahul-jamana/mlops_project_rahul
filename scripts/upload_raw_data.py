"""
Upload raw data to S3
Usage: python scripts/upload_raw_data.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_utils import upload_file
from src.utils.s3_config import RAW_DATA_PATH, RAW_DATA_KEY, NEW_RAW_DATA_KEY, S3_BUCKET

if __name__ == "__main__":
    try:
        # Upload canonical dataset file
        upload_file(RAW_DATA_PATH, S3_BUCKET, RAW_DATA_KEY)
        print("[OK] Raw data uploaded successfully to RAW_DATA_KEY")

        # Upload same or new data key for audit / versioning
        upload_file(RAW_DATA_PATH, S3_BUCKET, NEW_RAW_DATA_KEY)
        print("[OK] Raw data uploaded successfully to NEW_RAW_DATA_KEY")

    except FileNotFoundError:
        print(f"[ERROR] {RAW_DATA_PATH} not found")
    except Exception as e:
        print(f"[ERROR] Error uploading to S3: {e}")
