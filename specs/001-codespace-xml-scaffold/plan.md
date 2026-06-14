# Implementation Plan: Codespace-Ready Repo Scaffold for Acoustic Reference Book (Phase 1 XML Pipeline)

**Branch**: `claude/zealous-davinci-n4ssvn` | **Date**: 2026-06-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-codespace-xml-scaffold/spec.md`

## Summary

Stand up a GitHub Codespaces-ready repository in which a contributor can, with zero local setup,
run an end-to-end **schema-driven XML pipeline** against a clearly-labelled placeholder schema:
generate typed models from an XSD with `xsdata`, map example calculation output **once** onto those
typed objects, serialise to XML, then validate against the XSD and round-trip. The scaffold
establishes the verification gates (structural vs. semantic), the migration-safety comparison
(catching *schema-valid-but-different*), scientific-seam code organisation, and CI regeneration
discipline the delivery plan calls for — all built so the real XSD/corpus drop into one documented
location without redesign. This plan covers Phase 1 only; Phase 2 and non-Python bindings are
explicitly out of scope and must not be foreclosed.

## Technical Context

**Language/Version**: Python **3.9.4** — pinned exactly to match the target system (devcontainer + CI pin the patch; `ruff`/`mypy` enforce the 3.9 floor). See ADR 0007.

**Primary Dependencies**:
- `xsdata[cli,lxml]` (≥24, supports Python 3.9) — generate typed dataclasses from the XSD; bind objects ↔ XML via `XmlSerializer` / `XmlParser`.
- `xmlschema` — pure-Python XSD validation gate (XSD 1.1 capable; portable, no system libs required).
- `lxml` — fast parsing backend used by xsdata and available for diffing.
- `mkdocs-material` — renders the documentation as an attractive HTML site with native Mermaid (including schema ERDs generated from the enriched XSD). See ADR 0009.

**Storage**: Files only — XSD (the contract), generated model modules, example input data, emitted XML artifacts, golden files, reference files. No database.

**Testing**: `pytest` — unit tests on calculation seams, integration tests asserting on populated domain objects and golden-file XML diffs, a structural-gate test (validate + round-trip), and a migration-safety comparison test.

**Tooling/Quality**: `ruff` (lint + format), `mypy` (type checking on hand-written code, not generated models), `pre-commit` optional. A `Makefile` (or task runner) exposes the single documented commands (`make bootstrap`, `make verify`, `make pipeline`, `make generate`, `make compare`).

**Target Platform**: GitHub Codespaces (devcontainer pinned to Python 3.9.4) as primary; any Linux/macOS with Python 3.9.x as the documented local fallback.

**Project Type**: Single-project Python CLI/library (the pipeline) plus repository infrastructure (devcontainer, CI, docs).

**Performance Goals**: Cold-start to green in under 15 minutes (SC-001); sample pipeline run completes in seconds on placeholder data. No throughput target — the placeholder corpus is small and illustrative.

**Constraints**: Fully runnable offline against the placeholder once provisioned; generated models reproducible and never hand-edited; no real data committed; deferred decisions (Phase 2 tool, Java/JSON bindings, pilot-block choice) must not be designed against.

**Scale/Scope**: One placeholder schema, one example calculation, a handful of acoustic-seam functions, ~4 test categories. Sized as a pilot runway, not a production corpus.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution (`.specify/memory/constitution.md`) is still the unfilled template — no
ratified principles exist yet. In their absence, this plan is gated against the **principles the
delivery plan carries throughout**, treated as de-facto constitution:

| Principle (from delivery plan) | How this plan complies | Gate |
|---|---|---|
| **Configure, don't create** | Models are generated from the XSD by `xsdata`; validation uses off-the-shelf `xmlschema`; no hand-rolled `write_xml.py`. | ✅ Pass |
| **Data as the contract** | The XSD is the single source of truth; models, validation, and bundles derive from it. One documented swap location. | ✅ Pass |
| **Robust across unknowns** | Pure-Python/portable tooling; placeholders isolated and labelled; Codespaces with a local fallback; Phase 2 and extra bindings not foreclosed. | ✅ Pass |
| **Single mapping / typed testable boundary** | Calc output mapped once to typed objects; tests assert on objects and golden XML — no CSV/pickle baton-pass. | ✅ Pass |
| **Two-gate verification** | Structural gate (generate + validate + round-trip) automated in CI; semantic gate (golden file + human sign-off) documented as a human gate. | ✅ Pass |
| **Scientific seams** | Acoustic operations are discrete, named, documented, testable functions in one module early, promoted to packages only when groupings are obvious. | ✅ Pass |

No violations — **Complexity Tracking left empty**. Re-evaluated post-design: still passing (see end of plan).

## Project Structure

### Documentation (this feature)

```text
specs/001-codespace-xml-scaffold/
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI command + schema/XML contracts)
│   ├── cli-commands.md
│   └── pipeline-contract.md
├── checklists/
│   └── requirements.md  # From /speckit-specify
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
.devcontainer/
└── devcontainer.json          # Codespaces: Python 3.11 image, post-create bootstrap, extensions

.github/
└── workflows/
    └── ci.yml                 # Regenerate models from XSD, assert no drift, run pytest, run pipeline

schema/
└── acoustic_dataset.xsd      # PLACEHOLDER schema (clearly labelled); the swap-in location

src/
└── acoustic_dataset/
    ├── __init__.py
    ├── models/                # GENERATED by xsdata — never hand-edited (regen target)
    │   └── .gitkeep
    ├── acoustics/             # Scientific seams: named, documented, testable calc functions
    │   └── __init__.py
    ├── mapping.py             # The ONE place: calc output -> typed domain objects
    ├── serialize.py           # objects -> XML via xsdata XmlSerializer
    ├── validate.py            # structural gate: xmlschema validation + round-trip
    ├── compare.py             # migration-safety: diff generated output vs reference file
    └── cli.py                 # entrypoints: generate / pipeline / validate / compare / bundle

examples/
├── calculation_input.json     # PLACEHOLDER example calculation output (illustrative values)
└── reference/                 # Drop known-good files here for migration-safety comparison
    └── .gitkeep

tests/
├── unit/                      # acoustic seam functions
├── integration/               # populated-object assertions + golden-file XML diff + round-trip
└── golden/                    # golden expected XML

docs/                          # MkDocs Material site (Diátaxis + ADRs); see ADR 0009
├── index.md                   # Site home / reading order
├── tutorials/                 # Learning-oriented (zero-to-green)
├── how-to/                    # Task recipes (use the Codespace, swap the schema, ...)
├── concepts/                  # Explanations (schema-as-contract, two gates, data-flow ERD)
├── decisions/                 # ADRs 0001-0009 (the defensible decision record)
├── reference/                 # Commands + GENERATED schema reference & Mermaid ERD
└── glossary.md

mkdocs.yml                     # Docs site config (Mermaid via pymdownx.superfences)
Makefile                       # bootstrap / verify / docs / generate / gen-schema-docs / pipeline / compare / bundle
pyproject.toml                 # deps (+docs extra), ruff(py39)/mypy(3.9)/pytest config
README.md                      # Top-level orientation pointing at docs/
```

**Structure Decision**: Single Python project (Option 1). The pipeline is one library with a thin CLI;
repository infrastructure (`.devcontainer`, `.github`, `schema`, `examples`, `docs`) wraps it. The
`models/` directory is a generated artifact with a `.gitkeep` and a regeneration target, never
hand-edited (FR-007, FR-017). Placeholders (`schema/`, `examples/`) are isolated top-level so the
real-material swap is obvious and low-cost (FR-011, FR-018). Acoustic seams live in `acoustics/` as
discrete functions, promoted to packages only when groupings are obvious (FR-012).

## Complexity Tracking

> No Constitution Check violations — section intentionally empty.

## Post-Design Constitution Re-check

After Phase 1 design (data-model, contracts, quickstart), all gates still pass: the design keeps a
single mapping boundary, generated-only models, two distinct verification gates, isolated labelled
placeholders, and no foreclosure of deferred decisions. No new complexity introduced.
