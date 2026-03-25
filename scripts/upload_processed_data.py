"""
Upload processed data to S3
Usage: python scripts/upload_processed_data.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_utils import upload_file
from src.utils.s3_config import PROCESSED_DATA_PATH, PROCESSED_DATA_KEY, S3_BUCKET

if __name__ == "__main__":
    try:
        upload_file(PROCESSED_DATA_PATH, S3_BUCKET, PROCESSED_DATA_KEY)
        print("[OK] Processed data uploaded successfully!")
    except FileNotFoundError:
        print(f"[ERROR] {PROCESSED_DATA_PATH} not found")
    except Exception as e:
        print(f"[ERROR] Error uploading to S3: {e}")
