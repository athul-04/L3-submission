from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import Application, Band, Decision, FactorDecision, Outcome


@dataclass(frozen=True)
class PolicyResult:
    outcome: Outcome
    credit_band: Band
    dti_band: Band
    ltv_band: Band
    governing_provision: str
    reason: str


def credit_band(value: Optional[int]) -> Band:
    if value is None:
        return Band.NOT_ASSESSED
    if value >= 700:
        return Band.STANDARD
    if value >= 640:
        return Band.ENHANCED_REVIEW
    return Band.DECLINE


def dti_band(value: Optional[float]) -> Band:
    if value is None:
        return Band.NOT_ASSESSED
    if value <= 0.36:
        return Band.STANDARD
    if value <= 0.43:
        return Band.ENHANCED_REVIEW
    return Band.DECLINE


def ltv_band(value: Optional[float]) -> Band:
    if value is None:
        return Band.NOT_ASSESSED
    if value <= 0.80:
        return Band.STANDARD
    if value <= 0.95:
        return Band.ENHANCED_REVIEW
    return Band.DECLINE


def evaluate(application: Application) -> PolicyResult:
    """Authoritative deterministic implementation of the supplied guidelines."""

    cb = credit_band(application.credit_score)
    db = dti_band(application.debt_to_income)
    lb = ltv_band(application.loan_to_value)

    missing = []
    if application.credit_score is None:
        missing.append("credit score")
    if application.debt_to_income is None:
        missing.append("debt-to-income")
    if application.loan_to_value is None:
        missing.append("loan-to-value")

    if missing:
        return PolicyResult(
            Outcome.REFER, cb, db, lb,
            "REFER: a primary factor is absent from the application.",
            f"Refer because the required factor(s) {', '.join(missing)} are absent; "
            "the guidelines prohibit inference, estimation, or defaulting."
        )

    # Both conditions are required for this referral.
    if application.employment_years < 1.0 and application.loan_amount > 3.0 * application.annual_income:
        return PolicyResult(
            Outcome.REFER, cb, db, lb,
            "REFER: employment history under 12 months and loan exceeds 3.0x annual income.",
            f"Refer because employment history is {application.employment_years:g} years "
            f"(< 12 months) and loan-to-income is {application.loan_amount / application.annual_income:.3f}x (> 3.0x)."
        )

    bands = (cb, db, lb)
    if Band.DECLINE in bands:
        reasons = []
        if cb is Band.DECLINE:
            reasons.append(f"credit score {application.credit_score} is below 640")
        if db is Band.DECLINE:
            reasons.append(f"DTI {application.debt_to_income:.2f} is above 0.43")
        if lb is Band.DECLINE:
            reasons.append(f"LTV {application.loan_to_value:.2f} is above 0.95")
        return PolicyResult(
            Outcome.DECLINE, cb, db, lb,
            "Combining the factors: any factor in the decline band produces DECLINE.",
            "Decline because " + "; ".join(reasons) + "."
        )

    if Band.ENHANCED_REVIEW in bands:
        reasons = []
        if cb is Band.ENHANCED_REVIEW:
            reasons.append(f"credit score {application.credit_score} is between 640 and 699 inclusive")
        if db is Band.ENHANCED_REVIEW:
            reasons.append(f"DTI {application.debt_to_income:.2f} is above 0.36 and at or below 0.43")
        if lb is Band.ENHANCED_REVIEW:
            reasons.append(f"LTV {application.loan_to_value:.2f} is above 0.80 and at or below 0.95")
        return PolicyResult(
            Outcome.ENHANCED_REVIEW, cb, db, lb,
            "Combining the factors: otherwise any factor in the enhanced-review band produces ENHANCED_REVIEW.",
            "Enhanced review because " + "; ".join(reasons) + "."
        )

    return PolicyResult(
        Outcome.APPROVE, cb, db, lb,
        "Combining the factors: all three primary factors are in the standard band.",
        "Approve because credit score, debt-to-income, and loan-to-value are all within the standard bands."
    )


def to_decision(application: Application, result: PolicyResult) -> Decision:
    return Decision(
        application_id=application.application_id,
        outcome=result.outcome,
        credit_score=FactorDecision(value=application.credit_score, band=result.credit_band),
        debt_to_income=FactorDecision(value=application.debt_to_income, band=result.dti_band),
        loan_to_value=FactorDecision(value=application.loan_to_value, band=result.ltv_band),
        governing_provision=result.governing_provision,
        reason=result.reason,
        human_approval_required=result.outcome is Outcome.DECLINE,
        issued=result.outcome is not Outcome.DECLINE,
    )
