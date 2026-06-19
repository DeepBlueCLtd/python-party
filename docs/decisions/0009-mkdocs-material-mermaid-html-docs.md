# ADR 0009: MkDocs Material + Mermaid for HTML docs and ERDs generated from the XSD

- **Status**: Superseded (in part) by [ADR 0010](0010-xs3p-html-schema-reference.md)
- **Date**: 2026-06-13
- **Deciders**: Project team

> **Note (superseded in part):** the decision to *generate the schema reference + Mermaid ERD as
> Markdown by walking the XSD ourselves* is superseded by [ADR 0010](0010-xs3p-html-schema-reference.md),
> which generates the reference as HTML with the off-the-shelf xs3p stylesheet (no generated ERD).
> The choice of MkDocs Material + Mermaid for the rest of the site still stands.

## Context

Two documentation needs exist:

1. A **learning/decision** documentation set (this site) that must be *attractive*, navigable,
   and grow with understanding.
2. **Schema documentation for consumers** — derived from the *enriched* XSD
   (the `xs:documentation` annotations), ideally including **Mermaid ER diagrams** of the
   entities and relationships, so a consumer can understand the contract without reading raw XSD.

Both should honour **Data-as-the-contract**: the schema reference must be *generated* from the
XSD, never hand-maintained, so it can't drift ([ADR 0008](0008-generated-models-no-drift.md)).
The toolchain must run on Python 3.9.4 ([ADR 0007](0007-pin-python-3-9-4.md)).

## Decision

We will use **MkDocs Material** to render Markdown into the HTML site, with **Mermaid**
diagrams enabled natively (via `pymdownx.superfences`). The **schema reference pages and the
Mermaid ERD are generated artifacts**: a `make gen-schema-docs` step walks the enriched XSD /
generated dataclasses and emits Markdown (with an `erDiagram`) into `docs/reference/`, which
MkDocs then renders. `make docs` builds the site (`--strict`); CI builds it on every change.

## Consequences

### Positive

- One pipeline, two outputs: the same enriched XSD feeds both the dataclasses and the docs/ERD.
- Diagrams are plain-text Mermaid in version control — diffable, no binary image assets.
- Material gives search, navigation, light/dark, and code copy out of the box; content stays
  portable Markdown, so the renderer is swappable (the plan's portability principle).
- The generated schema reference can't drift from the contract (same discipline as bindings).

### Negative / trade-offs

- Adds `mkdocs-material` as a docs dependency and a build step.
- Mermaid renders client-side (JS in the browser); very large ERDs can get visually dense —
  we'll partition big schemas into per-area diagrams.
- The XSD→Markdown/ERD generator is bespoke (a small amount of "create"), justified because no
  off-the-shelf tool produces Mermaid ERDs from an annotated XSD the way we want.

## Alternatives considered

- **Sphinx** — powerful but heavier; reST-centric and less attractive by default for this use.
- **`xs3p` / `xsddoc` (XSLT/Java XSD→HTML)** — produce reference HTML but no Mermaid ERD and
  don't integrate with our Markdown learning docs; rejected.
- **Quarto** — durable and capable (and the plan's Phase 2 fallback for the *document*), but
  heavier to adopt now and not needed for developer/consumer schema docs. Not foreclosed for
  Phase 2.
- **Hand-drawn diagrams (images)** — rejected: drift from the schema, not diffable.

## Notes / revisit triggers

- This concerns *developer/consumer schema docs*, not the Phase 2 consolidated document. The
  Phase 2 publishing-tool decision (Livemark vs Quarto) remains deliberately open.
- If the bespoke XSD→ERD generator grows costly, reassess against any tool that has since
  gained annotated-XSD→Mermaid support.
