# Contract: Schema / XML / Mapping Pipeline

This is the data-contract side of the scaffold: what the schema guarantees, what the pipeline promises
about its output, and the swap procedure for real materials. The **XSD is the contract**; everything
here derives from it.

## Schema contract (placeholder → real)

- The repository contains exactly one authoritative schema at `schema/acoustic_dataset.xsd`.
- The placeholder schema declares a banded, typed numeric structure with `xs:documentation` on terms,
  so it exercises the typed/banded path — not just flat strings.
- **Swap procedure** (the one documented location, FR-011):
  1. Replace `schema/acoustic_dataset.xsd` with the real XSD (keep the path, or update one config key
     in `pyproject.toml` / `Makefile` if the filename differs).
  2. Run `make generate` — models regenerate from the new schema with no code edits.
  3. Update `examples/calculation_input.json` and the golden file to match; run `make verify`.
- No generation code references schema-specific element names; mapping is the only schema-aware code
  and is expected to change when the real schema lands (that is where the real logic belongs).

## Output (emitted XML) contract

A pipeline run that exits 0 guarantees the emitted XML:
1. **Validates** against the current `schema/acoustic_dataset.xsd` (`xmlschema`).
2. **Round-trips**: `serialize(parse(xml)) ≡ xml` under canonicalisation (no binding loss).
3. Was produced by a **single mapping** from `CalculationResult` to typed objects (no intermediate
   CSV/pickle/string re-parse).

Schema-validity alone is explicitly **not** sufficient — the round-trip and (human) semantic gates
also apply.

## Mapping contract (`mapping.py` — the one place logic lives)

- Input: `CalculationResult` (output of the acoustics seams).
- Output: populated instances of the generated domain models.
- Rules:
  - Performs the mapping exactly **once** (no reshape-twice).
  - Surfaces any value that does not fit a declared schema band/type as an error at mapping time
    (before serialisation) — never emits schema-valid-but-wrong XML.
  - Is the documented home of the band/recalculation/resampling logic and its unit tests.

## Documentation homes contract (FR-013)

| Documentation kind | Home | Mechanism |
|---|---|---|
| Definitions of terms/elements | The schema | `xs:annotation/xs:documentation` → generated model docstrings |
| Engineering "how it's computed" | The code | Docstrings on the acoustics seam functions / mapping |

XML comments are NOT used for definitions (discarded at parse time).

## Verification gate contract

| Gate | Pass condition | Where enforced |
|---|---|---|
| Structural: schema validity | `xmlschema` reports valid | `validate` / `pipeline` / CI |
| Structural: round-trip | canonical-equal after parse→serialise | `validate` / `pipeline` / CI |
| Semantic: correctness | golden-file diff clean + human sign-off | integration tests + reviewer |
| Migration safety | canonical-equal vs reference | `compare` (on demand) |
| Drift discipline | regenerate ⇒ no git diff | CI |
