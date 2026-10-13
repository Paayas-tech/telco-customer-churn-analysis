"""Local HTTP checks: run python -m unittest app.test_api -v."""
import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from unittest.mock import patch

import joblib
import pandas as pd

from app.main import CATEGORICAL, FEATURES, MODEL_PATH, app, lifespan

CUSTOMER = {
    "gender": "Female", "senior_citizen": 1, "partner": "No", "dependents": "No",
    "tenure": 6, "phone_service": "Yes", "multiple_lines": "No",
    "internet_service": "Fiber optic", "online_security": "No", "online_backup": "No",
    "device_protection": "No", "tech_support": "No", "streaming_tv": "Yes",
    "streaming_movies": "Yes", "contract": "Month-to-month", "paperless_billing": "Yes",
    "payment_method": "Electronic check", "monthly_charges": 85.0, "total_charges": 510.0,
}


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        cls.base = f"http://127.0.0.1:{port}"
        cls.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=Path(__file__).resolve().parents[1],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        for _ in range(150):
            if cls.process.poll() is not None:
                raise RuntimeError("Test server failed startup.")
            try:
                with urlopen(cls.base + "/health", timeout=1):
                    return
            except (URLError, TimeoutError):
                time.sleep(0.1)
        cls.process.terminate()
        cls.process.wait(timeout=10)
        raise RuntimeError("Test server did not become healthy.")

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=10)

    def request(self, path, payload=None):
        request = Request(self.base + path,
                          data=json.dumps(payload).encode() if payload is not None else None,
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=10) as response:
            return json.load(response)

    def test_health_and_summary(self):
        self.assertEqual(self.request("/health"), {"status": "healthy"})
        summary = self.request("/analytics/summary")
        self.assertEqual(summary["total_customers"], 7043)
        self.assertEqual(summary["churn_rate_pct"], 26.54)
        self.assertEqual(summary["flagged_monthly_revenue_exposure"], 183535.15)
        self.assertEqual(summary["decision_threshold"], 0.35)

    def test_prediction_matches_saved_pipeline(self):
        result = self.request("/predict-risk", CUSTOMER)
        features = pd.DataFrame([CUSTOMER], columns=FEATURES)
        features[CATEGORICAL] = features[CATEGORICAL].astype(str)
        expected = joblib.load(MODEL_PATH).predict_proba(features)[0, 1]
        self.assertAlmostEqual(result["churn_probability"], expected, places=14)
        self.assertEqual(result["is_high_risk"], expected >= 0.35)
        self.assertEqual(result["revenue_at_risk"], 85.0 if expected >= 0.35 else 0.0)
        self.assertEqual(result["risk_tier"], "High" if expected >= 0.35 else "Moderate" if expected >= 0.20 else "Low")

    def test_invalid_inputs_return_422(self):
        for key, value in [("gender", "invalid"), ("senior_citizen", 2),
                           ("tenure", -1), ("tenure", 1.5), ("monthly_charges", 0),
                           ("total_charges", -1), ("payment_method", "invalid"),
                           ("customer_id", "unexpected")]:
            with self.subTest(field=key):
                with self.assertRaises(HTTPError) as error:
                    self.request("/predict-risk", dict(CUSTOMER, **{key: value}))
                self.assertEqual(error.exception.code, 422)
                error.exception.close()

    def test_missing_model_fails_startup(self):
        async def check():
            with patch("app.main.joblib.load", side_effect=FileNotFoundError):
                with self.assertRaises(RuntimeError):
                    async with lifespan(app):
                        pass
        asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
