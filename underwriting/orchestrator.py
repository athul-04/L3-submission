from __future__ import annotations

from dataclasses import dataclass

from .models import Application, Decision
from .policy import evaluate, to_decision
from .routing import Route, route


@dataclass(frozen=True)
class AssessmentTrace:
    route: Route
    policy_outcome: str
    model_boundary_fields: tuple[str, ...]
    human_gate: bool


def assess(application: Application) -> tuple[Decision, AssessmentTrace]:
    """Bounded orchestration.

    Router selects a verification model class; the deterministic policy engine is
    the authority. A model candidate can inform evidence, but cannot change the
    regulated decision. Declines end at a human gate.
    """
    selected = route(application)
    policy = evaluate(application)
    decision = to_decision(application, policy)
    trace = AssessmentTrace(
        route=selected,
        policy_outcome=policy.outcome.value,
        model_boundary_fields=(
            "credit_score",
            "debt_to_income",
            "loan_to_value",
            "annual_income",
            "loan_amount",
            "employment_years",
        ),
        human_gate=decision.human_approval_required,
    )
    return decision, trace
