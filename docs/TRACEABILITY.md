# Case Requirement Traceability

| Requirement | Implementation / evidence |
|---|---|
| Determinism | `underwriting/policy.py`; `artifacts/determinism_evidence.json` |
| Structured output | `underwriting/models.py` Pydantic `Decision` |
| Exact thresholds | `underwriting/policy.py`; `tests/test_policy.py` |
| Missing factor → REFER | `underwriting/policy.py`; tests |
| Employment + >3x income referral | `underwriting/policy.py`; tests |
| Model routing + measurement | `underwriting/routing.py`; `scripts/run_model_benchmark.py`; ADR-002 |
| Fair-lending exclusion | `underwriting/model_boundary.py`; ADR-003; boundary test |
| Applicant free text | excluded from model payload; policy tests |
| Adverse action | `Decision.issued=False`; `issue_decline`; tests |
| Cost/latency | PMAT report + benchmark |
| Audit | `underwriting/audit.py`; `artifacts/audit_samples.json` |
| Kill switch | `underwriting/controls.py`; `scripts/demo_kill_switch.py`; tests |
| Requirements conflict | ADR-002 |
| Reflection / effort | `REFLECTION.md` |

## Visible threshold applications

APP-5007, APP-5008, APP-5009, APP-5010, APP-5022, APP-5023.

## Visible robustness applications

- APP-5015 / APP-5016: missing primary factors → REFER.
- APP-5018: applicant note attempts to override the process.
- APP-5019: applicant note attempts to override thresholds.
- APP-5011: short employment alone does not refer because the >3x income condition is false.
