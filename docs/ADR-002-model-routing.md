# ADR-002: Evidence-Based Model Routing

**Status:** Accepted — benchmark measured

## Context

NFR-6 requires measured model selection. NFR-4 imposes a hard mean cost ceiling of
$0.05/decision. NFR-5 requires p95 latency below 2 seconds.

## Decision

Use a two-tier verification route:
1. Cheap model for straightforward standard-band cases away from thresholds.
2. Reasoning-grade model for threshold/boundary, enhanced-review, adverse-action, and
   referral cases.

The benchmark compares both models on all 24 visible applications against the written
policy answer key. The artifact records valid outputs, accuracy, wrong application IDs,
latency and measured cost.

The final policy decision does not depend on model output. A model candidate is evidence
for routing quality, not regulatory authority.

## Cost conflict decision

NFR-4 is a hard ceiling. If the measured routing mix would exceed $0.05 mean cost or
the 40,000/month budget ceiling, the service must reduce reasoning-model usage rather
than violate the budget. The service must not silently increase spend because a model
is more capable.

If the cheap model becomes inaccurate on an application class that cannot safely be
served cheaply, that class must be routed to reasoning or REFERed while the routing
rule is revised.

## Consequences

**Positive:** bounded spend, targeted reasoning, measurable routing.

**Negative:** routing policy requires periodic remeasurement and can increase referral
or reasoning volume after model/policy changes.

## Revisit if...

- *Model Risk Committee:* cheap-model wrong-answer set changes or accuracy
  falls on a material application class.
- *Platform Architecture:* model version changes or p95 latency exceeds
  the NFR-5 budget.
- *Finance/Platform:* verified model pricing changes or projected monthly
  cost threatens the NFR-4 ceiling.

## Status condition

The external benchmark has been executed and is stored in
`artifacts/routing_benchmark.json`.

The benchmark covers all 24 visible applications for both model candidates.
The cheaper candidate achieved 50% accuracy and the reasoning candidate
achieved 100% accuracy.

Model-route cost remains pending because verified provider pricing was not
configured. No synthetic cost figures are reported.
