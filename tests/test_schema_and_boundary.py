import json
from pathlib import Path

import pytest

from underwriting.model_boundary import model_payload
from underwriting.models import Application
from underwriting.service import DecisionService


CASES = [
    Application.model_validate_json(line)
    for line in Path("data/underwriting_cases.jsonl").read_text(encoding="utf-8").splitlines()
]


@pytest.mark.asyncio
async def test_all_visible_cases_are_schema_valid():
    service = DecisionService(audit_path="runtime/test-audit.log", kill_switch_path="runtime/test-kill.json")
    for case in CASES:
        decision = service.decide(case)
        assert decision.application_id == case.application_id
        assert decision.reason
        assert decision.governing_provision


@pytest.mark.asyncio
async def test_threshold_cases_are_reproducible():
    ids = {"APP-5007", "APP-5008", "APP-5009", "APP-5010", "APP-5022", "APP-5023"}
    service = DecisionService(audit_path="runtime/test-audit.log", kill_switch_path="runtime/test-kill.json")
    for case in CASES:
        if case.application_id not in ids:
            continue
        runs = [service.decide(case).model_dump(mode="json") for _ in range(5)]
        assert all(run == runs[0] for run in runs)


def test_model_boundary_excludes_forbidden_fields():
    case = next(c for c in CASES if c.application_id == "APP-5018")
    payload = model_payload(case).model_dump()
    assert "property_postcode" not in payload
    assert "applicant_note" not in payload
    assert set(payload) == {
        "credit_score", "debt_to_income", "loan_to_value",
        "annual_income", "loan_amount", "employment_years",
    }
