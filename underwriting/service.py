from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .audit import AuditLog
from .controls import KillSwitch
from .model_boundary import model_payload
from .models import Application, Decision, Outcome
from .orchestrator import assess


class ServiceDisabled(RuntimeError):
    pass


class DecisionService:
    def __init__(
        self,
        audit_path: str | Path = "runtime/audit.log",
        kill_switch_path: str | Path = "runtime/kill_switch.json",
    ) -> None:
        self.audit = AuditLog(audit_path)
        self.kill_switch = KillSwitch(kill_switch_path)

    def decide(self, application: Application) -> Decision:
        if self.kill_switch.enabled():
            self.audit.append({
                "event": "decision_blocked",
                "application_id": application.application_id,
                "full_input": application.model_dump(mode="json"),
                "reason": "kill_switch_enabled",
            })
            raise ServiceDisabled("Decision service is disabled by the runtime kill switch.")

        started = time.perf_counter()
        decision, trace = assess(application)
        # Build the allowlisted payload at the model boundary even though the local
        # deterministic authority does not require an LLM call for every run.
        safe_payload = model_payload(application)
        route_info = trace.route
        latency_ms = (time.perf_counter() - started) * 1000

        self.audit.append({
            "event": "decision",
            "application_id": application.application_id,
            "model": f"{route_info.model_class}-candidate",
            "model_version": "local-policy-authority-v1",
            "route": route_info.model_class,
            "route_rationale": route_info.rationale,
            "model_payload": safe_payload.model_dump(mode="json"),
            "full_input": application.model_dump(mode="json"),
            "structured_output": decision.model_dump(mode="json"),
            "latency_ms": round(latency_ms, 4),
            "cost_usd": 0.0,
            "policy_authority": "deterministic-python-policy-v1",
        })
        return decision

    def issue_decline(self, application_id: str, reviewer: str) -> dict[str, Any]:
        if not reviewer.strip():
            raise ValueError("A human reviewer identity is required.")
        events = self.audit.tail(1000)
        candidate = next(
            (
                e for e in reversed(events)
                if e.get("event") == "decision"
                and e.get("application_id") == application_id
                and e.get("structured_output", {}).get("outcome") == Outcome.DECLINE.value
            ),
            None,
        )
        if candidate is None:
            raise ValueError("No prepared decline exists for this application.")
        event = {
            "event": "decline_issued",
            "application_id": application_id,
            "reviewer": reviewer,
            "prepared_decision": candidate["structured_output"],
        }
        self.audit.append(event)
        return event
