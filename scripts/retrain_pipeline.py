"""
Complete Retraining Pipeline with S3
1. Upload new raw data to S3
2. Download raw data locally
3. Preprocess data
4. Upload processed data to S3
5. Train model (auto-uploads)
6. Verify everything in S3

Usage: python scripts/retrain_pipeline.py
"""

import os
import sys
import subprocess


def run_command(cmd, description):
    """Run a command in myenv and report status"""
    print(f"\n{'='*60}")
    print(f"[STEP] {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}\n")

    # Use conda run to execute in myenv
    result = subprocess.run(f"conda run -n myenv {cmd}", shell=True)

    if result.returncode == 0:
        print(f"[OK] {description} completed successfully!")
        return True
    else:
        print(f"[ERROR] {description} failed!")
        return False


def retrain_pipeline():
    """Complete retraining pipeline"""

    print("\n" + "=" * 60)
    print("COMPLETE RETRAINING PIPELINE WITH S3")
    print("=" * 60)

    steps = [
        ("python scripts/upload_raw_data.py", "1. Upload new raw data to S3"),
        ("python src/data/preprocess.py", "2. Preprocess data locally"),
        ("python scripts/upload_processed_data.py", "3. Upload processed data to S3"),
        ("python src/model/train.py", "4. Train model (auto-uploads to S3)"),
        ("python scripts/verify_s3_files.py", "5. Verify all files in S3"),
    ]

    completed = 0
    failed = 0

    for cmd, description in steps:
        if run_command(cmd, description):
            completed += 1
        else:
            failed += 1
            print(f"[SKIP] Skipping remaining steps due to error")
            break

    print(f"\n{'='*60}")
    print(f"PIPELINE SUMMARY: {completed} completed, {failed} failed")
    print(f"{'='*60}\n")

    if failed == 0:
        print("✓ All steps completed successfully!")
        print("\nYour S3 bucket now contains:")
        print("  - New raw data")
        print("  - New processed data")
        print("  - Newly trained model")
        return True
    else:
        print("✗ Pipeline failed. Check errors above.")
        return False


if __name__ == "__main__":
    success = retrain_pipeline()
    sys.exit(0 if success else 1)
