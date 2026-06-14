# Feature Specification: Codespace-Ready Repo Scaffold for Acoustic Reference Book (Phase 1 XML Pipeline)

**Feature Branch**: `claude/zealous-davinci-n4ssvn`

**Created**: 2026-06-13

**Status**: Draft

**Input**: User description: "Create repo materials so the Acoustic Reference Book delivery plan can be progressed using GitHub Codespaces. There is currently no schema or materials — everything must be created. The feature is the repository scaffolding/working environment itself (a Codespace-ready repo) that lets a contributor start executing the plan in the attached delivery-plan.md, focusing on Phase 1 (the schema-driven XML production pipeline using xsdata) as the first concrete target."

## Overview

The Acoustic Reference Book delivery plan describes a schema-driven production line for emitting Sonar
Performance XML (Phase 1), feeding a later consolidated document (Phase 2). Today there is
**no repository scaffolding, no schema, and no working materials** — only the plan. Substantive
work is also gated on external inputs (the conversation with the author, the real XSD and
corpus), so the plan explicitly favours **reversible, portable moves that pay off across the range
of ways the unknowns resolve**.

This feature delivers the **working environment** itself: a repository a contributor can open in a
GitHub Codespace and, within minutes, run an end-to-end schema-driven XML pipeline against a clearly
labelled **placeholder** schema and example calculation. It establishes the seams, the verification
gates, and the regeneration discipline the plan calls for, so that when the real schema and corpus
arrive they drop into an existing, tested structure rather than triggering a fresh start.

The scaffold is the **pilot block's runway**, not the pilot block itself: it makes the first real
end-to-end pilot cheap to attempt, and doubles as the place the bottleneck analysis will happen.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Zero-to-running environment in a Codespace (Priority: P1)

A contributor with only a GitHub account opens the repository in a GitHub Codespace. The environment
provisions itself automatically — language runtime, the schema-binding tool, validation tooling, and
test runner are all present — and the contributor can immediately run the test suite and a sample
pipeline command that produces a validated XML file, without any manual setup, README archaeology, or
"works on my machine" troubleshooting.

**Why this priority**: This is the MVP and the whole point of the request. Until a contributor can
go from a cold repository to a green, runnable pipeline with no local setup, nothing else in the plan
can be progressed collaboratively. Every later story builds on this environment.

**Independent Test**: Launch a fresh Codespace from the repository, wait for provisioning to finish,
run the documented "verify everything" command, and confirm the test suite passes and a sample XML
artifact is produced and validates — all without editing any environment configuration.

**Acceptance Scenarios**:

1. **Given** a contributor with no local tooling installed, **When** they open the repository in a GitHub Codespace, **Then** the development environment finishes provisioning with all required tools available and no manual install steps.
2. **Given** a freshly provisioned Codespace, **When** the contributor runs the single documented bootstrap/verify command, **Then** the test suite runs to completion and reports pass/fail clearly.
3. **Given** a freshly provisioned Codespace, **When** the contributor runs the documented sample pipeline command, **Then** a schema-valid XML file is produced from example inputs and the run reports success.
4. **Given** the repository on a machine that is not a Codespace, **When** a contributor follows the documented local fallback, **Then** they can reach the same green state, confirming the environment is portable and not Codespace-locked.

---

### User Story 2 - Schema-driven pipeline skeleton with a swappable schema (Priority: P1)

A contributor follows the Phase 1 path end to end against a placeholder schema: a schema definition
exists in the repository, typed domain models are generated from it, example calculation output is
mapped **once** onto those typed objects, the objects are serialised to XML, and the result is
validated against the schema and round-tripped. The placeholder schema and example calculation are
clearly marked as replaceable, and there is one documented, obvious place to drop in the real schema
when it arrives.

**Why this priority**: This is the concrete Phase 1 target named in the request and the part of the
plan that proves the schema-driven approach works. It must be runnable now (against a placeholder) so
the approach is validated before the real XSD lands, and structured so swapping in the real schema is
a configuration change, not a redesign.

**Independent Test**: Run the model-generation step against the placeholder schema, run the mapping
and serialisation step on example calculation output, and confirm the emitted XML validates against
the schema and survives a parse-and-re-serialise round trip with no loss.

**Acceptance Scenarios**:

1. **Given** a schema definition in the repository, **When** the contributor runs the model-generation step, **Then** typed domain models are produced as generated artifacts (not hand-written) and the step is repeatable.
2. **Given** generated models and example calculation output, **When** the contributor runs the mapping step, **Then** the output is mapped once onto typed objects with no intermediate stringified hand-off (no CSV/pickle baton-pass).
3. **Given** populated domain objects, **When** they are serialised, **Then** the resulting XML validates against the schema and round-trips (parse → re-serialise) without semantic loss.
4. **Given** the populated objects before serialisation, **When** tests run, **Then** assertions are made directly on the typed objects and/or the serialised XML is diffed against a golden file, demonstrating a typed, testable boundary.
5. **Given** a different (e.g. updated) schema is dropped into the documented location, **When** generation and the pipeline are re-run, **Then** models and output regenerate from the new schema without editing generation code.

---

### User Story 3 - Migration-safety / golden-file verification harness (Priority: P2)

A contributor can place a known-good reference XML file (for example, a trial file produced by the
old hand-rolled process) into a reference location and run a comparison that reports any differences
between the new generator's output and that reference — distinguishing "schema-valid and matching"
from the dangerous "schema-valid but different" case the plan calls out.

**Why this priority**: The plan names *schema-valid-but-different* as the failure mode to catch before
trusting the new generator against real consumers. It is essential for the eventual real migration but
not required for the environment to be usable, so it ranks below the two P1 stories.

**Independent Test**: Drop a reference XML file into the reference location, run the comparison
command against freshly generated output, and confirm meaningful differences are reported clearly
(and that identical output reports a clean match).

**Acceptance Scenarios**:

1. **Given** a reference XML file and freshly generated output, **When** the contributor runs the comparison, **Then** a clear, human-readable diff of meaningful differences is reported.
2. **Given** generated output identical to the reference, **When** the comparison runs, **Then** it reports a clean match.
3. **Given** output that validates against the schema but differs from the reference, **When** the comparison runs, **Then** the difference is surfaced rather than silently passing.

---

### User Story 4 - Distribution bundle and regeneration discipline (Priority: P3)

A contributor can produce a distributable bundle that ships **data + schema + generated models
together**, and the repository's automation regenerates all bindings from the schema on every schema
change so bindings can never silently drift from the contract.

**Why this priority**: The plan treats the schema as the language-agnostic contract and insists
bindings stay generated and version-locked. This matters for exploitation but is downstream of having
a working pipeline, so it is the lowest priority for this scaffold.

**Independent Test**: Trigger the bundle step and confirm the output contains the schema, the data,
and the generated models together; change the schema and confirm automation regenerates bindings and
fails if a hand-edited or stale binding is detected.

**Acceptance Scenarios**:

1. **Given** a validated pipeline run, **When** the contributor produces the distribution bundle, **Then** the bundle contains the data, the schema, and the generated models together.
2. **Given** a change to the schema, **When** the repository automation runs, **Then** bindings are regenerated from the schema and a stale or hand-edited binding causes a clear failure.

---

### Edge Cases

- **No real schema yet**: The environment must be fully runnable using the labelled placeholder schema; nothing about being green should depend on the real XSD existing.
- **Schema that does not validate / malformed schema**: Generation and validation steps must fail loudly with an actionable message, not produce empty or partial models silently.
- **Calculation output that does not fit the schema** (e.g. a value outside a declared band): The mapping step must surface the mismatch rather than emitting schema-valid-but-wrong XML.
- **Round-trip loss**: If parse-and-re-serialise changes the XML in a meaningful way, the round-trip gate must fail rather than pass.
- **Codespace provisioning failure or slow cold start**: The contributor must get clear feedback on provisioning status and a documented way to re-run provisioning.
- **Schema-valid-but-different vs reference**: The comparison harness must not let a difference from a trusted reference pass merely because the new output is itself schema-valid.
- **Contributor on a constrained network**: Environment provisioning and tooling installation should be documented and, where feasible, resilient so a contributor is not blocked by transient access issues.

## Requirements *(mandatory)*

### Functional Requirements

**Environment & onboarding**

- **FR-001**: The repository MUST provide a one-click GitHub Codespaces configuration that provisions a complete, ready-to-use development environment with no manual setup steps.
- **FR-002**: Provisioning MUST install and make available the language runtime, the schema-to-model binding tool, schema validation tooling, and the test runner needed to run the Phase 1 pipeline.
- **FR-003**: The repository MUST provide a single documented command that verifies the environment by running the test suite and reporting clear pass/fail status.
- **FR-004**: The repository MUST provide a documented local (non-Codespace) path to reach the same green state, so the environment is portable and not locked to Codespaces.
- **FR-005**: The repository MUST include top-level documentation that orients a new contributor: how to open the Codespace, how to verify it, how to run the sample pipeline, and where the plan and key seams live.

**Phase 1 pipeline skeleton**

- **FR-006**: The repository MUST include a clearly labelled **placeholder** schema definition that represents a Sonar-Performance-style structure closely enough to exercise the pipeline end to end.
- **FR-007**: The repository MUST generate typed domain models from the schema as **generated artifacts** that are never hand-edited.
- **FR-008**: The pipeline MUST map example calculation output **once** onto the typed domain objects, with no intermediate stringified hand-off (explicitly no CSV staging file and no pickle baton-pass).
- **FR-009**: The pipeline MUST serialise the populated domain objects to XML, validate the result against the schema, and round-trip it (parse → re-serialise) as two distinct structural gates.
- **FR-010**: The repository MUST expose the populated, pre-serialisation domain objects as a typed, testable boundary, with tests that assert on those objects and/or diff serialised XML against a golden file.
- **FR-011**: The repository MUST provide one documented, obvious location and procedure for replacing the placeholder schema (and example calculation) with the real ones, such that swapping the schema and re-running regenerates models and output without editing generation code.
- **FR-012**: Calculation/mapping logic MUST be organised along scientific seams as named, documented, individually testable units (discrete functions/modules), rather than a single monolithic script.
- **FR-013**: Term/element definitions MUST live in the schema as schema-level documentation (so they ride through to generated model docstrings), while engineering "how it's computed" notes live with the calculation code — the spec must establish both homes.

**Verification & migration safety**

- **FR-014**: The repository MUST distinguish the two verification gates: structural (mechanical/automatable — generation, schema validation, round-trip) and semantic (human + golden-file judgement on whether recalculation/resampling onto schema bands is correct).
- **FR-015**: The repository MUST provide a migration-safety comparison that diffs newly generated output against a contributor-supplied known-good reference file and surfaces meaningful differences (catching schema-valid-but-different).

**Distribution & discipline**

- **FR-016**: The repository MUST support producing a distribution bundle that ships data + schema + generated models together.
- **FR-017**: Repository automation MUST regenerate bindings from the schema on every schema change and MUST fail if a binding is stale or hand-edited, keeping bindings version-locked to the schema.

**Documentation & schema reference (HTML + ERD)**

- **FR-020**: The repository MUST render its documentation (tutorials, how-to guides, concepts, decision records) as an attractive, navigable **HTML site** produced from portable Markdown, buildable with a single documented command and in CI.
- **FR-021**: The documentation MUST support **Mermaid diagrams**, including at least one **entity-relationship diagram (ERD)** of the schema's entities and relationships.
- **FR-022**: The schema reference pages and the schema ERD MUST be **generated from the enriched XSD** (its `xs:documentation` annotations), as generated artifacts that are never hand-maintained, so they cannot drift from the contract.

**Robustness across unknowns**

- **FR-018**: All scaffold artifacts that stand in for not-yet-available real materials (schema, calculation, reference files) MUST be clearly marked as placeholders and isolated so replacing them is low-cost and does not require restructuring.
- **FR-019**: The scaffold MUST avoid foreclosing deferred decisions named in the plan (Phase 2 publishing tool, which language bindings ultimately matter, whether Frictionless has a supplier-input role) — these are out of scope for this feature but must not be designed against.

### Key Entities *(include if feature involves data)*

- **Schema (the contract)**: The authoritative, language-agnostic definition of the XML Acoustic Dataset structure, including embedded term/element definitions. Present initially as a labelled placeholder; the single source of truth from which models, validation, and bindings derive.
- **Generated domain models**: Typed entities produced from the schema; the in-memory representation the pipeline populates. Always regenerated, never hand-edited.
- **Calculation output (example)**: Representative input numbers/structures that the mapping step turns into populated domain objects; a placeholder standing in for the real acoustic calculation results.
- **Populated domain objects**: The pre-serialisation, typed, testable boundary of the pipeline — the object graph asserted on by tests.
- **Emitted XML artifact**: The validated, round-tripped output of the pipeline; the Phase 1 deliverable and the contract Phase 2 will later consume.
- **Golden file**: A trusted expected-output XML used to detect unintended changes in pipeline output.
- **Reference (known-good) file**: An externally supplied prior-process output used by the migration-safety comparison to catch schema-valid-but-different output.
- **Distribution bundle**: The packaged combination of data + schema + generated models shipped to consumers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A contributor with only a GitHub account and no local tooling can go from opening the repository to a passing test suite and a produced, validated sample XML artifact in under 15 minutes, with zero manual environment configuration.
- **SC-002**: The end-to-end sample pipeline (generate models → map → serialise → validate → round-trip) runs successfully on the placeholder schema with a single documented command.
- **SC-003**: Replacing the placeholder schema with a different schema and re-running the pipeline requires no edits to generation code — only dropping the new schema into the documented location and re-running.
- **SC-004**: 100% of generated model files are reproducible from the schema by re-running generation, and no generated file requires manual editing to make the pipeline pass.
- **SC-005**: The migration-safety comparison correctly reports a clean match for identical output and surfaces at least one meaningful difference for output that validates against the schema but differs from a supplied reference.
- **SC-006**: Every placeholder artifact (schema, example calculation, reference) is discoverable as such (clearly labelled) and can be replaced without restructuring the repository.
- **SC-007**: A second contributor, given only the top-level documentation, can independently reproduce the green state and locate where the real schema, the calculation seams, and the plan live, without assistance.
- **SC-008**: The documentation builds to an HTML site with a single command (and in CI) and renders at least one Mermaid ERD of the schema; a strict build fails on any broken internal link.
- **SC-009**: Swapping in a different enriched schema and regenerating produces an updated schema reference and ERD with no hand-editing of documentation.

## Assumptions

- **Codespaces is the primary target**, with a documented local fallback; the environment is built to be portable rather than Codespace-locked (per the plan's robustness-across-unknowns principle).
- **The scaffold ships a runnable placeholder schema and example calculation.** Although the plan records the real XSD as "in hand," the contributor currently has no materials, so an illustrative, clearly-labelled placeholder is included so the pipeline is demonstrably runnable now and the approach can be validated before the real schema lands.
- **Python with `xsdata` is the binding stack for this scaffold's MVP**, consistent with the plan's named Phase 1 toolchain. Other bindings (Java/`xjc`, JSON Schema for JS/TS) are acknowledged by the plan but are out of scope for this feature and are not designed against.
- **The target system is constrained to exactly Python 3.9.4**; the development environment and CI pin that patch so "runs in dev/CI" implies "runs on the target." Tooling (`ruff`/`mypy`) enforces 3.9 compatibility.
- **HTML documentation is produced with MkDocs Material (with Mermaid)**; this concerns developer/consumer *schema* documentation and the learning docs, and is distinct from — and does not foreclose — the deferred Phase 2 consolidated-document publishing-tool decision (Livemark vs Quarto).
- **Phase 2 (the consolidated document) and its publishing-tool choice are out of scope**; this feature only sets up Phase 1 and must avoid foreclosing the Phase 2 decision.
- **The real corpus, the choice of pilot block, Future range prediction tool/the consumer's stack details, and any supplier-input Frictionless boundary are external unknowns** that remain open; the scaffold accommodates them rather than resolving them.
- **No accredited/production version-control platform integration is required from this scaffold** beyond standard Git/GitHub; the plan records that platform as already settled.
- **Example/placeholder data contains no real content**; only illustrative values are committed.

## Out of Scope

- Authoring the real Acoustic Dataset XSD or any real acoustic calculation logic.
- Phase 2 document production and the publishing-tool decision (Livemark vs Quarto, etc.).
- Java and JSON-Schema/TypeScript binding generation.
- Selecting or implementing the actual pilot block (gated on corpus knowledge and the conversation with the author).
- Any integration with Future range prediction tool or the consumer's stack.
