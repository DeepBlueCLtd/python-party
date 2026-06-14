# Commands

> **Reference** — the stable command surface. Authoritative contract:
> `specs/001-codespace-xml-scaffold/contracts/cli-commands.md`.

## Make targets

| Target | Purpose | Status |
|---|---|---|
| `make help` | List targets | ✅ |
| `make bootstrap` | Install deps (dev + docs); run by the devcontainer | ✅ |
| `make verify` | Lint (`ruff`) + tests (`pytest`) | ✅ |
| `make docs` | Build static HTML site (`mkdocs build --strict`) → `site/` | ✅ |
| `make docs-serve` | Live-preview docs at <http://localhost:8000> | ✅ |
| `make generate` | Regenerate models from `schema/*.xsd` via `xsdata` | ✅ |
| `make gen-schema-docs` | Generate schema reference + Mermaid ERD from the enriched XSD | ✅ |
| `make pipeline` | End-to-end: map → serialise → validate → round-trip | ✅ |
| `make compare` | Migration-safety diff vs a known-good reference | ✅ |
| `make bundle` | Distribution bundle (data + schema + models) | ⏳ Phase 1 task |

The remaining ⏳ target (`make bundle`, User Story 4) currently prints a pointer to
`specs/001-codespace-xml-scaffold/tasks.md` and exits non-zero.

## CLI subcommands

`python -m acoustic_dataset.cli <command>` (and the `acoustic` entry point). Each maps to a make target
above; full input/exit-code semantics are in the contract file. Summary:

| Command | Exit 0 means | Non-zero means |
|---|---|---|
| `generate` | Models regenerated (idempotent) | Malformed/missing schema (no partial write) |
| `pipeline` | Artifact written, schema-valid, round-trip-equal | Validation/round-trip/mapping failure |
| `validate` | XML valid + round-trips | Invalid or lossy (prints line-aware errors) |
| `compare` | Canonical match with reference | Meaningful difference (prints diff) |
| `bundle` | Bundle has data + schema + models | A component is missing |

## Tooling versions

- **Python**: 3.9.4 (pinned — [ADR 0007](../decisions/0007-pin-python-3-9-4.md))
- **xsdata**: ≥ 24 · **xmlschema**: ≥ 3 · **mkdocs-material**: ≥ 9.5
- Lint/type floors: `ruff target-version = py39`, `mypy python_version = 3.9`
