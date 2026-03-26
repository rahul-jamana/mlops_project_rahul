from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.s3_utils import download_file
from src.utils.s3_config import (
    MODEL_PATH,
    MODEL_KEY,
    MODEL_META_PATH,
    MODEL_META_KEY,
    S3_BUCKET,
)

# Create FastAPI app with detailed information
app = FastAPI(
    title="Student Score Prediction API",
    description="Machine Learning API to predict student scores based on study hours. Uses a trained regression model deployed with AWS S3 integration.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Request model with validation
class PredictionRequest(BaseModel):
    hours: float = Field(
        ...,
        ge=0,
        le=24,
        title="Study Hours",
        description="Number of hours studied (0-24)",
        example=5.0,
    )


# Response model
class PredictionResponse(BaseModel):
    hours: float = Field(..., title="Study Hours", description="Input study hours")
    predicted_score: float = Field(
        ..., title="Predicted Score", description="Model's predicted student score"
    )
    model_version: str = Field(
        ..., title="Model Version", description="Version of the model used"
    )


class HealthResponse(BaseModel):
    status: str = Field(..., title="Status", description="API health status")
    model: str = Field(..., title="Model Status", description="Model loading status")
    s3_bucket: str = Field(
        ..., title="S3 Bucket", description="S3 bucket used for model storage"
    )


def load_model():
    """Load model and metadata from S3 if available, otherwise use local files"""
    model = None
    model_version = "unknown"

    try:
        print(f"[INFO] Downloading model from S3: s3://{S3_BUCKET}/{MODEL_KEY}")
        download_file(S3_BUCKET, MODEL_KEY, MODEL_PATH)
        print(f"[OK] Model downloaded from S3")
    except Exception as e:
        print(f"[WARNING] Could not download model from S3: {e}")
        print(f"[INFO] Using local model: {MODEL_PATH}")

    try:
        print(
            f"[INFO] Downloading model metadata from S3: s3://{S3_BUCKET}/{MODEL_META_KEY}"
        )
        download_file(S3_BUCKET, MODEL_META_KEY, MODEL_META_PATH)
    except Exception as e:
        print(f"[WARNING] Could not download model metadata from S3: {e}")

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)
    if os.path.exists(MODEL_META_PATH):
        try:
            with open(MODEL_META_PATH) as f:
                meta = json.load(f)
                model_version = meta.get("model_version", "unknown")
        except Exception:
            pass

    print(f"[OK] Model loaded successfully from {MODEL_PATH} (version={model_version})")
    return model, model_version


# Load model at startup
model, model_version = load_model()


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Predictions"],
    summary="Predict Student Score",
    responses={
        200: {
            "description": "Successful prediction",
            "example": {"hours": 5.0, "predicted_score": 55.2, "model_version": "1.0"},
        },
        422: {"description": "Invalid input (hours must be 0-24)"},
    },
)
def predict(request: PredictionRequest):
    """
    Predict a student's score based on study hours.

    - **hours**: Number of hours studied (must be between 0 and 24)

    Returns the predicted score and model information.
    """
    hours = request.hours

    df = pd.DataFrame({"Hours": [hours], "hours_squared": [hours**2]})

    predicted_score = float(model.predict(df)[0])

    return PredictionResponse(
        hours=hours, predicted_score=predicted_score, model_version=model_version
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health Check",
    responses={
        200: {
            "description": "API is healthy",
            "example": {
                "status": "healthy",
                "model": "loaded",
                "s3_bucket": "mlops-student",
            },
        }
    },
)
def health_check():
    """
    Check the health status of the API and model.

    Returns:
    - **status**: Overall API status
    - **model**: Whether the model is loaded
    - **s3_bucket**: S3 bucket used for model storage
    """
    return HealthResponse(status="healthy", model="loaded", s3_bucket=S3_BUCKET)


@app.post("/reload", tags=["System"], summary="Reload model from S3")
def reload_model():
    """Force reloading the latest model from S3 without restarting the app."""
    global model, model_version
    model, model_version = load_model()
    return {"status": "reloaded", "model_version": model_version}


@app.get("/", tags=["Info"], summary="API Information")
def root():
    """
    Welcome endpoint with API information.

    Visit `/docs` for interactive API documentation (Swagger UI)
    Visit `/redoc` for alternative API documentation (ReDoc)
    """
    return {
        "message": "Welcome to Student Score Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "POST /predict - Predict student score",
            "health": "GET /health - Check API health",
            "docs": "GET /docs - Swagger UI documentation",
            "redoc": "GET /redoc - ReDoc documentation",
        },
    }
