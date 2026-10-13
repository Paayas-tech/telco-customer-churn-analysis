"""Validated API contracts aligned with the fitted model's categorical domains."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

YesNo = Literal["Yes", "No"]
InternetAddon = Literal["Yes", "No", "No internet service"]


class CustomerInput(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    gender: Literal["Male", "Female"]
    senior_citizen: Literal[0, 1]
    partner: YesNo
    dependents: YesNo
    tenure: int = Field(ge=0, strict=True)
    phone_service: YesNo
    multiple_lines: Literal["Yes", "No", "No phone service"]
    internet_service: Literal["DSL", "Fiber optic", "No"]
    online_security: InternetAddon
    online_backup: InternetAddon
    device_protection: InternetAddon
    tech_support: InternetAddon
    streaming_tv: InternetAddon
    streaming_movies: InternetAddon
    contract: Literal["Month-to-month", "One year", "Two year"]
    paperless_billing: YesNo
    payment_method: Literal[
        "Electronic check", "Mailed check", "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]
    monthly_charges: float = Field(gt=0.0)
    total_charges: float = Field(ge=0.0)


class PredictionResponse(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    churn_probability: float = Field(ge=0.0, le=1.0)
    risk_tier: Literal["High", "Moderate", "Low"]
    is_high_risk: bool
    revenue_at_risk: float = Field(ge=0.0)
