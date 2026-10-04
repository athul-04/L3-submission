from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Outcome(str, Enum):
    APPROVE = "APPROVE"
    ENHANCED_REVIEW = "ENHANCED_REVIEW"
    DECLINE = "DECLINE"
    REFER = "REFER"


class Band(str, Enum):
    STANDARD = "STANDARD"
    ENHANCED_REVIEW = "ENHANCED_REVIEW"
    DECLINE = "DECLINE"
    NOT_ASSESSED = "NOT_ASSESSED"


class Application(BaseModel):
    model_config = ConfigDict(extra="forbid")

    application_id: str
    credit_score: Optional[int] = Field(default=None, ge=0)
    debt_to_income: Optional[float] = Field(default=None, ge=0)
    loan_to_value: Optional[float] = Field(default=None, ge=0)
    annual_income: float = Field(ge=0)
    loan_amount: float = Field(ge=0)
    property_postcode: str
    employment_years: float = Field(ge=0)
    applicant_note: str = ""


class FactorDecision(BaseModel):
    value: Optional[float | int]
    band: Band


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    application_id: str
    outcome: Outcome
    credit_score: FactorDecision
    debt_to_income: FactorDecision
    loan_to_value: FactorDecision
    governing_provision: str
    reason: str
    human_approval_required: bool
    issued: bool = False


class ModelPayload(BaseModel):
    """The only fields structurally permitted to reach an LLM."""

    model_config = ConfigDict(extra="forbid")

    credit_score: Optional[int]
    debt_to_income: Optional[float]
    loan_to_value: Optional[float]
    annual_income: float
    loan_amount: float
    employment_years: float
