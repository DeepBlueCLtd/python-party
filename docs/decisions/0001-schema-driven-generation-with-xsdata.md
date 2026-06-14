# ADR 0001: Generate typed data classes from the XSD with xsdata

- **Status**: Accepted (provisional — pending validation against the real XSD)
- **Date**: 2026-06-13
- **Deciders**: Project team (to confirm with the author/the consumer)

## Context

Phase 1 must emit XML Acoustic Dataset that conforms to a mature schema (XSD). The old
chain (`generate_params → CSV → pickle → write_xml → XML`) hand-assembled XML and required
editing code per element type — the *programmer-as-bottleneck* antipattern. The delivery
plan's governing principles are **Configure, don't create** and **Data as the contract**:
the schema is the inter-organisational contract, and artefacts should be *derived* from it,
not hand-built alongside it.

## Decision

We will generate **typed Python dataclasses from the XSD using `xsdata`**, and use its
`XmlSerializer`/`XmlParser` to bind objects ↔ XML. Calculation output is mapped **once**
onto these generated objects; that mapping is the single place real logic lives.

## Consequences

### Positive

- Conformant *by construction* — the object model is the schema's shape.
- `xs:documentation` in the schema rides through to model docstrings (see
  [ADR 0009](0009-mkdocs-material-mermaid-html-docs.md) — same source feeds the HTML docs).
- Removes the "reshape twice" duplication of the old pipeline (calc → dict → XML text).
- Working in typed domain entities (not dicts/primitives) makes review and testing easier.

### Negative / trade-offs

- Field-level type strength is only as rich as the XSD declares — entity-level modelling is
  solid, but semantic field-typing exists only where the schema defines it.
- Adds `xsdata` (and `lxml`) as dependencies, and a generation step to the build.
- Generated code must be treated as an artifact, never hand-edited (see
  [ADR 0008](0008-generated-models-no-drift.md)).

## Alternatives considered

- **Hand-written models / keep `write_xml.py`** — the exact bottleneck the plan retires.
- **`generateDS`** — older, weaker dataclass support, less active.
- **`PyXB`** — effectively unmaintained.

## Notes / revisit triggers

- The real XSD's structure may expose xsdata edge cases (e.g. substitution groups, mixed
  content). Revisit generation options if the real schema doesn't bind cleanly.
- `xsdata >= 24` supports Python 3.9, which is compatible with our pin
  ([ADR 0007](0007-pin-python-3-9-4.md)).
