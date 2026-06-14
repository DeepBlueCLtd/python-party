# Schema ERD (example)

> **Reference** — an example of the **generated** Mermaid ER diagram.

!!! info "This is a hand-drawn stand-in"
    Once the real enriched XSD is in place, `make gen-schema-docs` produces this page
    **automatically from the schema** — entities, fields, relationships, and the
    `xs:documentation` prose all read from the XSD so the diagram can't drift from the contract
    ([ADR 0009](../decisions/0009-mkdocs-material-mermaid-html-docs.md)). The diagram below
    shows the intended shape for the *placeholder* schema.

## Entities and relationships

```mermaid
erDiagram
    PLATFORM ||--|| CHARACTERISTICS : describes
    PLATFORM ||--o{ RADIATED_BAND : "radiates across (10 bands)"
    RADIATED_BAND ||--o{ SECTOR : "all round (12 x 30 deg)"
    PLATFORM ||--|| SENSOR_SUITE : carries
    SENSOR_SUITE ||--|| ACTIVE_SONAR : "1 active"
    SENSOR_SUITE ||--o{ PASSIVE_SONAR : "2 passive"

    PLATFORM {
        string name "Human-readable name of the platform"
        date generated_on "When the document was produced"
        string schema_version "Version of the contract used"
    }
    CHARACTERISTICS {
        decimal draft "Draft below the waterline, in metres"
        decimal length "Overall length, in metres"
        decimal weight "Displacement, in tonnes"
        int year_introduced "Year the class entered service"
    }
    RADIATED_BAND {
        int index "1-based ordinal of the band"
        decimal centre_frequency "Centre frequency of the band, in hertz"
    }
    SECTOR {
        decimal bearing "Centre bearing of the sector, in degrees [0, 360)"
        decimal level "Radiated noise level in this sector, in decibels"
    }
    ACTIVE_SONAR {
        string name "Model name of the sonar"
        decimal source_level "Transmit source level, in decibels"
        decimal max_range "Maximum echo detection range, in metres"
    }
    PASSIVE_SONAR {
        string name "Model name of the sonar"
        decimal array_gain "Array gain, in decibels"
        decimal bearing_accuracy "1-sigma bearing accuracy, in degrees"
    }
```

## How to read it

- `||--o{` means "one to zero-or-many" — one `PLATFORM` radiates across many
  `RADIATED_BAND`s, each holding many `SECTOR`s.
- `||--||` means "one to one".
- The text after each field (e.g. *"Lower edge of the band"*) is exactly what the **enriched
  XSD** will carry in `xs:annotation/xs:documentation` — the same prose that becomes the
  generated data-class docstrings. One source, many outputs
  ([Schema as the contract](../concepts/schema-as-contract.md)).

## Why generate it (rather than draw it)

A hand-drawn diagram is a second source of truth that rots. Generating the ERD from the schema
means the picture and the contract are *the same artefact viewed two ways* — change the schema,
regenerate, and the diagram is correct by construction
([ADR 0008](../decisions/0008-generated-models-no-drift.md)).
