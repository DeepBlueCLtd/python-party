# python-playground

Playground for developing / demonstrating python dev techniques.

This repository hosts **Acoustic Reference Book — Phase 1**: a schema-driven pipeline that turns acoustic
calculation output into validated **XML Acoustic Dataset**, built as a *learning* project
where every decision is documented and defensible.

## Quick start

Open in a **GitHub Codespace** (Code → Codespaces → Create codespace). It provisions
**Python 3.9.4** (matching the target system) and runs `make bootstrap` automatically. Then:

```bash
make verify        # lint + tests — confirm the environment is green
make docs-serve    # browse the docs at http://localhost:8000
```

Working locally instead? You need Python 3.9.x and `make`, then `make bootstrap`. Run `make`
to see all targets.

## Documentation

The full, navigable documentation — tutorials, how-to guides, concepts, decision records
(ADRs), and a Mermaid schema ERD — lives in [`docs/`](docs/index.md) and renders as an
attractive HTML site via MkDocs Material (`make docs`).

**Start here:** [`docs/tutorials/01-start-here.md`](docs/tutorials/01-start-here.md).

## Spec-driven development

This project uses [GitHub Spec Kit](https://github.com/github/spec-kit). The active feature's
specification, plan, and design artifacts are under
[`specs/001-codespace-xml-scaffold/`](specs/001-codespace-xml-scaffold/). Use the
`/speckit-*` skills (`specify`, `plan`, `tasks`, `implement`) to drive development.

## Layout

| Path | What it is |
|---|---|
| `.devcontainer/` | Codespaces environment (Python 3.9.4) |
| `schema/` | The XSD contract (placeholder until the real one lands) |
| `src/acoustic_dataset/` | The pipeline package (`models/` is generated, never hand-edited) |
| `examples/` | Example calculation input + `reference/` known-good files |
| `tests/` | Unit, integration, and golden-file tests |
| `docs/` | The documentation site (MkDocs Material) |
| `specs/` | Spec Kit feature specs, plans, and contracts |
