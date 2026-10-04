# Reflection

## What was built

A minimal deterministic underwriting decision service implementing the supplied Brightmoor
policy, with structured Pydantic output, an explicit model boundary, bounded model routing,
audit logging, a runtime kill switch, and a human gate for adverse action.

## What was intentionally not built

- No FastAPI/Swagger layer: the case does not require HTTP transport.
- No database: the capstone can demonstrate audit reconstruction with append-only JSONL.
- No LangGraph: the workflow is small enough that explicit Python orchestration is easier
  to reason about and more reproducible.
- No cloud deployment: not required by the case.
- No fake model benchmark numbers: external model evidence must be generated using the
  user's configured Portkey access.

## Failure modes considered

1. Boundary drift: addressed by explicit inclusive comparisons and repeated threshold tests.
2. Missing factor inference: addressed by explicit REFER.
3. Prompt injection in applicant notes: notes never enter the model payload.
4. Fair-lending proxy leakage: postcode is structurally excluded.
5. LLM schema failure: candidate output is validated separately and cannot override policy.
6. Adverse-action automation: decline remains prepared but unissued until human approval.
7. Cost conflict: NFR-4 hard ceiling wins; reasoning usage is bounded and measured.
8. Operational stop: kill switch blocks decisions without redeployment.

## What should be improved for production

Use a durable append-only audit store with integrity controls, a centralized policy/version
registry, authenticated administrative controls, secret management, distributed metrics,
and a controlled model-evaluation pipeline.

