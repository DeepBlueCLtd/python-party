# Contract: CLI Commands & Make Targets

The scaffold's external interface is a small set of commands. Each Make target wraps a CLI subcommand
so onboarding has a stable surface independent of internal module layout. This is the contract that
tests and CI depend on; command names and exit-code semantics must remain stable.

## Make targets (documented onboarding surface)

| Target | Wraps | Purpose | Success exit | Failure exit |
|---|---|---|---|---|
| `make bootstrap` | install deps + `make generate` | One-time/Codespaces provisioning (run by devcontainer `postCreateCommand`). | 0 | non-zero if deps or generation fail |
| `make generate` | `python -m acoustic_dataset.cli generate` | Regenerate models from `schema/*.xsd` via xsdata. | 0 | non-zero on malformed/missing schema |
| `make pipeline` | `python -m acoustic_dataset.cli pipeline` | End-to-end: map example input → objects → XML → validate → round-trip; writes artifact. | 0 + artifact written | non-zero if validation or round-trip fails |
| `make verify` | `pytest` (+ optional lint/type) | Run the full test suite; the single "is the environment good?" command. | 0 | non-zero on any test failure |
| `make compare` | `python -m acoustic_dataset.cli compare <generated> <reference>` | Migration-safety diff vs a known-good reference. | 0 on clean match | non-zero (and prints diff) on meaningful difference |
| `make bundle` | `python -m acoustic_dataset.cli bundle` | Produce distribution bundle (data + schema + models). | 0 + bundle written | non-zero on incomplete bundle |

## CLI subcommands (`python -m acoustic_dataset.cli ...`)

### `generate`
- **Input**: `--schema schema/acoustic_dataset.xsd` (default), `--out src/acoustic_dataset/models`.
- **Behaviour**: Invoke xsdata generation; write generated dataclasses with a "do not edit" header.
- **Contract**: Idempotent — re-running on an unchanged schema produces byte-identical output (enables
  the CI drift check `git diff --exit-code`). Malformed/missing schema → exit non-zero with an
  actionable message; never writes partial output.

### `pipeline`
- **Input**: `--input examples/calculation_input.json` (default), `--out build/acoustic_dataset.xml`.
- **Behaviour**: acoustics seams → `CalculationResult` → single mapping → populated objects →
  serialise → validate (xmlschema) → round-trip check. Writes artifact only if both structural gates pass.
- **Contract**: Exit 0 ⇔ artifact written AND schema-valid AND round-trip-equal. A band/type mismatch
  in mapping → exit non-zero before writing (no schema-valid-but-wrong output).

### `validate`
- **Input**: `--xml <path>` `--schema <path>`.
- **Behaviour**: Run the structural gate (XSD validation + round-trip) on an existing XML file.
- **Contract**: Exit 0 ⇔ valid and round-trip-equal; otherwise prints line-aware errors, exit non-zero.

### `compare`
- **Input**: positional `<generated.xml> <reference.xml>`.
- **Behaviour**: Canonicalise both (sort attributes, normalise whitespace/namespaces), diff.
- **Contract**: Exit 0 ⇔ canonical-equal (clean match); meaningful difference → print human-readable
  diff, exit non-zero. Cosmetic-only differences (attribute order, whitespace) MUST NOT cause failure.

### `bundle`
- **Input**: `--out build/dist/`.
- **Behaviour**: Assemble data + schema + generated models into a bundle directory/archive.
- **Contract**: Exit 0 ⇔ bundle contains all three; missing any component → exit non-zero.

## Stability notes

- Command names, argument names, and exit-code semantics are the contract — tests and CI bind to them.
- Internal module names (`mapping.py`, `serialize.py`, …) are NOT part of the contract and may change.
