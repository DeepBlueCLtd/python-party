# Glossary

Domain (acoustics / sonar) and tooling terms used across this documentation.

## Domain

**Acoustic Reference Book** — the reference work this project supports.

**XML Acoustic Dataset** — the structured, machine-readable output that Phase 1 produces;
the canonical data contract that the Phase 2 document later consumes.

**Band / rebanding / resampling** — acoustic figures are reported against
discrete bands (e.g. frequency or range bands). The hard part of the calculation is
recalculating/resampling results onto the *schema's* bands. The pilot block should
include at least one real rebanding case so the pipeline exercises the hard half.

**Future range prediction tool** — a consuming system referenced in the delivery plan; which language bindings
ultimately matter depends partly on what it (and the consumer's stack) are built in. Open question.

## Pipeline & data

**XSD (XML Schema Definition)** — the schema; the authoritative, language-agnostic
**contract** that defines the structure and types of the XML Acoustic Dataset.

**Enriched XSD** — an XSD that carries human documentation inline via
`xs:annotation/xs:documentation`. That documentation rides through to generated model
docstrings *and* into the generated HTML reference — which is why definitions live in the
schema, not in XML comments (those are discarded at parse time).

**Data class / binding** — a typed object (here, a Python `dataclass`) generated from the
XSD that the pipeline populates. "Bindings" are the per-language conveniences derived from
the contract; they stay generated, never hand-edited.

**Round-trip** — parse an emitted XML document back into objects and re-serialise it; if
the result differs meaningfully, a binding/serialisation loss has occurred. A distinct
check from schema validation.

**Golden file** — a trusted expected-output XML, used by tests to catch unintended changes.

**Reference (known-good) file** — prior-process output (e.g. the consumer's trial files) used to
catch *schema-valid-but-different* output during migration.

**Schema-valid-but-different** — the dangerous failure mode: output that passes XSD
validation yet differs from what a consumer depended on. Caught by the migration-safety
comparison, not by validation alone.

**ERD (Entity-Relationship Diagram)** — a diagram of entities and how they relate. We draw
these by hand with **Mermaid** in the concept pages. The entity/type structure of the contract
itself is in the [generated schema reference](reference/schema/index.html) (HTML, from the XSD).

## Tooling

**xsdata** — generates typed Python dataclasses from an XSD and binds objects ↔ XML.
See [ADR 0001](decisions/0001-schema-driven-generation-with-xsdata.md).

**xmlschema** — pure-Python library used as the XSD validation gate.
See [ADR 0003](decisions/0003-xmlschema-as-validation-gate.md).

**MkDocs Material** — static-site generator that turns this Markdown into the attractive
HTML site, with native Mermaid support.
See [ADR 0009](decisions/0009-mkdocs-material-mermaid-html-docs.md).

**Mermaid** — text-based diagramming (flowcharts, ER diagrams) rendered in the browser;
keeps diagrams in version control as plain text.

**Devcontainer / GitHub Codespaces** — a declarative development environment so a
contributor gets a ready-to-run setup with no manual installation.
See [ADR 0006](decisions/0006-codespaces-with-local-fallback.md).

**Diátaxis** — the documentation framework (tutorials / how-to / reference / explanation)
this site is organised around.

**ADR (Architecture Decision Record)** — a short document capturing one decision: its
context, the choice, the consequences, and the alternatives rejected.
