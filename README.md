# L3 Case 03 — Deterministic Underwriting Decision Service

This project is a minimal Python implementation of the supplied L3 Case 03 requirements.
It intentionally does **not** add a web server, Swagger, database, or orchestration framework.

## What is implemented

- Deterministic policy engine implementing the supplied Brightmoor Lending guidelines exactly.
- Pydantic structured decision schema and validation.
- Referral handling for missing primary factors and the employment/income referral rule.
- Structural fair-lending field exclusion: `property_postcode` and `applicant_note` never enter the model payload.
- Untrusted applicant notes are retained as audit evidence only; they cannot act as instructions.
- Model-candidate routing/benchmark harness through Portkey (optional until the external benchmark is run).
- Deterministic final authority: an LLM candidate can never override the written policy.
- Adverse-action gate: a prepared decline requires explicit human issuance.
- Immutable append-only JSONL audit log containing the full request, final structured result, model/version, latency, cost, and timestamp.
- Runtime kill switch with no redeploy.
- Five-run determinism evidence for all six visible threshold applications.
- PMAT report generation.
- Async pytest test suite.

## Requirements

- Python 3.11+
- `pip install -r requirements.txt`

No API key is required for the deterministic service or the local test suite.

## Run the deterministic service

```bash
python -m underwriting.cli decide APP-5007
```

Or pass a JSON application:

```bash
python -m underwriting.cli decide-json path/to/application.json
```

Generate evidence:

```bash
python scripts/generate_evidence.py
```

Run tests:

```bash
pytest -q
```

## Model benchmark

The case requires measured evidence for model selection. The project therefore includes
an optional Portkey benchmark. Do not invent benchmark numbers.

Copy `.env.example` to `.env` and fill the Portkey/model settings only when you are ready
to make real model calls:

```text
PORTKEY_API_KEY=...
PORTKEY_CHEAP_MODEL=...
PORTKEY_REASONING_MODEL=...
PORTKEY_PROVIDER=...          # optional if your Portkey workspace needs it
```

Then:

```bash
python scripts/run_model_benchmark.py
python scripts/generate_evidence.py
pytest -q
```

The benchmark compares model candidates against the deterministic policy answer key.
The final service remains deterministic regardless of model output.

## Kill switch

The runtime state is stored in `runtime/kill_switch.json`.

```bash
python scripts/kill_switch.py on
python -m underwriting.cli decide APP-5001   # blocked
python scripts/kill_switch.py off
```


## Submission gate

`pmat-report.json` intentionally remains `PRE_SUBMISSION` until the real external
model benchmark has been executed.
