"""Reproducible CSV churn baseline; run with .venv/Scripts/python python/train_baseline.py."""
from pathlib import Path
import hashlib
import platform

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, confusion_matrix, precision_score, recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 42
DATA = Path(__file__).resolve().parents[1] / "data/processed/cleaned_telco_churn.csv"
NUMERIC = ["tenure", "monthly_charges", "total_charges"]
CATEGORICAL = [
    "gender", "senior_citizen", "partner", "dependents", "phone_service",
    "multiple_lines", "internet_service", "online_security", "online_backup",
    "device_protection", "tech_support", "streaming_tv", "streaming_movies",
    "contract", "paperless_billing", "payment_method",
]
EXPECTED = {"customer_id", "churn", "tenure_group", *NUMERIC, *CATEGORICAL}
DOMAINS = {
    "gender": {"Female", "Male"}, "senior_citizen": {"0", "1"},
    "contract": {"Month-to-month", "One year", "Two year"},
    "internet_service": {"DSL", "Fiber optic", "No"},
    "multiple_lines": {"Yes", "No", "No phone service"},
    "payment_method": {"Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"},
    "tenure_group": {"0-1 Year", "1-2 Years", "2-4 Years", "4+ Years"},
}
for column in ["partner", "dependents", "phone_service", "paperless_billing"]:
    DOMAINS[column] = {"Yes", "No"}
for column in ["online_security", "online_backup", "device_protection", "tech_support", "streaming_tv", "streaming_movies"]:
    DOMAINS[column] = {"Yes", "No", "No internet service"}


def validate(data):
    """Fail clearly on invalid inputs without printing customer records."""
    if set(data.columns) != EXPECTED:
        raise ValueError("CSV columns do not match the expected 22-column schema.")
    if data.empty or data.isna().any().any():
        raise ValueError("CSV is empty or contains missing values; review the source.")
    if data["customer_id"].str.strip().eq("").any() or data["customer_id"].duplicated().any():
        raise ValueError("Customer IDs must be nonblank and unique.")
    if set(data["churn"]) != {"Yes", "No"}:
        raise ValueError("Churn labels must contain both Yes and No only.")
    for column, domain in DOMAINS.items():
        if not set(data[column]).issubset(domain):
            raise ValueError(f"Unexpected category in {column}.")
    for column in NUMERIC:
        data[column] = pd.to_numeric(data[column], errors="raise")
        if not np.isfinite(data[column].to_numpy()).all() or (data[column] < 0).any():
            raise ValueError(f"Invalid numeric values in {column}.")
    if (data["tenure"] % 1 != 0).any():
        raise ValueError("Tenure must be a whole number of months.")
    if data["churn"].value_counts().min() < 5:
        raise ValueError("Too few examples per class for the stratified split.")


def sql_heuristic(features):
    """Mirror SQL 05 rules; scores rank risk but are not probabilities."""
    contract = features["contract"]
    fiber = features["internet_service"].eq("Fiber optic")
    unsupported = features["tech_support"].eq("No")
    tenure = features["tenure"]
    return (
        np.where(contract.eq("Month-to-month"), 40, np.where(contract.eq("One year"), 10, 0))
        + np.where(fiber & unsupported, 30, np.where(fiber, 15, 0))
        + np.where(tenure <= 12, 20, np.where(tenure <= 24, 10, 0))
        + np.where(features["payment_method"].eq("Electronic check"), 10, 0)
    )


def evaluate(name, target, scores, predictions):
    """Use identical test labels for every ranking and classification metric."""
    tn, fp, fn, tp = confusion_matrix(target, predictions, labels=[0, 1]).ravel()
    return {
        "Model / threshold": name,
        "ROC-AUC": roc_auc_score(target, scores),
        "AP": average_precision_score(target, scores),
        "Precision": precision_score(target, predictions, zero_division=0),
        "Recall": recall_score(target, predictions, zero_division=0),
        "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp),
    }


def main():
    # Resolve the CSV relative to this script so any working directory is supported.
    data = pd.read_csv(DATA, dtype=str)
    validate(data)
    target = data["churn"].map({"No": 0, "Yes": 1}).astype(int)
    # Explicit feature selection excludes ID, target, and redundant tenure cohorts.
    features = data[NUMERIC + CATEGORICAL]
    # Split once; every comparator receives these exact same train/test rows.
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.20, stratify=target, random_state=SEED,
    )
    # Encoders and scalers learn only from training rows inside the pipeline.
    preprocessing = ColumnTransformer([
        ("numeric", StandardScaler(), NUMERIC),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    model = Pipeline([
        ("preprocessing", preprocessing),
        ("classifier", LogisticRegression(max_iter=2000, random_state=SEED)),
    ])
    model.fit(x_train, y_train)
    if model.named_steps["classifier"].n_iter_.max() >= 2000:
        raise RuntimeError("Logistic regression did not converge.")
    results = []
    # Constant-probability dummy gives a stable no-skill ranking reference.
    dummy = DummyClassifier(strategy="most_frequent", random_state=SEED)
    dummy.fit(x_train, y_train)
    positive = list(dummy.classes_).index(1)
    results.append(evaluate("Dummy (most frequent)", y_test,
                            dummy.predict_proba(x_test)[:, positive], dummy.predict(x_test)))
    # High SQL risk means score >=70; continuous scores supply ranking metrics.
    heuristic = sql_heuristic(x_test)
    results.append(evaluate("SQL heuristic (>=70)", y_test, heuristic, (heuristic >= 70).astype(int)))
    probabilities = model.predict_proba(x_test)[:, list(model.classes_).index(1)]
    # Fixed scenarios illustrate tradeoffs; no threshold is selected using test labels.
    for threshold in (0.50, 0.40, 0.35):
        results.append(evaluate(f"Logistic (>= {threshold:.2f})", y_test,
                                probabilities, (probabilities >= threshold).astype(int)))
    print("TELCO CHURN BASELINE | seed=42 | stratified 80/20 split")
    print(f"Versions: Python {platform.python_version()}, pandas {pd.__version__}, "
          f"numpy {np.__version__}, scikit-learn {sklearn.__version__}")
    print(f"CSV SHA-256: {hashlib.sha256(DATA.read_bytes()).hexdigest()}")
    print(f"Validated: {len(data)} rows, unique IDs, complete schema, no missing values")
    print(f"Labels: No={(target == 0).sum()}, Yes={(target == 1).sum()} ({target.mean():.2%} churn)")
    print(f"Train: {len(y_train)} rows / {y_train.sum()} churn; "
          f"Test: {len(y_test)} rows / {y_test.sum()} churn ({y_test.mean():.2%})")
    print(f"Features: {len(NUMERIC)} scaled numeric + {len(CATEGORICAL)} one-hot categorical; ID/cohort excluded")
    print(pd.DataFrame(results).to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("AP = Average Precision (PR-AUC summary). Confusion matrices: [[TN, FP], [FN, TP]].")
    print("Precision/recall for no positive predictions are reported as 0.")
    print("Lower thresholds are preset scenarios, not validated business-optimal thresholds.")
    print("SQL heuristic is retrospective and uncalibrated; causal effects and future performance are unverified.")
    print("No customer-level outputs or model files are written.")


if __name__ == "__main__":
    main()
