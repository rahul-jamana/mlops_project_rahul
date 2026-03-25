"""
Handle new data arrival and trigger retraining
Two modes:
1. APPEND: Add new data to existing data
2. REPLACE: Replace old data with new data

Usage examples:
  python scripts/handle_new_data.py --mode replace --file data/raw/new_data.csv
  python scripts/handle_new_data.py --mode append --file data/raw/new_data.csv
"""

import os
import sys
import argparse
import subprocess
import pandas as pd
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.utils.s3_utils import upload_file
from src.utils.s3_config import S3_BUCKET, NEW_RAW_DATA_KEY


def append_data(existing_file, new_file, output_file):
    """Append new data to existing data"""
    print(f"\n[MODE] APPEND: Combining existing + new data")
    print(f"{'='*60}")

    try:
        # Read both files
        existing_df = pd.read_csv(existing_file)
        new_df = pd.read_csv(new_file)

        print(f"Existing data: {len(existing_df)} records")
        print(f"New data: {len(new_df)} records")

        # Combine
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates()  # Remove duplicates

        # Save
        combined_df.to_csv(output_file, index=False)

        print(f"Combined data: {len(combined_df)} records (duplicates removed)")
        print(f"Saved to: {output_file}")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to append data: {e}")
        return False

def replace_data(old_file, new_file, backup=True):
    """Replace old data with new data (with backup)"""
    print(f"\n[MODE] REPLACE: Replacing old data with new data")
    print(f"{'='*60}")

    try:
        # Create backup of old data
        if backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{old_file}.backup_{timestamp}"
            os.rename(old_file, backup_file)
            print(f"Backup created: {backup_file}")

        # Replace with new data
        new_df = pd.read_csv(new_file)
        new_df.to_csv(old_file, index=False)

        print(f"New data: {len(new_df)} records")
        print(f"Replaced: {old_file}")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to replace data: {e}")
        return False


def get_combined_df(mode, new_file, output_file):
    """Compute what combined data would look like (no side effects)."""
    if mode == "append":
        existing_df = pd.read_csv(output_file) if os.path.exists(output_file) else pd.DataFrame()
        new_df = pd.read_csv(new_file)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates()
        return combined_df

    return pd.read_csv(new_file)


def run_retrain_if_needed(row_count, dry_run=False, threshold=21):
    print(f"[INFO] Current data row count: {row_count}")

    if row_count < threshold:
        print(f"[INFO] Row count < {threshold}, skipping retraining.")
        return True

    print(f"[INFO] Row count >= {threshold}, retraining required.")

    if dry_run:
        print("[DRY RUN] Would run: python scripts/retrain_pipeline.py")
        return True

    result = subprocess.run([sys.executable, "scripts/retrain_pipeline.py"], check=False)
    if result.returncode == 0:
        print("[OK] Retraining pipeline completed successfully.")
        return True

    print(f"[ERROR] Retraining pipeline failed with exit code {result.returncode}.")
    return False


def main():
    parser = argparse.ArgumentParser(description="Handle new data and trigger retraining")
    parser.add_argument("--mode", choices=["append", "replace"], default="replace",
                       help="How to handle new data (append or replace)")
    parser.add_argument("--file", required=True, help="Path to new data file")
    parser.add_argument("--output", default="data/raw/student_scores.csv",
                       help="Output file path (default: data/raw/student_scores.csv)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Do not modify files or run retrain; show what would happen")
    parser.add_argument("--repeat", type=int, default=1,
                       help="Repeat the workflow N times (for testing/dry-run)")

    args = parser.parse_args()

    new_file = args.file
    output_file = args.output
    dry_run = args.dry_run
    repeat = max(1, args.repeat)

    # Validate new file exists
    if not os.path.exists(new_file):
        print(f"[ERROR] New data file not found: {new_file}")
        return False

    if dry_run:
        print("\n[DRY RUN] Running in dry-run mode. No file changes will be persisted.")

    success = True
    for attempt in range(1, repeat + 1):
        print(f"\n{'='*60}")
        print(f"RUN {attempt}/{repeat} (mode={args.mode}, dry-run={dry_run})")
        print(f"{'='*60}")

        if dry_run:
            # Skip file writes on dry run
            if args.mode == "append":
                existing_df = pd.read_csv(output_file) if os.path.exists(output_file) else pd.DataFrame()
                new_df = pd.read_csv(new_file)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates()
                print(f"[DRY RUN] Existing data rows: {len(existing_df)}, new data rows: {len(new_df)}")
                print(f"[DRY RUN] Combined data rows (dedup): {len(combined_df)}")
            else:
                combined_df = pd.read_csv(new_file)
                print(f"[DRY RUN] Replace mode - new data rows: {len(combined_df)}")

            print(f"[DRY RUN] Would upload combined raw data to S3: s3://{S3_BUCKET}/{NEW_RAW_DATA_KEY}")
            if not run_retrain_if_needed(len(combined_df), dry_run=True):
                success = False
                break

            continue

        # Actual run (non-dry-run)
        if args.mode == "append":
            if os.path.exists(output_file):
                step_ok = append_data(output_file, new_file, output_file)
            else:
                print(f"[INFO] Output file doesn't exist, creating it...")
                new_df = pd.read_csv(new_file)
                new_df.to_csv(output_file, index=False)
                step_ok = True
        else:  # replace
            if os.path.exists(output_file):
                step_ok = replace_data(output_file, new_file, backup=True)
            else:
                print(f"[INFO] Output file doesn't exist, copying new data...")
                new_df = pd.read_csv(new_file)
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                new_df.to_csv(output_file, index=False)
                step_ok = True

        if not step_ok:
            print(f"[ERROR] Data handling failed on attempt {attempt}")
            success = False
            break

        combined_df = pd.read_csv(output_file)

        # Ensure dedupe if repeated data arrives
        combined_df = combined_df.drop_duplicates().reset_index(drop=True)
        combined_df.to_csv(output_file, index=False)

        try:
            upload_file(output_file, S3_BUCKET, NEW_RAW_DATA_KEY)
            print(f"[OK] Uploaded new raw data snapshot to S3: s3://{S3_BUCKET}/{NEW_RAW_DATA_KEY}")
        except Exception as e:
            print(f"[WARNING] Could not upload combined raw data to S3: {e}")

        if not run_retrain_if_needed(len(combined_df), dry_run=False):
            success = False
            break

    if success:
        print(f"\nNext steps:")
        print(f"  1. python scripts/upload_raw_data.py        (upload to S3)")
        print(f"  2. python src/data/preprocess.py            (preprocess)")
        print(f"  3. python scripts/upload_processed_data.py  (upload processed)")
        print(f"  4. python src/model/train.py                (retrain & upload model)")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
