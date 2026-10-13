"""Local analytics and inference API; no training or customer-data persistence."""
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from sklearn.pipeline import Pipeline

from app.schemas import CustomerInput, PredictionResponse

MODEL_PATH = Path(__file__).resolve().parents[1] / "models/baseline_logistic_pipeline.joblib"
HIGH_RISK_THRESHOLD = 0.35
# Display-only policy boundary; this tier has not been separately validated.
MODERATE_RISK_THRESHOLD = 0.20
NUMERIC = ["tenure", "monthly_charges", "total_charges"]
CATEGORICAL = [
    "gender", "senior_citizen", "partner", "dependents", "phone_service",
    "multiple_lines", "internet_service", "online_security", "online_backup",
    "device_protection", "tech_support", "streaming_tv", "streaming_movies",
    "contract", "paperless_billing", "payment_method",
]
FEATURES = NUMERIC + CATEGORICAL


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Joblib is executable serialization: load only this trusted local artifact.
    # Fail startup clearly rather than serving a healthy API with no usable model.
    try:
        pipeline = joblib.load(MODEL_PATH)
        if not isinstance(pipeline, Pipeline):
            raise ValueError("Expected a fitted sklearn Pipeline.")
        if list(pipeline.classes_) != [0, 1]:
            raise ValueError("Expected class 1 to represent churn.")
        if list(pipeline.feature_names_in_) != FEATURES:
            raise ValueError("Model features do not match the API schema.")
    except Exception as exc:
        raise RuntimeError("Cannot initialize the trusted local baseline pipeline; regenerate it with python/train_baseline.py.") from exc
    app.state.pipeline = pipeline
    yield
    del app.state.pipeline


app = FastAPI(title="Telco Churn Analytics & Prediction", lifespan=lifespan)


@app.get("/health")
def health(request: Request):
    if getattr(request.app.state, "pipeline", None) is None:
        raise HTTPException(status_code=503, detail="Model is not ready.")
    return {"status": "healthy"}


@app.post("/predict-risk", response_model=PredictionResponse)
def predict_risk(customer: CustomerInput, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model is not ready.")
    features = pd.DataFrame([customer.model_dump()], columns=FEATURES)
    # Training loaded categorical values as strings, including senior_citizen.
    features[CATEGORICAL] = features[CATEGORICAL].astype(str)
    try:
        probability = float(pipeline.predict_proba(features)[0, 1])
        if not np.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError("Invalid probability.")
    except Exception:
        # Avoid exposing artifact internals or customer values in responses.
        raise HTTPException(status_code=500, detail="Prediction failed.") from None
    high_risk = probability >= HIGH_RISK_THRESHOLD
    tier = "High" if high_risk else "Moderate" if probability >= MODERATE_RISK_THRESHOLD else "Low"
    return PredictionResponse(
        churn_probability=probability, risk_tier=tier, is_high_risk=high_risk,
        revenue_at_risk=customer.monthly_charges if high_risk else 0.0,
    )


@app.get("/analytics/summary")
def analytics_summary():
    # Static retrospective benchmarks, not live API activity or new validation.
    return {
        "total_customers": 7043,
        "churn_rate_pct": 26.54,
        "flagged_monthly_revenue_exposure": 183535.15,
        "decision_threshold": HIGH_RISK_THRESHOLD,
        "currency": "USD",
        "benchmark_scope": "Retrospective dataset snapshot including training rows and historical churners",
    }
