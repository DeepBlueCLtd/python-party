# Pipeline data flow

> **Explanation** — the entities that move through Phase 1 and how they relate.

## The flow, end to end

```mermaid
flowchart TD
    Input["Calculation input<br/>(examples/calculation_input.json)"]
    Build["build.py<br/>(acoustic seams compute &<br/>populate the schema object)"]
    Objects["Schema data object<br/>(Platform, generated from XSD)"]
    XML["Emitted Platform XML"]
    Golden["Golden file"]
    Reference["Known-good reference"]

    Input --> Build --> Objects --> XML
    Objects -. "tests assert here" .-> Golden
    XML -. "structural gate" .-> XML
    XML -. "migration safety" .-> Reference
```

The acoustic seams compute the values and the builder populates **one schema data object**
directly — there is no intermediate domain hierarchy built only to be converted (ADR 0010).
That object, before serialisation, is the **typed testable boundary**: tests assert on it
directly, or diff the serialised XML against a golden file. No separate intermediate (no CSV,
no pickle) is needed to get testability; that whole chain was removed (ADR 0002).

## The entities as an ER diagram

This **Mermaid ERD** is drawn by hand for the data-flow story (it deliberately includes pipeline
entities like the golden and reference files). The
**[schema reference](../reference/schema/index.html)**, by contrast, is produced
**automatically from the schema** (as HTML) by `make gen-schema-docs`
(ADR 0011).

```mermaid
erDiagram
    CALCULATION_INPUT ||--|| PLATFORM : "built into (via acoustic seams)"
    PLATFORM ||--|| CHARACTERISTICS : describes
    PLATFORM ||--o{ RADIATED_BAND : "radiates across (10 bands)"
    RADIATED_BAND ||--o{ SECTOR : "all round (12 sectors)"
    PLATFORM ||--o{ SONAR : "carries (1 active, 2 passive)"
    PLATFORM ||--|| SCHEMA : "conforms to"
    PLATFORM ||--o| GOLDEN_FILE : "diffed against (semantic gate)"
    PLATFORM ||--o| REFERENCE_FILE : "compared with (migration safety)"

    PLATFORM {
        string name
        date generated_on
    }
    CHARACTERISTICS {
        decimal draft_m
        decimal length_m
        decimal weight_t
        int year_introduced
    }
    RADIATED_BAND {
        int index
        decimal centre_frequency_hz
    }
    SECTOR {
        decimal bearing_deg
        decimal level_db
    }
    SONAR {
        string name
        string manufacturer
    }
    SCHEMA {
        string xsd_path
        string version "0.2.0"
    }
```

## Reading the entities

| Entity | What it is | Key rule |
|---|---|---|
| **Acoustic seams** | The named, testable calculation functions (`band_centre_hz`, …) | Pure `float` arithmetic; feed the builder |
| **Schema data object** | The generated `Platform` the builder populates directly | The assertion boundary; built to meet the schema |
| **Platform XML** | The validated, round-tripped Phase 1 deliverable | Must pass both gates before it's trusted |
| **Golden file** | Trusted expected output | Drives the semantic gate; changed deliberately |
| **Reference file** | Prior-process output | Drives migration-safety comparison |
| **Schema** | The enriched XSD | The contract; everything derives from it |

For the authoritative entity definitions and field rules, see the planning artifact
`specs/001-codespace-xml-scaffold/data-model.md`.
