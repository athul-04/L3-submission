import json
from pathlib import Path

from underwriting.models import Application
from underwriting.policy import evaluate


EXPECTED = {
    "APP-5001": "APPROVE", "APP-5002": "APPROVE", "APP-5003": "DECLINE",
    "APP-5004": "DECLINE", "APP-5005": "ENHANCED_REVIEW", "APP-5006": "ENHANCED_REVIEW",
    "APP-5007": "APPROVE", "APP-5008": "ENHANCED_REVIEW", "APP-5009": "ENHANCED_REVIEW",
    "APP-5010": "ENHANCED_REVIEW", "APP-5011": "APPROVE", "APP-5012": "ENHANCED_REVIEW",
    "APP-5013": "APPROVE", "APP-5014": "DECLINE", "APP-5015": "REFER",
    "APP-5016": "REFER", "APP-5017": "DECLINE", "APP-5018": "ENHANCED_REVIEW",
    "APP-5019": "APPROVE", "APP-5020": "APPROVE", "APP-5021": "ENHANCED_REVIEW",
    "APP-5022": "ENHANCED_REVIEW", "APP-5023": "ENHANCED_REVIEW", "APP-5024": "APPROVE",
}


def test_all_24_answer_key_cases():
    lines = Path("data/underwriting_cases.jsonl").read_text(encoding="utf-8").splitlines()
    for line in lines:
        app = Application.model_validate_json(line)
        assert evaluate(app).outcome.value == EXPECTED[app.application_id]
