# ADR 0008: Treat bindings as generated artifacts and fail CI on drift

- **Status**: Accepted
- **Date**: 2026-06-13
- **Deciders**: Project team

## Context

Once models are generated from the XSD ([ADR 0001](0001-schema-driven-generation-with-xsdata.md)),
the temptation is to "just tweak" a generated file. That is exactly how you get **N drifting
de-facto schemas** — the `write_xml.py` trap, multiplied across languages. The plan's
**Data-as-the-contract** principle requires bindings to stay generated and version-locked to
the schema.

## Decision

We will treat everything under `src/acoustic_dataset/models/` (and any future per-language binding)
as a **generated artifact**:

- Generated files carry a "do not edit" header.
- `ruff`/`mypy` exclude the generated package (it is not hand-maintained code).
- CI **regenerates** from the XSD and fails if the working tree differs, catching any
  hand-edit or stale output.
- The same discipline extends to the generated HTML schema reference and ERD
  ([ADR 0009](0009-mkdocs-material-mermaid-html-docs.md)).

For the drift gate to be reliable rather than flaky, **generation must be byte-reproducible on
the Python 3.9.4 target** ([ADR 0007](0007-pin-python-3-9-4.md)):

- `xsdata` is **pinned to `==25.7`** — the last release line that supports Python 3.9 (26.x
  requires ≥3.10). The drift gate runs on Python 3.9, the same as the rest of CI; there is no
  separate "generation toolchain" Python.
- `make generate` passes explicit `--no-slots --no-kw-only --no-union-type
  --no-postponed-annotations` flags, because xsdata otherwise toggles those by the *running*
  interpreter's version (`config.py` checks `sys.version_info`), which would make the committed
  models depend on who generated them.
- xsdata's docstring wrapping still differs between Python **minor** versions (3.9 vs 3.11), so
  models **must be regenerated on Python 3.9.x** (the devcontainer, or `uv python install
  3.9.4`). The schema-reference generator is pure-Python string building and is version-independent.

## Consequences

### Positive

- Bindings can never silently diverge from the contract.
- Regeneration is the *only* way to change models, which keeps the schema authoritative.
- Reviewers don't waste effort reviewing machine-generated code.

### Negative / trade-offs

- A schema change produces a large generated diff in the PR (noise, but honest).
- Contributors must learn "edit the schema or the mapping, never the models." Documented in
  [Swap in the real schema](../how-to/swap-in-the-real-schema.md).

## Alternatives considered

- **Don't commit generated models at all** (generate at build time only) — viable; rejected
  for now because committing them keeps diffs reviewable and the repo runnable without a
  generation step on every checkout. Revisit if the generated tree becomes unwieldy.
- **Trust contributors not to hand-edit** — rejected: it's the exact failure mode the plan names.

## Notes / revisit triggers

- When real per-language bindings (Java `xjc`, JSON Schema) are added, apply the identical
  generate-and-diff discipline to each.
