# Reference

> **Reference** — precise, look-it-up facts. Not a tutorial; no narrative.

| Page | What it gives you |
|---|---|
| [Commands](commands.md) | Every `make` target and CLI command, with exit-code meaning |
| [Schema ERD (example)](schema-erd.md) | The Mermaid ER diagram the docs generate from the enriched XSD |

## Authoritative specifications

The deeper, authoritative reference for this feature lives in the planning artifacts (outside
the docs site, under version control):

- `specs/001-codespace-xml-scaffold/spec.md` — the feature specification (WHAT/WHY).
- `specs/001-codespace-xml-scaffold/plan.md` — the implementation plan.
- `specs/001-codespace-xml-scaffold/data-model.md` — entities and field rules.
- `specs/001-codespace-xml-scaffold/contracts/` — the CLI and pipeline contracts.

## Generated reference (coming with the real schema)

When the enriched XSD lands, `make gen-schema-docs` adds **generated** pages here — one per
schema type, carrying the `xs:documentation` prose, plus the Mermaid ERD — produced *from the
schema* so they cannot drift ([ADR 0009](../decisions/0009-mkdocs-material-mermaid-html-docs.md)).
