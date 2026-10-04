from __future__ import annotations

from .models import Application, ModelPayload

# Explicit allowlist. The postcode and free-text note are intentionally impossible
# to reach the model through this boundary.
MODEL_FIELDS = (
    "credit_score",
    "debt_to_income",
    "loan_to_value",
    "annual_income",
    "loan_amount",
    "employment_years",
)


def model_payload(application: Application) -> ModelPayload:
    return ModelPayload(
        credit_score=application.credit_score,
        debt_to_income=application.debt_to_income,
        loan_to_value=application.loan_to_value,
        annual_income=application.annual_income,
        loan_amount=application.loan_amount,
        employment_years=application.employment_years,
    )
