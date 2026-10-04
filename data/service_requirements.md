# Underwriting Decision Service - Non-Functional Requirements (Synthetic)

> Owned by the Model Risk Committee. Priya Raghunathan (Platform Architecture) and
> the Chief Credit Officer are joint approvers. Neither will sign off on a service
> whose output they cannot reproduce.

## NFR-1 Determinism

The same application must produce the same decision, every time, indefinitely.

This is the requirement the committee cares about most, because an underwriting
decision that cannot be reproduced cannot be defended to a regulator or to the
applicant. Identical input, identical output - including the reasoning recorded
alongside it, not merely the outcome label.

You must be able to demonstrate this, not assert it. State what makes your service
deterministic and what would break it.

## NFR-2 Structured output

Every decision is a structured record validated against a schema before it leaves
the service: the outcome, the factor values used, the band each fell into, the
governing rule, and the reason. A free-text decision is not acceptable.

## NFR-3 Explainability

Every decision must be traceable to the specific guideline provision that produced
it. "The model assessed the application holistically" is not an explanation and
would not survive a complaint.

## NFR-4 Cost

Mean cost per decision **below $0.05**. This is a hard budget: the portfolio runs
roughly 40,000 decisions a month and the committee approved the business case on
that figure.

## NFR-5 Latency

p95 latency **below 2 seconds** per decision. Broker-facing, and brokers abandon.

## NFR-6 Model selection

Justify your model choices with your own measurements. Where you route different
applications to different models, state the routing rule and what it costs.

Reasoning-grade models are available and are substantially more expensive. The
committee's position is that they should be used where they change the answer and
not where they do not - but the committee has not defined which applications those
are, and does not consider that its job.

## NFR-7 Audit

Every decision logs the application id, the model and version, the full input, the
structured output, the latency, the cost, and an immutable timestamp. Sufficient to
reconstruct any decision without re-running it.

## NFR-8 Kill switch and rollback

A documented path to disable the service or revert to a prior model version without
a redeploy. Demonstrate it.

## Where these requirements are silent

NFR-4 sets a hard mean cost ceiling. NFR-6 expects reasoning-grade models where
they change the answer. Those two requirements can conflict on a given month's
mix of applications, and nothing here says which yields. Decide, justify the
decision, and record what the service does when the budget is under pressure.
