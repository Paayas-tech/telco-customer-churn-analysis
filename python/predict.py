"""Score the local customer snapshot with the saved training-fitted pipeline."""
from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from train_baseline import CATEGORICAL, DATA, MODEL_PATH, NUMERIC, validate

THRESHOLD = 0.35
OUTPUT = Path(__file__).resolve().parents[1] / "data/predictions/customer_churn_scored.csv"
EXPORT_COLUMNS = [
    "customer_id", "tenure", "contract", "monthly_charges", "churn_probability",
    "predicted_churn_flag", "monthly_revenue_at_risk",
]


def score_customers(data, pipeline):
    """Validate the snapshot and score without fitting or using churn labels."""
    data = data.copy()
    validate(data)
    # Explicit selection preserves training features and excludes ID and tenure_group.
    features = data[NUMERIC + CATEGORICAL]
    if list(pipeline.classes_) != [0, 1]:
        raise ValueError("Expected class order [0, 1], with class 1 representing churn.")
    if list(pipeline.feature_names_in_) != list(features.columns):
        raise ValueError("Saved pipeline features do not match the scoring schema.")
    probabilities = pipeline.predict_proba(features)[:, 1]
    if not np.isfinite(probabilities).all() or ((probabilities < 0) | (probabilities > 1)).any():
        raise ValueError("Model returned invalid churn probabilities.")
    # Equality at the threshold is included in the high-risk group.
    flags = (probabilities >= THRESHOLD).astype(int)
    scored = data[["customer_id", "tenure", "contract", "monthly_charges"]].copy()
    scored["churn_probability"] = probabilities
    scored["predicted_churn_flag"] = flags
    scored["monthly_revenue_at_risk"] = np.where(flags == 1, data["monthly_charges"], 0.0)
    return scored[EXPORT_COLUMNS]


def main():
    # Load only the trusted artifact generated locally by train_baseline.py.
    pipeline = joblib.load(MODEL_PATH)
    data = pd.read_csv(DATA, dtype=str)
    scored = score_customers(data, pipeline)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    # Keep full probability precision and omit the DataFrame index from the audit CSV.
    scored.to_csv(OUTPUT, index=False)
    # Decimal summation keeps the aggregate currency total precise to cents.
    flagged_mrr = sum((Decimal(str(value)) for value in scored["monthly_revenue_at_risk"]), Decimal("0"))
    print(f"BATCH CHURN SCORING | threshold={THRESHOLD:.2f}")
    print(f"Total accounts scored: {len(scored):,}")
    print(f"Accounts flagged as high risk: {scored['predicted_churn_flag'].sum():,}")
    print(f"Total MRR flagged at risk: ${flagged_mrr:,.2f}")
    print(f"Average churn probability: {scored['churn_probability'].mean():.4f} ({scored['churn_probability'].mean():.2%})")
    print(f"Export: {OUTPUT}")
    print("Flagged MRR is exposure at the chosen threshold, not expected or realized loss.")
    print("Flag 0 means below threshold, not guaranteed safe. The 0.35 threshold is a preset scenario.")
    print("This retrospective snapshot includes training rows and historical churners; it is not a new model evaluation.")


if __name__ == "__main__":
    main()
