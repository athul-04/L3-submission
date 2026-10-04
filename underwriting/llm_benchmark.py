from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

from dotenv import load_dotenv
from portkey_ai import Portkey
from pydantic import BaseModel, ConfigDict, ValidationError

from .models import Application, Band, Outcome
from .model_boundary import model_payload
from .policy import evaluate


class Candidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: Outcome
    credit_band: Band
    dti_band: Band
    ltv_band: Band
    governing_provision: str
    reason: str


@dataclass
class BenchmarkRow:
    application_id: str
    model_class: str
    model: str
    valid: bool
    outcome: str | None
    expected_outcome: str
    correct: bool
    latency_ms: float
    cost_usd: float | None
    error: str | None

SYSTEM_PROMPT = """You are an underwriting assessment candidate.

Return JSON only.

IMPORTANT: Use these EXACT uppercase enum values:
- outcome: APPROVE, ENHANCED_REVIEW, DECLINE, REFER
- credit_band: STANDARD, ENHANCED_REVIEW, DECLINE, NOT_ASSESSED
- dti_band: STANDARD, ENHANCED_REVIEW, DECLINE, NOT_ASSESSED
- ltv_band: STANDARD, ENHANCED_REVIEW, DECLINE, NOT_ASSESSED

Use ONLY the supplied policy fields.
Do not infer missing primary factors.
Do not use postcode or applicant free text.

Return these fields:
outcome, credit_band, dti_band, ltv_band, governing_provision, reason.

Apply the Brightmoor policy exactly:
credit >=700 standard, 640-699 enhanced, <640 decline;
DTI <=.36 standard, >.36<=.43 enhanced, >.43 decline;
LTV <=.80 standard, >.80<=.95 enhanced, >.95 decline.

Any decline wins;
otherwise any enhanced wins;
otherwise approve.

Missing primary factor means REFER.

Employment under 12 months AND loan >3x annual income means REFER.
"""
USER_TEMPLATE = "Application policy fields:\n{payload}"


def _client() -> Portkey:
    load_dotenv()
    key = os.environ.get("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is not configured.")
    base_url = os.environ.get("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")
    return Portkey(api_key=key, base_url=base_url)


def _cost_from_usage(usage: Any, model_class: str) -> float | None:
    if usage is None:
        return None
    prompt_tokens = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None)
    completion_tokens = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", None)
    if prompt_tokens is None or completion_tokens is None:
        return None
    pfx = "PORTKEY_CHEAP" if model_class == "cheap" else "PORTKEY_REASONING"
    in_price = float(os.environ.get(f"{pfx}_INPUT_USD_PER_1K", "0"))
    out_price = float(os.environ.get(f"{pfx}_OUTPUT_USD_PER_1K", "0"))
    return prompt_tokens / 1000 * in_price + completion_tokens / 1000 * out_price


def call_model(application: Application, model_class: str) -> BenchmarkRow:
    load_dotenv()
    model = os.environ["PORTKEY_CHEAP_MODEL" if model_class == "cheap" else "PORTKEY_REASONING_MODEL"]
    expected = evaluate(application).outcome.value
    payload = model_payload(application).model_dump(mode="json")
    started = time.perf_counter()

    try:
        client = _client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_TEMPLATE.format(payload=json.dumps(payload, sort_keys=True))},
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2048,
        )
        latency_ms = (time.perf_counter() - started) * 1000
        content = response.choices[0].message.content or ""
        candidate = Candidate.model_validate_json(content)
        correct = candidate.outcome.value == expected
        return BenchmarkRow(
            application.application_id, model_class, model, True,
            candidate.outcome.value, expected, correct, latency_ms,
            _cost_from_usage(getattr(response, "usage", None), model_class), None
        )
    except (ValidationError, ValueError, KeyError, RuntimeError, Exception) as exc:
        latency_ms = (time.perf_counter() - started) * 1000
        return BenchmarkRow(
            application.application_id, model_class, model, False,
            None, expected, False, latency_ms, None, f"{type(exc).__name__}: {exc}"
        )


def run_benchmark(applications: list[Application]) -> dict[str, Any]:
    rows: list[BenchmarkRow] = []
    for application in applications:
        rows.append(call_model(application, "cheap"))
        rows.append(call_model(application, "reasoning"))

    serialised = [asdict(row) for row in rows]
    summary: dict[str, Any] = {}
    for cls in ("cheap", "reasoning"):
        subset = [r for r in rows if r.model_class == cls]
        valid = [r for r in subset if r.valid]
        correct = [r for r in valid if r.correct]
        costs = [r.cost_usd for r in valid if r.cost_usd is not None]
        latencies = sorted(r.latency_ms for r in valid)
        summary[cls] = {
            "model": subset[0].model if subset else None,
            "applications": len(subset),
            "valid_outputs": len(valid),
            "accuracy": len(correct) / len(subset) if subset else 0.0,
            "mean_cost_usd": sum(costs) / len(costs) if costs else None,
            "p95_latency_ms": latencies[max(0, int(len(latencies) * 0.95) - 1)] if latencies else None,
            "wrong_applications": [r.application_id for r in subset if not r.correct],
        }

    return {"rows": serialised, "summary": summary}
