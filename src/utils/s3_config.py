import os

# S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET", "mlops-student")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# S3 Paths (keys in bucket)
RAW_DATA_KEY = "data/raw/student_scores.csv"
NEW_RAW_DATA_KEY = "data/raw/new_student_scores.csv"
PROCESSED_DATA_KEY = "data/processed/train.csv"
MODEL_KEY = "models/model_latest.pkl"
MODEL_META_KEY = "models/model_meta.json"

# Local Paths
RAW_DATA_PATH = "data/raw/student_scores.csv"
PROCESSED_DATA_PATH = "data/processed/train.csv"
MODEL_PATH = "models/model_latest.pkl"
MODEL_META_PATH = "models/model_meta.json"
