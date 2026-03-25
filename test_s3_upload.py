import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.utils.s3_utils import upload_file
from src.utils.s3_config import S3_BUCKET, RAW_DATA_PATH, NEW_RAW_DATA_KEY, MODEL_PATH, MODEL_KEY

print("=" * 60)
print("S3 Upload Test")
print("=" * 60)

# Test 1: Upload raw data
print(f"\nTest 1: Upload raw data to S3")
print(f"  Bucket: {S3_BUCKET}")
print(f"  File: {RAW_DATA_PATH}")
print(f"  S3 Key: {NEW_RAW_DATA_KEY}")

try:
    if os.path.exists(RAW_DATA_PATH):
        print(f"  File exists: YES ({os.path.getsize(RAW_DATA_PATH)} bytes)")
        upload_file(RAW_DATA_PATH, S3_BUCKET, NEW_RAW_DATA_KEY)
        print(f"  Result: SUCCESS ✓")
    else:
        print(f"  File exists: NO")
        print(f"  Result: FAILED - File not found")
except Exception as e:
    print(f"  Result: FAILED")
    print(f"  Error: {type(e).__name__}: {e}")

# Test 2: Upload model
print(f"\nTest 2: Upload model to S3")
print(f"  Bucket: {S3_BUCKET}")
print(f"  File: {MODEL_PATH}")
print(f"  S3 Key: {MODEL_KEY}")

try:
    if os.path.exists(MODEL_PATH):
        print(f"  File exists: YES ({os.path.getsize(MODEL_PATH)} bytes)")
        upload_file(MODEL_PATH, S3_BUCKET, MODEL_KEY)
        print(f"  Result: SUCCESS ✓")
    else:
        print(f"  File exists: NO")
        print(f"  Result: FAILED - File not found")
except Exception as e:
    print(f"  Result: FAILED")
    print(f"  Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
