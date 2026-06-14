# How to swap in the real schema

> **How-to** — replace the placeholder XSD with the real one when it arrives.

The placeholder schema lives at one documented location so this swap is a *configuration
change, not a redesign* ([ADR 0005](../decisions/0005-placeholder-schema-runnable-now.md)).

## Steps

1. **Replace the schema file.**
   Put the real enriched XSD at `schema/acoustic_dataset.xsd` (keep the path; if the filename
   must differ, update the single schema path in the `Makefile` / `pyproject.toml`).

2. **Regenerate the models.**
   ```bash
   make generate
   ```
   This runs `xsdata` over the new schema and rewrites `src/acoustic_dataset/models/`. **Do not
   hand-edit** the result — it's a generated artifact
   ([ADR 0008](../decisions/0008-generated-models-no-drift.md)).

3. **Regenerate the schema docs + ERD.**
   ```bash
   make gen-schema-docs
   ```
   Produces the HTML reference pages and the Mermaid ERD from the new enriched XSD
   ([ADR 0009](../decisions/0009-mkdocs-material-mermaid-html-docs.md)).

4. **Update the mapping.**
   `src/acoustic_dataset/mapping.py` is the **one place** that knows real element names — this is
   where the band/recalculation logic lives and where it's expected to change. Generation code
   does *not* change.

5. **Update the example and golden file.**
   Refresh `examples/calculation_input.json` and the golden file in `tests/golden/` to match
   the new contract.

6. **Re-run the gates.**
   ```bash
   make verify      # structural gate + tests
   make pipeline    # end-to-end: map -> serialise -> validate -> round-trip
   ```

## Guard against schema-valid-but-different

If you have a **known-good** file from the old process (e.g. one of the consumer's trial files), drop
it in `examples/reference/` and compare:

```bash
make pipeline
python -m acoustic_dataset.cli compare build/acoustic_dataset.xml examples/reference/<file>.xml
```

A clean match exits 0; a meaningful difference prints a diff and exits non-zero — catching
output that is schema-valid but differs from what a consumer depends on
([ADR 0004](../decisions/0004-two-gate-verification.md)).

## What you should *not* touch

- Generated models (`src/acoustic_dataset/models/`) — regenerate instead.
- Generated schema reference/ERD under `reference/` — regenerate instead.
- The generation code — it's schema-agnostic by design.

Once the real schema is in and green, mark
[ADR 0005](../decisions/0005-placeholder-schema-runnable-now.md) as **Superseded** and delete
the placeholder artefacts.
