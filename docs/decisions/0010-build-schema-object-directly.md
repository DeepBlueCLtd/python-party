# ADR 0010: Build the schema's data object directly (drop the intermediate domain hierarchy)

- **Status**: Proposed
- **Date**: 2026-06-16
- **Deciders**: Project team (pending stakeholder confirmation of the defensible-process framing)

## Context

The pipeline computes acoustic values and must emit an XML Acoustic Dataset that conforms to
the XSD. Today it does so in two typed hierarchies:

1. The acoustic seams build a **hand-written domain hierarchy** — `CalculationResult`,
   `BandResult`, `SectorResult`, `CharacteristicsResult`, `ActiveSonarResult`,
   `PassiveSonarResult` — holding plain `float`s.
2. A **single mapping** (`mapping.to_model`) then copies that hierarchy onto the
   **schema-generated classes** — `Platform`, `RadiatedBand`, `Directional`, `Sector`,
   `SensorSuite`, `ActiveSonar`, `PassiveSonar` — converting `float → Decimal`, quantising to a
   fixed scale, and range-checking each value (raising `MappingError`) before serialisation.
   This is the "single mapping onto schema-generated objects" of
   [ADR 0002](0002-drop-csv-pickle-and-write_xml.md).

So two typed hierarchies mirror each other: one in the science code, one generated from the
schema. The first exists **only to be converted into** the second.

The force driving this decision is not internal: it is **what the process must be to be
defensible to stakeholders**. The account we can stand behind is *"we build one data object
that meets the schema, and we prove it does."* An intermediate structure that exists solely to
be re-mapped is machinery with no externally visible purpose, and it weakens that account. The
relevant delivery-plan principles — **Data-as-contract** (the schema is the single source of
truth) and the **single typed, testable boundary** — are best served by keeping *one* schema
object and the proof it conforms, not a duplicate hierarchy in front of it.

## Decision

We will have the acoustic calculation **populate the schema-generated data object directly.**

- The orchestration constructs `Platform` / `RadiatedBand` / `Directional` / `Sector` /
  `SensorSuite` / `ActiveSonar` / `PassiveSonar` from the input, applying the schema's
  `float → Decimal` conversion, fixed quantisation, and range-checks **at the point of
  construction**.
- We **delete** the intermediate domain hierarchy: `CalculationResult`, `BandResult`,
  `SectorResult`, `CharacteristicsResult`, `ActiveSonarResult`, `PassiveSonarResult`.
- We **keep the pure calculation functions** — `band_centre_hz`, `spectral_rolloff_db`,
  `directivity_db`, `radiated_level_db`, `active_max_range_m`, `bearings`. These are arithmetic,
  not a data structure; they stay `float`-only and independently unit-tested, and now feed
  construction of the schema object instead of a twin hierarchy.
- We **fold `to_model`'s responsibilities** (Decimal conversion, quantisation, range-check →
  `MappingError`) into the construction step, kept in small named helpers so the rules still
  mirror the XSD facets and the physics stays readable.
- We **preserve both verification gates unchanged**: the constructed object is still validated
  against the XSD (structural gate) and diffed against golden / reference files (semantic and
  migration-safety gates); a range violation is still rejected, with a located error, before
  serialisation.

This **refines [ADR 0002](0002-drop-csv-pickle-and-write_xml.md)** rather than reversing it:
"drop CSV / pickle / `write_xml`, serialise once" stands; the "single mapping *from a separate
calculation-output hierarchy*" becomes "construct the schema object directly." There is still
exactly one place that produces schema-typed objects, and tests still assert on those objects.

## Consequences

### Positive

- The implementation matches the defensible account: one data object, built to meet the schema
  and validated against it. No structure exists solely to be converted.
- Removes an entire parallel typed hierarchy and the copy-pass that mirrored it — less code, and
  no "two structures to keep in step" maintenance when the schema or the calc changes.
- Tests assert on the **actual deliverable** (the schema object), not a stand-in for it.

### Negative / trade-offs

- The calculation code now **imports the schema-generated classes** and the schema's ranges, so a
  schema change can ripple into the builder (previously contained to `mapping.py`). *Mitigation*:
  keep all construction in one builder module so the blast radius stays one file, and lean on
  model regeneration plus the validation gate to surface any mismatch.
- `float → Decimal` conversion and quantisation now sit next to the physics rather than behind a
  boundary; we keep them in small, named helpers so the seam functions remain `float`-only and
  the arithmetic stays legible.
- Part of ADR 0002's wording ("no separate intermediate / single mapping") is superseded; that
  ADR gets a "Refined by ADR 0010" note.

## Alternatives considered

- **Keep the intermediate hierarchy (status quo)** — rejected. Its benefits (decoupling the
  science from the generated classes; one file to touch on a schema change) are *internal*
  engineering conveniences. They do not outweigh a process the stakeholders cannot defend, and
  they cost a duplicated typed hierarchy that must be kept in step.
- **Generate the intermediate from the schema too** (so it is not hand-mirrored) — rejected. It
  removes the hand-duplication but still leaves a second structure whose only job is to be
  converted; it does not simplify the account we have to defend.

## Notes / revisit triggers

- If the schema begins changing frequently and the builder's coupling to the generated classes
  becomes a churn cost, revisit whether a thin mapping layer earns its keep again.
- If the calculation later grows a genuinely different intermediate representation for
  *computational* reasons (e.g. a resampling buffer), that is a different structure from a schema
  mirror and is not precluded here.
