# Phase 0 Research: Codespace-Ready Repo Scaffold (Phase 1 XML Pipeline)

The spec's Assumptions section resolved the major directional choices (Codespaces, Python, `xsdata`),
so there are no open `NEEDS CLARIFICATION` markers. This document records the supporting toolchain
decisions, each with rationale and rejected alternatives, so the plan is grounded rather than assumed.

## D1 — Schema-to-model binding: `xsdata`

- **Decision**: Use `xsdata[cli,lxml]` to generate typed Python dataclasses from the XSD, and to bind
  objects ↔ XML via `xsdata.formats.dataclass.serializers.XmlSerializer` and
  `xsdata.formats.dataclass.parsers.XmlParser`.
- **Rationale**: Named directly in the delivery plan. Generates simple dataclasses with type hints
  from XSD; carries `xs:annotation/xs:documentation` through to model docstrings (FR-013); CLI
  generation (`xsdata generate <xsd> --package ...`) is repeatable and CI-friendly (FR-007, FR-017).
  Single mapping object → XML removes the old "reshape twice" duplication (FR-008).
- **Alternatives rejected**: `generateDS` (less active, dataclass support weaker); hand-written models
  (the `write_xml.py` antitrust the plan explicitly retires); `PyXB` (unmaintained).

## D2 — XSD validation gate: `xmlschema`

- **Decision**: Use the `xmlschema` package as the structural validation gate (validate emitted XML
  against the XSD), keeping `lxml` available for fast parsing and diff support.
- **Rationale**: Pure-Python, no system libraries required → portable and reproducible across
  Codespaces and local machines, matching the plan's "robust across unknowns / portable artefacts"
  principle. Supports XSD 1.1. Produces detailed, line-aware error reports suitable for a clear gate.
- **Alternatives rejected**: `lxml.etree.XMLSchema` alone — fast and capable, but XSD 1.0 only and
  ties validation to a C-extension build; kept as a secondary/parsing dependency rather than the
  primary gate. Online validators — not reproducible, not offline-capable.

## D3 — Round-trip as a distinct structural gate

- **Decision**: After serialising populated objects to XML, parse the XML back with `XmlParser` and
  re-serialise; assert structural/semantic equivalence. This is a *separate* gate from XSD validation.
- **Rationale**: The plan calls out two mechanical checks — "XSD validation **and** round-trip".
  Round-trip catches binding/serialisation losses that a schema-valid document can still hide.
- **Alternatives rejected**: Treating schema-validity as sufficient — explicitly the failure mode the
  plan warns against ("schema-valid is not the same as correct").

## D4 — Migration-safety comparison (schema-valid-but-different)

- **Decision**: Provide a `compare` step that canonicalises both the freshly generated XML and a
  contributor-supplied known-good reference (sort attributes, normalise whitespace/namespaces) and
  reports a human-readable diff of meaningful differences.
- **Rationale**: FR-015 / US3 — catch *schema-valid-but-different* against trusted prior output (e.g. the
  consumer's trial files) before trusting the new generator. Canonicalisation avoids false positives from
  cosmetic ordering while surfacing real differences.
- **Alternatives rejected**: Raw text diff (noisy — flags attribute order/whitespace); XSD validation
  of the reference only (cannot detect *difference*, only *invalidity*).

## D5 — Codespaces environment: devcontainer

- **Decision**: A `.devcontainer/devcontainer.json` on the Python 3.11 image with a `postCreateCommand`
  that runs `make bootstrap` (install deps, generate models). Document an identical local path.
- **Rationale**: FR-001/FR-002 one-click provisioning with no manual steps; FR-004 portability via the
  same Make targets locally. Keeps the environment definition declarative and version-controlled.
- **Alternatives rejected**: Manual setup docs only (fails FR-001); Docker Compose (over-engineered for
  a single-service scaffold); Nix (higher barrier, not in the plan's stack).

## D6 — Single-command entrypoints: `Makefile`

- **Decision**: Expose `make bootstrap`, `make verify`, `make generate`, `make pipeline`,
  `make compare`, `make bundle` as the documented commands; CLI subcommands live in `cli.py`.
- **Rationale**: FR-003 "single documented command" for verify; gives onboarding a stable, memorable
  surface independent of internal module layout (SC-007).
- **Alternatives rejected**: Bare `python -m` invocations in docs (brittle, leaks internals);
  `just`/`tox` (extra tool to learn; Make is ubiquitous on the base image).

## D7 — Placeholder schema shape

- **Decision**: Author a small but representative `acoustic_dataset.xsd` with a banded/typed numeric
  structure (e.g. a performance table with typed band elements and `xs:documentation` on terms), and a
  matching `examples/calculation_input.json`. Both clearly marked PLACEHOLDER in headers/comments.
- **Rationale**: FR-006/FR-018 + the spec assumption — the pipeline must be demonstrably runnable now,
  and the placeholder should exercise the *hard half* (a banded/typed numeric, not just flat strings)
  so the approach is genuinely validated before the real XSD lands.
- **Alternatives rejected**: Empty stub schema (pipeline not runnable, fails SC-002); copying a real
  schema (none available; would violate the no-real-data assumption).

## D8 — Generated-model drift discipline in CI

- **Decision**: CI regenerates models from the XSD and fails if the working tree differs from committed
  generated output (or, alternatively, treats `models/` as build-time-only). Generated files carry a
  "do not edit" header.
- **Rationale**: FR-017 — bindings stay version-locked to the schema; prevents the "N drifting de-facto
  schemas" trap. A `git diff --exit-code` after regeneration is a simple, robust drift check.
- **Alternatives rejected**: Trusting contributors not to hand-edit (the exact failure the plan names);
  not committing generated models at all (acceptable variant — documented as an option in the plan).

## D9 — Pin to exactly Python 3.9.4 (target-match)

- **Decision**: Pin the dev/CI interpreter to **exactly 3.9.4** (devcontainer Python feature +
  `actions/setup-python` `3.9.4`), and enforce the floor with `ruff target-version=py39` and
  `mypy python_version=3.9`. Package metadata keeps `requires-python=">=3.9"`.
- **Rationale**: The target system is constrained to 3.9.4; matching it exactly means "runs in dev/CI"
  implies "runs on target," and lint catches accidental 3.10+ syntax. `xsdata>=24`, `xmlschema`, and
  `mkdocs-material` all support 3.9. (See ADR 0007.)
- **Alternatives rejected**: latest 3.9.x (still risks post-3.9.4 stdlib behaviour); develop on 3.11/3.12
  with only a metadata floor (nothing stops 3.10+ feature use that fails on target).

## D10 — HTML docs via MkDocs Material + Mermaid; schema reference/ERD generated from the XSD

- **Decision**: Render docs with **MkDocs Material**, Mermaid enabled via
  `pymdownx.superfences`; build with `mkdocs build --strict` (in `make docs` and CI). The schema
  reference pages and the Mermaid **ERD** are produced by `make gen-schema-docs` **from the enriched
  XSD**, as generated artifacts (same no-drift discipline as bindings, D8).
- **Rationale**: FR-020/021/022 — one enriched-XSD source feeds dataclasses *and* docs/ERD; content
  stays portable Markdown so the renderer is swappable; Material gives search/nav/light-dark out of the
  box; diagrams are diffable plain-text. (See ADR 0009.)
- **Alternatives rejected**: Sphinx (heavier, reST-centric, less attractive by default); `xs3p`/`xsddoc`
  (XSD→HTML but no Mermaid ERD, no Markdown integration); Quarto (heavier now, and reserved as the
  *Phase 2* document fallback — not foreclosed); hand-drawn diagrams (drift, not diffable).
- **Note**: This is developer/consumer *schema* documentation, distinct from the deferred Phase 2
  consolidated-document publishing-tool decision.
