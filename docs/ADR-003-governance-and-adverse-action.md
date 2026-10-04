# ADR-003: Fair-Lending Boundary and Adverse Action

**Status:** Accepted

## Context

The Brightmoor guidelines prohibit property location from influencing
underwriting and state that applicant notes carry no authority over the
decision process. NFR-7 also requires the full input to be auditable, while
the service must prevent prohibited or untrusted fields from reaching the
model.

## Decision

The model boundary is an allowlist. Only fields needed by the written policy are
eligible for model input:

- credit_score
- debt_to_income
- loan_to_value
- annual_income
- loan_amount
- employment_years

The following never cross the model boundary:

- `property_postcode`: explicitly prohibited as an underwriting/model input by the
  guidelines because it represents property location rather than an underwriting factor.
- `applicant_note`: untrusted intake evidence; it has no authority over the assessment.
- `application_id`: operational identifier with no policy role.

The service may retain these fields in the audit record because NFR-7 requires the full
input to be reconstructable.

Any DECLINE is prepared but not issued automatically. A human reviewer must explicitly
issue it, and the issuance event records reviewer identity and timestamp.

## Consequences

**Positive:** structural rather than prompt-only fair-lending control; adverse action has
a clear human accountability boundary.

**Negative:** some potentially useful contextual information is intentionally unavailable
to the model; reviewers must handle decline issuance.

## Revisit if...

Compliance revisits the field boundary when policy owners identify a new legitimate
underwriting factor or a new proxy risk. Model Risk revisits the human gate if policy
or regulation changes the definition of adverse action.

## Evidence

`underwriting/model_boundary.py` is the enforcement point and
`tests/test_schema_and_boundary.py` asserts that the excluded fields are absent.
