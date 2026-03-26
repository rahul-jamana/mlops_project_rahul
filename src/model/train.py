import sys
import os
import json
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Add parent directory to path to allow imports when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.s3_utils import upload_file, download_file
from src.utils.s3_config import (
    MODEL_PATH,
    MODEL_KEY,
    MODEL_META_PATH,
    MODEL_META_KEY,
    PROCESSED_DATA_PATH,
    S3_BUCKET,
)


def load_existing_model():
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"[WARNING] Could not load existing model: {e}")
        return None


def evaluate(model, X, y):
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    return float(mse), float(r2)


def save_model_meta(mse, r2, version):
    meta = {
        "model_version": version,
        "mse": mse,
        "r2": r2,
    }
    os.makedirs(os.path.dirname(MODEL_META_PATH), exist_ok=True)
    with open(MODEL_META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    # Upload metadata to S3
    try:
        upload_file(MODEL_META_PATH, S3_BUCKET, MODEL_META_KEY)
        print(f"[OK] Model metadata uploaded to S3: s3://{S3_BUCKET}/{MODEL_META_KEY}")
    except Exception as e:
        print(f"[WARNING] Could not upload model metadata: {e}")


def train():
    df = pd.read_csv(PROCESSED_DATA_PATH)

    if df.empty:
        raise ValueError("Processed data is empty. Run preprocessing first.")

    X = df[["Hours", "hours_squared"]]
    y = df["Scores"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())])

    pipeline.fit(X_train, y_train)

    new_mse, new_r2 = evaluate(pipeline, X_test, y_test)
    print(f"[INFO] New model mse={new_mse:.5f}, r2={new_r2:.5f}")

    # Download existing model metadata from S3 if available
    try:
        download_file(S3_BUCKET, MODEL_META_KEY, MODEL_META_PATH)
    except Exception:
        print(
            "[INFO] No existing model metadata on S3, first deployment or no prior metadata."
        )

    # Evaluate old model if available
    old_model = load_existing_model()
    old_mse, old_r2 = None, None

    if old_model is not None:
        try:
            old_mse, old_r2 = evaluate(old_model, X_test, y_test)
            print(f"[INFO] Old model mse={old_mse:.5f}, r2={old_r2:.5f}")
        except Exception as e:
            print(f"[WARNING] Old model evaluation failed: {e}")

    # Determine model promotion
    promote = False
    if old_mse is None:
        promote = True
        version = "v1"
    elif new_mse <= old_mse:
        promote = True
        version = "v{:.0f}".format(
            (float(old_r2 or 0) + 1) if old_r2 is not None else 1
        )
    else:
        promote = False
        version = "older"

    if promote:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(pipeline, MODEL_PATH)
        print(f"[OK] Promoted new model to {MODEL_PATH}")

        save_model_meta(new_mse, new_r2, version)

        try:
            upload_file(MODEL_PATH, S3_BUCKET, MODEL_KEY)
            print(f"[OK] Model uploaded to S3: s3://{S3_BUCKET}/{MODEL_KEY}")
        except Exception as e:
            print(f"[WARNING] Could not upload model to S3: {e}")

    else:
        print("[INFO] New model did not beat old model; old model stays deployed.")

    return {
        "promoted": promote,
        "new_mse": new_mse,
        "new_r2": new_r2,
        "old_mse": old_mse,
        "old_r2": old_r2,
    }


if __name__ == "__main__":
    stats = train()
    print(f"[SUMMARY] {stats}")
