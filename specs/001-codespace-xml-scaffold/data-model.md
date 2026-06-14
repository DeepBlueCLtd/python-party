# Phase 1 Data Model: Codespace-Ready Repo Scaffold (Phase 1 XML Pipeline)

This describes the conceptual entities that flow through the pipeline and the artifacts the scaffold
manages. Concrete field-level types are owned by the **XSD** (the contract) — the generated models are
only as strongly typed as the schema declares (per the spec's domain-objects note). The placeholder
shapes below are illustrative and replaced wholesale when the real XSD/corpus arrive.

## Pipeline data flow

```text
calculation_input.json   →  [acoustics seams]  →  CalculationResult
CalculationResult        →  [mapping.py: ONE mapping]  →  populated domain objects (generated models)
domain objects           →  [serialize.py]  →  XML text
XML text                 →  [validate.py]  →  (XSD-valid?) + (round-trip equal?)   ← STRUCTURAL GATE
XML text  vs  golden     →  [tests]  →  diff                                       ← SEMANTIC GATE (human)
XML text  vs  reference  →  [compare.py]  →  diff                                  ← MIGRATION SAFETY
{data + schema + models} →  [bundle]  →  distribution bundle
```

## Entities

### Schema (the contract) — `schema/acoustic_dataset.xsd`
- **Represents**: The authoritative, language-agnostic definition of the XML Acoustic Dataset
  structure. Single source of truth.
- **Key content**: Complex/simple types, banded numeric elements, and `xs:annotation/xs:documentation`
  for term/element definitions (which ride through to model docstrings).
- **State**: `PLACEHOLDER` initially (labelled in a leading comment). Replaced in place; everything
  downstream regenerates.
- **Rules**: Must itself be well-formed and parseable; a malformed schema must fail generation loudly
  (edge case), never produce partial/empty models.

### Generated domain models — `src/acoustic_dataset/models/`
- **Represents**: Typed dataclasses produced from the Schema by `xsdata`; the in-memory shape the
  pipeline populates.
- **Attributes**: Derived entirely from the XSD — entity-level modelling is solid, field-level type
  strength only as rich as the XSD declares.
- **Rules**: GENERATED ARTIFACT — never hand-edited (FR-007); reproducible by re-running generation
  (SC-004); carries a "do not edit" header; regeneration drift fails CI (FR-017).

### CalculationResult (example) — produced by `acoustics/` from `examples/calculation_input.json`
- **Represents**: The output of the acoustic calculation seams; the placeholder stand-in for the real
  recalculation/resampling-onto-bands work.
- **Attributes (illustrative)**: a set of named measures keyed by band; numeric, typed in Python.
- **Rules**: Produced by discrete, named, testable seam functions (FR-012); a value that does not fit
  a declared schema band must be surfaced at mapping time, not silently emitted (edge case).

### Populated domain objects (the typed testable boundary)
- **Represents**: Generated-model instances after `mapping.py` has mapped CalculationResult onto them —
  pre-serialisation.
- **Rules**: This is the assertion boundary (FR-010): tests assert directly on these objects and/or on
  the golden-diffed serialised XML. The mapping that produces them is the **one place real logic lives**.

### Emitted XML artifact
- **Represents**: The validated, round-tripped pipeline output — the Phase 1 deliverable and the
  contract Phase 2 will later consume.
- **Rules**: Must pass XSD validation AND round-trip equivalence (FR-009) before being considered good.

### Golden file — `tests/golden/*.xml`
- **Represents**: Trusted expected output for the placeholder pipeline.
- **Rules**: Used by integration tests to detect unintended output changes; updated deliberately, with
  human review (the semantic gate).

### Reference (known-good) file — `examples/reference/*.xml`
- **Represents**: Externally supplied prior-process output (e.g. the consumer's trial files) for migration safety.
- **Rules**: Consumed by `compare.py`; not required to exist for the pipeline to be green; surfaces
  *schema-valid-but-different* differences (FR-015).

### Distribution bundle
- **Represents**: Packaged `data + schema + generated models` shipped together so consumers ingest
  without reverse-engineering the XSD (FR-016).
- **Rules**: Built from a validated run; contains all three; bindings inside are generated, version-
  locked to the included schema.

## Verification gates (cross-cutting)

| Gate | Mechanism | Entity checked | Automated? |
|---|---|---|---|
| Structural — schema validity | `xmlschema` validate vs XSD | Emitted XML | Yes (CI) |
| Structural — round-trip | parse → re-serialise → compare | Emitted XML | Yes (CI) |
| Semantic — correctness | golden-file diff + human judgement | Populated objects / XML | Human gate |
| Migration safety | canonicalised diff vs reference | Emitted XML vs reference | On demand |
| Drift discipline | regenerate + `git diff --exit-code` | Generated models | Yes (CI) |
