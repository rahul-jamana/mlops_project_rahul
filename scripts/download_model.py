"""
Download trained model from S3
Usage: python scripts/download_model.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_utils import download_file
from src.utils.s3_config import MODEL_PATH, MODEL_KEY, S3_BUCKET

if __name__ == "__main__":
    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        download_file(S3_BUCKET, MODEL_KEY, MODEL_PATH)
        print(f"✓ Model downloaded successfully!")
    except Exception as e:
        print(f"✗ Error downloading from S3: {e}")
