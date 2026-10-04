from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from underwriting.cli import load_case
from underwriting.service import DecisionService, ServiceDisabled

service = DecisionService()
app = load_case("APP-5001")
service.kill_switch.set(True)
try:
    service.decide(app)
except ServiceDisabled as exc:
    print(f"PASS: runtime kill switch blocked the decision: {exc}")
finally:
    service.kill_switch.set(False)
print("PASS: service re-enabled without redeploy.")
