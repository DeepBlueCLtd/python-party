# Architecture Decision Records

An **ADR** captures a single significant decision: the **context** that forced it, the
**decision** taken, its **consequences**, and the **alternatives rejected** (and why).
They are the record you use to *defend* a choice later — or to revisit it when the context
changes.

We keep them numbered and append-only. A decision is never edited away; if it changes, a
new ADR supersedes it and the old one is marked `Superseded by NNNN`. That history is the
point — it shows how the thinking evolved.

To add one, follow [Add a decision record](../how-to/add-a-decision-record.md) using the
[template](0000-template.md).

## Status legend

- **Accepted** — in force.
- **Provisional** — adopted but explicitly pending validation (here: against the author, the consumer,
  and the corpus, per the delivery plan).
- **Superseded** — replaced by a later ADR.

## The record so far

| ADR | Decision | Status |
|----:|----------|--------|
| [0001](0001-schema-driven-generation-with-xsdata.md) | Generate typed data classes from the XSD with `xsdata` | Accepted |
| [0002](0002-drop-csv-pickle-and-write_xml.md) | Drop the CSV, the pickle hand-off, and hand-rolled `write_xml.py` | Accepted |
| [0003](0003-xmlschema-as-validation-gate.md) | Use `xmlschema` as the structural validation gate | Accepted |
| [0004](0004-two-gate-verification.md) | Verify with two gates: structural (mechanical) + semantic (human) | Accepted |
| [0005](0005-placeholder-schema-runnable-now.md) | Ship a labelled placeholder schema so the pipeline runs today | Accepted |
| [0006](0006-codespaces-with-local-fallback.md) | GitHub Codespaces as primary env, with a portable local fallback | Accepted |
| [0007](0007-pin-python-3-9-4.md) | Pin to exactly Python 3.9.4 to match the target system | Accepted |
| [0008](0008-generated-models-no-drift.md) | Treat bindings as generated artifacts; fail CI on drift | Accepted |
| [0009](0009-mkdocs-material-mermaid-html-docs.md) | MkDocs Material + Mermaid for HTML docs and ERDs from the XSD | Accepted |

!!! note
    Most decisions are **provisional in spirit** — the delivery plan records that the design
    still needs validating against the author and the corpus. "Accepted" here means "adopted for
    the scaffold," not "signed off by the customer."
