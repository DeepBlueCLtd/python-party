# ADR 0004: Verify with two gates — structural (mechanical) and semantic (human)

- **Status**: Accepted
- **Date**: 2026-06-13
- **Deciders**: Project team

## Context

There are two genuinely different questions about an emitted document:

1. *Is it well-formed and schema-conformant, and does it survive a round trip?* — mechanical,
   automatable.
2. *Is the underlying recalculation/resampling onto schema bands actually right?* — a matter
   of acoustic judgement that no schema can answer.

Conflating them is how *schema-valid-but-wrong* output slips through. The plan names both and
keeps them separate, with correctness living **upstream in the calculation**.

## Decision

We will operate **two distinct gates**:

- **Structural gate (mechanical):** conformant-by-construction generation + `xmlschema`
  validation ([ADR 0003](0003-xmlschema-as-validation-gate.md)) + a parse→re-serialise
  round-trip check. Runs automatically in CI.
- **Semantic gate (human judgement):** golden-file review plus expert sign-off on whether
  the science is right. Stays a human gate; the correctness lives in the calculation, not the
  serialisation.

## Consequences

### Positive

- Each gate does one job, so neither masks the other.
- The automatable half is fully in CI; the judgement half is explicit and owned by a person.
- A domain expert signs off a well-named function or a golden diff — not a 500-line script.

### Negative / trade-offs

- The semantic gate cannot be fully automated; it needs an expert in the loop and good golden
  files. That is a deliberate cost, not a gap to "fix" with more validation.

## Alternatives considered

- **Treat schema-validity as sufficient** — explicitly the failure mode the plan warns against.
- **Try to encode all semantic correctness in the XSD** — impossible; the schema knows nothing
  about the calculation. Engineering "how it's computed" lives in code, definitions in the schema.

## Notes / revisit triggers

- Some semantic checks may later be promotable to automated property tests (e.g. monotonicity,
  band coverage). When a judgement becomes a stable rule, move it into the structural gate.
