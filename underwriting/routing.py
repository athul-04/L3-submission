from __future__ import annotations

from dataclasses import dataclass

from .models import Application
from .policy import credit_band, dti_band, ltv_band


@dataclass(frozen=True)
class Route:
    model_class: str
    rationale: str


def route(application: Application) -> Route:
    """Evidence-oriented routing heuristic.

    The production rule is intentionally conservative: use the cheaper model for
    straightforward standard-band cases; route boundary, adverse, referral, or
    mixed-band cases to the reasoning model. The final decision remains the
    deterministic policy result. After the external benchmark, this rule should be
    updated if the measured error set shows a narrower safe boundary.
    """
    cb, db, lb = (
        credit_band(application.credit_score),
        dti_band(application.debt_to_income),
        ltv_band(application.loan_to_value),
    )

    if None in (application.credit_score, application.debt_to_income, application.loan_to_value):
        return Route("reasoning", "Missing primary factor: referral cases are high consequence.")

    boundary = (
        application.credit_score in {640, 641, 699, 700}
        or application.debt_to_income in {0.36, 0.37, 0.43, 0.44}
        or application.loan_to_value in {0.80, 0.81, 0.95, 0.96}
    )
    if boundary:
        return Route("reasoning", "Policy boundary case; use reasoning-grade verification.")

    if application.employment_years < 1.0 and application.loan_amount > 3.0 * application.annual_income:
        return Route("reasoning", "Referral condition is jointly triggered.")

    if "DECLINE" in {cb.value, db.value, lb.value}:
        return Route("reasoning", "Adverse-action candidate requires higher scrutiny.")

    if "ENHANCED_REVIEW" in {cb.value, db.value, lb.value}:
        return Route("reasoning", "Non-standard band requires higher-scrutiny verification.")

    return Route("cheap", "All policy factors are standard and not at a measured boundary.")
