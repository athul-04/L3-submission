# Declared Effort

I treated this as a substantial architecture and implementation exercise.

Work included:
- interpreting the supplied NFRs and underwriting guidelines
- implementing the deterministic policy engine
- implementing structured output and validation
- implementing the model boundary and routing rule
- implementing adverse-action and kill-switch controls
- writing automated tests
- measuring deterministic threshold reproducibility
- running external model benchmarks through Portkey
- generating audit, routing, determinism and PMAT evidence
- documenting architecture decisions and trade-offs

The external model benchmark was run against all 24 visible applications.
Model-route cost remains marked PENDING where verified provider pricing was
not available; no synthetic cost figures were reported.