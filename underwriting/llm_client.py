from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from portkey_ai import Portkey
from pydantic import ValidationError

from .model_boundary import model_payload
from .models import Application, Band, Outcome
from .models import Decision
from .llm_benchmark import Candidate, SYSTEM_PROMPT, USER_TEMPLATE


@dataclass(frozen=True)
class Verification:
    attempted: bool
    model: str | None
    valid: bool
    candidate: Candidate | None
    latency_ms: float | None
    cost_usd: float | None
    error: str | None


def verify(application: Application, model_class: str) -> Verification:
    load_dotenv()
    key = os.environ.get("PORTKEY_API_KEY")
    model = os.environ.get(
        "PORTKEY_CHEAP_MODEL" if model_class == "cheap" else "PORTKEY_REASONING_MODEL"
    )
    if not key or not model:
        return Verification(False, None, False, None, None, None, "External model not configured")

    try:
        client = Portkey(
            api_key=key,
            base_url=os.environ.get("PORTKEY_BASE_URL", "https://api.portkey.ai/v1"),
        )
        payload = model_payload(application).model_dump(mode="json")
        started = time.perf_counter()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_TEMPLATE.format(payload=json.dumps(payload, sort_keys=True))},
            ],
            temperature=0,
        )
        latency_ms = (time.perf_counter() - started) * 1000
        candidate = Candidate.model_validate_json(response.choices[0].message.content or "")
        usage = getattr(response, "usage", None)
        cost = None
        if usage is not None:
            prompt_tokens = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None)
            completion_tokens = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", None)
            if prompt_tokens is not None and completion_tokens is not None:
                prefix = "PORTKEY_CHEAP" if model_class == "cheap" else "PORTKEY_REASONING"
                cost = (
                    prompt_tokens / 1000 * float(os.environ.get(f"{prefix}_INPUT_USD_PER_1K", "0"))
                    + completion_tokens / 1000 * float(os.environ.get(f"{prefix}_OUTPUT_USD_PER_1K", "0"))
                )
        return Verification(True, model, True, candidate, latency_ms, cost, None)
    except Exception as exc:
        return Verification(True, model, False, None, (time.perf_counter() - started) * 1000 if "started" in locals() else None, None, f"{type(exc).__name__}: {exc}")
