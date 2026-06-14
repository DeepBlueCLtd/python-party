# ADR 0005: Ship a labelled placeholder schema so the pipeline runs today

- **Status**: Accepted (provisional — replaced by the real XSD when it lands)
- **Date**: 2026-06-13
- **Deciders**: Project team

## Context

The delivery plan records the mature XSD as "in hand," but at the time of building this
scaffold **we have no materials** — no schema, no corpus, no calculation. The critical path
is external (the conversation with the author). The plan's principle is to favour
**reversible moves that keep the release moving** and pay off across the ways the unknowns
resolve. A scaffold nobody can run teaches nothing and validates nothing.

## Decision

We will author a small but representative **placeholder** `schema/acoustic_dataset.xsd`
(a banded, typed numeric structure with `xs:documentation` on terms) and a matching example
calculation, both **clearly labelled as placeholders**, so the whole pipeline — generate →
map → serialise → validate → round-trip — is demonstrably runnable now. The schema sits at a
single documented swap location (see [the how-to](../how-to/swap-in-the-real-schema.md)).

## Consequences

### Positive

- The approach (xsdata, the two gates, the docs/ERD generation) is *proven* before the real
  XSD arrives — de-risking the first real pilot.
- New contributors get a green, runnable system on day one
  ([ADR 0006](0006-codespaces-with-local-fallback.md)).
- The placeholder deliberately includes the *hard half* (a banded/typed numeric, not flat
  strings) so it exercises the rebanding path the real corpus will need.

### Negative / trade-offs

- Risk that the placeholder's shape subtly biases the design toward itself. Mitigated by
  isolating it to `schema/` + `examples/` and keeping generation schema-agnostic, so swapping
  is a config change, not a redesign.
- Two artefacts to replace later (schema + example), plus the golden file.

## Alternatives considered

- **Empty stub schema** — rejected: the pipeline wouldn't run, so it couldn't validate the
  approach (fails the "runnable now" goal).
- **Wait for the real XSD** — rejected: stalls everything on the external critical path and
  leaves the toolchain unproven.
- **Copy a real schema** — rejected: none available, and would risk
  committing real content.

## Notes / revisit triggers

- When the real XSD arrives, follow the swap how-to; this ADR is then **superseded** by the
  reality of the real contract, and the placeholder is deleted.
