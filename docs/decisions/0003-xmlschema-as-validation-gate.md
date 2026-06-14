# ADR 0003: Use xmlschema as the structural validation gate

- **Status**: Accepted
- **Date**: 2026-06-13
- **Deciders**: Project team

## Context

Generated objects make the output *conformant by construction*, but the plan is explicit:
**schema-valid is not the same as correct**, and we still want an independent mechanical
check that the emitted XML validates against the XSD. We also value **robustness across
unknowns** — portable, reproducible tooling that runs the same in a Codespace, on a laptop,
and in CI without system-library surprises.

## Decision

We will use the **`xmlschema`** package as the structural validation gate: validate every
emitted document against `schema/acoustic_dataset.xsd`, alongside a round-trip check (see
[ADR 0004](0004-two-gate-verification.md)).

## Consequences

### Positive

- Pure-Python, no system libraries to build → portable and reproducible everywhere.
- Supports XSD 1.1, giving headroom if the real schema uses 1.1 features (assertions, etc.).
- Detailed, line-aware error reporting suitable for a clear pass/fail gate.

### Negative / trade-offs

- Pure-Python validation is slower than a C-based validator on very large documents. For the
  placeholder corpus this is irrelevant; revisit only if real-corpus validation is a bottleneck.

## Alternatives considered

- **`lxml.etree.XMLSchema`** — fast (C/libxml2) but XSD 1.0 only, and ties validation to a
  C-extension build. We keep `lxml` as a parsing backend for `xsdata` but not as the gate.
- **Online / external validators** — not reproducible, not offline-capable; rejected.

## Notes / revisit triggers

- If the real XSD is 1.0-only and the corpus is large, a hybrid (lxml for speed) could be
  reconsidered — but only behind the same gate interface.
