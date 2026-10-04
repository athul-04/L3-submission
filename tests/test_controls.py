import pytest

from underwriting.controls import KillSwitch
from underwriting.models import Application, Outcome
from underwriting.service import DecisionService, ServiceDisabled


def case():
    return Application(
        application_id="CONTROL-1",
        credit_score=720,
        debt_to_income=.30,
        loan_to_value=.80,
        annual_income=100000,
        loan_amount=250000,
        property_postcode="X",
        employment_years=5,
        applicant_note="",
    )


@pytest.mark.asyncio
async def test_kill_switch_blocks_and_reenables(tmp_path):
    switch = tmp_path / "kill.json"
    audit = tmp_path / "audit.log"
    service = DecisionService(audit, switch)

    service.kill_switch.set(True)
    with pytest.raises(ServiceDisabled):
        service.decide(case())

    service.kill_switch.set(False)
    decision = service.decide(case())
    assert decision.outcome is Outcome.APPROVE


@pytest.mark.asyncio
async def test_decline_is_prepared_but_not_issued(tmp_path):
    service = DecisionService(tmp_path / "audit.log", tmp_path / "kill.json")
    app = case().model_copy(update={"application_id": "DECLINE-1", "credit_score": 600})
    decision = service.decide(app)
    assert decision.outcome is Outcome.DECLINE
    assert decision.human_approval_required is True
    assert decision.issued is False

    event = service.issue_decline(app.application_id, "Chief Credit Officer")
    assert event["reviewer"] == "Chief Credit Officer"
