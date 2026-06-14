---
description: "Task list for Codespace-Ready Repo Scaffold (Phase 1 XML Pipeline)"
---

# Tasks: Codespace-Ready Repo Scaffold for Acoustic Reference Book (Phase 1 XML Pipeline)

**Input**: Design documents from `specs/001-codespace-xml-scaffold/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED — the spec requires a typed testable boundary, golden-file diffs, and a
round-trip gate (FR-009, FR-010, FR-014), so test tasks are first-class here.

**Organization**: Tasks are grouped by user story (from spec.md) for independent delivery.

> **Status note**: Phase 1 (Setup) and User Story 1 (zero-to-green) landed first. Phase 2
> (Foundational) and **User Story 2 — the schema-driven pipeline MVP** are now implemented:
> enriched placeholder XSD, xsdata generation (3.9-safe, idempotent), the single mapping, the
> two structural gates, `make generate` / `make pipeline`, and the golden-file tests.
> **User Story 3 — the migration-safety `compare`** and **User Story 5 — the generated schema
> reference & ERD** are now implemented too: a canonicalising comparison (`make compare`) with a
> shipped reference fixture, and an XSD-driven Markdown reference + Mermaid `erDiagram`
> (`make gen-schema-docs`) wired into the docs nav, both with tests. The **remaining work is US4
> (bundle + drift gate)**; the `bundle` CLI subcommand exists but exits non-zero as
> not-yet-implemented.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1–US5 maps to the user stories below
- Exact file paths are included in each task

---

## Phase 1: Setup (Shared Infrastructure) — ✅ COMPLETE

- [X] T001 Create Python project (src layout) and `pyproject.toml` with deps + `requires-python` in `pyproject.toml`
- [X] T002 [P] Configure devcontainer pinned to Python 3.9.4 in `.devcontainer/devcontainer.json`
- [X] T003 [P] Configure ruff (py39), mypy (3.9), pytest in `pyproject.toml`
- [X] T004 Create the `make` command surface (bootstrap/verify/docs/…) in `Makefile`
- [X] T005 [P] Add CI workflow (setup 3.9.4 → bootstrap → verify → strict docs build) in `.github/workflows/ci.yml`
- [X] T006 [P] Stand up MkDocs Material site with Mermaid + learning docs/ADRs in `mkdocs.yml` and `docs/`

---

## Phase 2: Foundational (Blocking Prerequisites) — ✅ COMPLETE

**Purpose**: The schema, the generated models, and the CLI skeleton that every pipeline story needs.

**⚠️ CRITICAL**: US2/US3/US5/US4 cannot begin until this phase is complete.

- [X] T007 [P] Author the enriched **placeholder** XSD (banded, typed numerics + `xs:annotation/xs:documentation` on terms) in `schema/acoustic_dataset.xsd`
- [X] T008 [P] Add the example calculation input (illustrative values) in `examples/calculation_input.json`
- [X] T009 Create the CLI dispatch skeleton (`generate`/`pipeline`/`validate`/`compare`/`bundle` subcommands + `main` for the `acoustic` entry point) in `src/acoustic_dataset/cli.py`
- [X] T010 Implement `generate` via xsdata and wire `make generate` to emit typed dataclasses with a "do not edit" header into `src/acoustic_dataset/models/` in `src/acoustic_dataset/generate.py` (depends on T007)

**Checkpoint**: `make generate` produces models from the placeholder schema; CLI subcommands dispatch.

---

## Phase 3: User Story 1 - Zero-to-running Codespace (Priority: P1) — ✅ COMPLETE

**Goal**: A contributor opens a Codespace and reaches a green test suite with zero manual setup.

**Independent Test**: Fresh Codespace → `make verify` passes with no config edits.

- [X] T011 [US1] Minimal green package + smoke tests (env verifiable before pipeline exists) in `src/acoustic_dataset/__init__.py`, `tests/test_smoke.py`
- [X] T012 [P] [US1] Document zero-to-green + local fallback in `docs/tutorials/01-start-here.md`, `docs/how-to/use-the-codespace.md`

---

## Phase 4: User Story 2 - Schema-driven pipeline skeleton (Priority: P1) 🎯 MVP — ✅ COMPLETE

**Goal**: Map example calc output once onto typed objects → serialise → validate → round-trip.

**Independent Test**: `make pipeline` writes a schema-valid, round-trip-clean XML artifact from the placeholder inputs.

- [X] T013 [P] [US2] Acoustic seams: parse example input → `CalculationResult` as named, documented, testable functions in `src/acoustic_dataset/acoustics/__init__.py`
- [X] T014 [US2] Implement the **single** mapping `CalculationResult` → generated objects, raising on band/type mismatch before serialise, in `src/acoustic_dataset/mapping.py` (depends on T010, T013)
- [X] T015 [US2] Implement serialisation (objects → XML via xsdata `XmlSerializer`) in `src/acoustic_dataset/serialize.py` (depends on T014)
- [X] T016 [US2] Implement the structural gate (xmlschema validation + parse→re-serialise round-trip) in `src/acoustic_dataset/validate.py`
- [X] T017 [US2] Wire `pipeline` subcommand + `make pipeline` (map→serialise→validate→round-trip; write `build/acoustic_dataset.xml` only if both gates pass) in `src/acoustic_dataset/cli.py` (depends on T014–T016)
- [X] T018 [P] [US2] Unit tests for the acoustic seams in `tests/unit/test_acoustics.py`
- [X] T019 [P] [US2] Integration test asserting on populated objects + golden-file XML diff (`tests/golden/acoustic_dataset.xml`) in `tests/integration/test_pipeline.py`
- [X] T020 [US2] Structural-gate test (schema-valid + round-trip equal) in `tests/integration/test_gates.py`

**Checkpoint**: `make pipeline` and `make verify` green on the placeholder schema (SC-002).

---

## Phase 5: User Story 3 - Migration-safety comparison (Priority: P2) — ✅ COMPLETE

**Goal**: Diff generated output against a known-good reference; surface *schema-valid-but-different*.

**Independent Test**: Identical output → clean match (exit 0); schema-valid-but-different → diff + non-zero exit.

- [X] T021 [US3] Implement canonicalise (sort attributes, normalise whitespace/namespaces) + diff in `src/acoustic_dataset/compare.py`
- [X] T022 [US3] Wire `compare` subcommand + `make compare` in `src/acoustic_dataset/cli.py` (depends on T021)
- [X] T023 [P] [US3] Reference fixture in `examples/reference/` + tests (clean match, meaningful diff, cosmetic-only ignored) in `tests/integration/test_compare.py`

**Checkpoint**: `make compare` catches a schema-valid-but-different file (SC-005). ✅

---

## Phase 6: User Story 5 - Generated schema reference & ERD (Priority: P2) [FR-020/021/022] — ✅ COMPLETE

**Goal**: Generate the HTML schema reference + a Mermaid **ERD** *from the enriched XSD*, so docs can't drift.

**Independent Test**: `make gen-schema-docs` then `make docs` renders generated reference pages and an ERD matching the schema.

- [X] T024 [US5] Implement the schema-docs generator (walk the enriched XSD/models → per-type Markdown reference carrying `xs:documentation` + a Mermaid `erDiagram`) into `docs/reference/schema/` in `src/acoustic_dataset/schema_docs.py` (depends on T010)
- [X] T025 [US5] Wire `gen-schema-docs` subcommand + `make gen-schema-docs` in `src/acoustic_dataset/cli.py` (depends on T024)
- [X] T026 [US5] Integrate the generated page into the MkDocs nav (single static `reference/schema/index.md` entry — no extra plugin needed) and replace the hand-drawn stand-in `docs/reference/schema-erd.md` (deleted; all inbound links repointed)
- [X] T027 [P] [US5] Test generator output contains entities, the `xs:documentation` prose, and an `erDiagram` block in `tests/integration/test_schema_docs.py`

**Checkpoint**: HTML site shows a schema ERD generated from the XSD (SC-008, SC-009). ✅

---

## Phase 7: User Story 4 - Distribution bundle & regeneration discipline (Priority: P3)

**Goal**: Ship data + schema + models together; CI fails on any generated-artifact drift.

**Independent Test**: `make bundle` yields a bundle with all three; a hand-edited model fails CI.

- [ ] T028 [US4] Implement the bundle (assemble data + schema + generated models) + wire `bundle`/`make bundle` in `src/acoustic_dataset/bundle.py`, `src/acoustic_dataset/cli.py`
- [ ] T029 [US4] CI drift gate: regenerate models AND schema docs, then fail on `git diff --exit-code` in `.github/workflows/ci.yml`
- [ ] T030 [P] [US4] Test the bundle contains data + schema + models in `tests/integration/test_bundle.py`

**Checkpoint**: bindings and generated docs are version-locked to the schema (FR-016, FR-017).

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T031 [P] Add `mypy` to `make verify` now that hand-written pipeline code exists in `Makefile`
- [ ] T032 Run the `quickstart.md` scenarios end-to-end and fix any gaps
- [ ] T033 [P] When the real XSD lands, follow `docs/how-to/swap-in-the-real-schema.md` and mark ADR 0005 **Superseded** in `docs/decisions/0005-placeholder-schema-runnable-now.md`
- [ ] T034 [P] Tidy docs cross-links/glossary for the new generated reference pages in `docs/`

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)** ✅ done.
- **Foundational (Phase 2)** — blocks all remaining stories. T007/T008 are [P]; T009 [P] with them; T010 depends on T007.
- **US2 (Phase 4)** — the MVP; depends on Phase 2.
- **US3 (Phase 5)**, **US5 (Phase 6)** — depend on Phase 2; both build on US2's output but are independently testable. US5 also depends on T010 (generated models).
- **US4 (Phase 7)** — depends on Phase 2; the CI drift gate (T029) is most meaningful after T010 and T024 exist.
- **Polish (Phase 8)** — after the stories it touches.

### Within each story

- Tests for a story marked [P] can run in parallel.
- Mapping (T014) before serialise (T015) before the pipeline wiring (T017).

### Parallel opportunities

- Foundational: T007, T008 in parallel; T009 alongside.
- US2: T013 ∥ (after T014–T016) T018, T019 in parallel.
- Cross-story: once Phase 2 is done, US3, US5, and US4 can proceed in parallel by different people.

---

## Parallel Example: User Story 2

```bash
# After T014–T016 land, run the US2 tests in parallel:
Task: "Unit tests for acoustic seams in tests/unit/test_acoustics.py"          # T018
Task: "Integration + golden-diff test in tests/integration/test_pipeline.py"   # T019
```

---

## Implementation Strategy

### MVP first

1. Phase 2 (Foundational): schema + generation + CLI skeleton.
2. Phase 4 (US2): the end-to-end pipeline on the placeholder schema.
3. **STOP and VALIDATE**: `make pipeline` + `make verify` green → this is the Phase 1 MVP.

### Incremental delivery

US2 (MVP) → US3 (migration safety) → US5 (generated schema docs/ERD) → US4 (bundle + drift gate),
each an independently testable, demoable increment. The real-schema swap (T033) supersedes the
placeholder once it arrives.

---

## Notes

- `[P]` = different files, no dependencies. `[Story]` ties a task to a user story for traceability.
- Generated artifacts (`src/acoustic_dataset/models/`, `docs/reference/schema/`) are **never** hand-edited — regenerate (ADR 0008).
- Commit after each task or logical group; keep `make verify` green.
- Total: 34 tasks — 27 already complete (`[X]`), 7 remaining (the pipeline).
