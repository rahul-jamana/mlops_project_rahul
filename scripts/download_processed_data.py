"""
Download processed data from S3
Usage: python scripts/download_processed_data.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_utils import download_file
from src.utils.s3_config import PROCESSED_DATA_PATH, PROCESSED_DATA_KEY, S3_BUCKET

if __name__ == "__main__":
    try:
        os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
        download_file(S3_BUCKET, PROCESSED_DATA_KEY, PROCESSED_DATA_PATH)
        print(f"✓ Processed data downloaded successfully!")
    except Exception as e:
        print(f"✗ Error downloading from S3: {e}")
