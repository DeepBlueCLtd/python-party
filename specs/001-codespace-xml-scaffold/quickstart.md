# Quickstart / Validation Guide: Codespace-Ready Repo Scaffold (Phase 1)

This guide proves the scaffold works end to end. It is a **run/validation** guide — implementation
detail lives in `tasks.md` and the code itself. Commands map to the contract in
[`contracts/cli-commands.md`](./contracts/cli-commands.md).

## Prerequisites

- A GitHub account (for the Codespaces path), **or** Python 3.9.x + `make` locally (fallback path).
- No other local tooling required — provisioning installs everything.

## Path A — GitHub Codespaces (primary)

1. On the repository page, **Code → Codespaces → Create codespace**.
2. Wait for provisioning. The devcontainer's `postCreateCommand` runs `make bootstrap` (installs
   dependencies and generates models from the placeholder schema). *(Validates US1 / FR-001, FR-002.)*
3. When the terminal is ready, run the single verify command:
   ```bash
   make verify
   ```
   **Expected**: the test suite runs to completion and reports a pass. *(Validates FR-003, SC-001.)*

## Path B — Local fallback (portability)

```bash
make bootstrap   # install deps + generate models
make verify      # run the full test suite -> expected: pass
```
**Expected**: identical green state to the Codespace. *(Validates US1 / FR-004, SC-001.)*

## Scenario 1 — End-to-end pipeline on the placeholder schema

```bash
make pipeline
```
**Expected**: a validated XML artifact (e.g. `build/acoustic_dataset.xml`) is written; the run reports
success after passing XSD validation and the round-trip check. *(Validates US2 / FR-006–FR-010, SC-002.)*

## Scenario 2 — Swap the schema, no code edits

```bash
# Replace schema/acoustic_dataset.xsd with a different/updated XSD, then:
make generate    # models regenerate from the new schema
make pipeline    # pipeline runs against the new contract
```
**Expected**: models and output regenerate with no edits to generation code. *(Validates US2 / FR-011, SC-003.)*

## Scenario 3 — Typed testable boundary

```bash
make verify   # runs tests in tests/integration/
```
**Expected**: tests assert on populated domain objects and diff serialised XML against a golden file.
*(Validates US2 / FR-010.)*

## Scenario 4 — Migration safety (schema-valid-but-different)

```bash
# Drop a known-good prior-process file into examples/reference/, then:
make pipeline
python -m acoustic_dataset.cli compare build/acoustic_dataset.xml examples/reference/<file>.xml
```
**Expected**: identical output → clean match (exit 0); output that is schema-valid but differs from the
reference → a clear human-readable diff and non-zero exit. *(Validates US3 / FR-015, SC-005.)*

## Scenario 5 — Drift discipline (CI)

Open a PR that hand-edits a file under `src/acoustic_dataset/models/`.
**Expected**: CI regenerates from the schema and fails on the drift, proving bindings stay
version-locked to the schema. *(Validates US4 / FR-017.)*

## Scenario 6 — Distribution bundle

```bash
make bundle
```
**Expected**: a bundle containing data + schema + generated models together. *(Validates US4 / FR-016.)*

## Where things live (orientation)

- The contract: `schema/acoustic_dataset.xsd` (PLACEHOLDER — swap here).
- The one place logic lives: `src/acoustic_dataset/mapping.py`.
- Scientific seams: `src/acoustic_dataset/acoustics/`.
- The source plan & design artifacts: `specs/001-codespace-xml-scaffold/` (`spec.md`, `plan.md`).
- Onboarding entry point: `docs/onboarding.md` (also the tutorial `docs/tutorials/01-start-here.md`).

*(SC-007: a second contributor should reach green and locate these using only `docs/onboarding.md`.)*
