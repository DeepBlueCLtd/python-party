# How to change the schema

> **How-to** — evolve the XSD and propagate the change through the schema-driven pipeline.

The schema is the single source of truth, so changing it is a *configuration change, not a
redesign*: models, validation, bindings and the schema docs all regenerate from it.

## Steps

1. **Edit the schema.**
   Change `schema/acoustic_dataset.xsd` (the contract). When you add or rename a type/element,
   put its definition prose in `xs:annotation/xs:documentation` so it rides through to the
   generated model docstrings and the schema reference.

2. **Regenerate the models.**
   ```bash
   make generate
   ```
   Runs `xsdata` over the schema and rewrites `src/acoustic_dataset/models/`. **Do not
   hand-edit** the result — it's a generated artifact
   (ADR 0008). Generation is pinned to the 3.9
   toolchain so the output is byte-reproducible for the drift gate.

3. **Regenerate the schema docs + ERD.**
   ```bash
   make gen-schema-docs
   ```
   Produces the reference pages and the Mermaid ERD from the schema
   (ADR 0009).

4. **Update the mapping.**
   `src/acoustic_dataset/mapping.py` is the **one place** that knows element names — update it
   for any added/renamed/retyped fields. Generation code does *not* change.

5. **Update the example and golden file.**
   Adjust `examples/calculation_input.json`, then refresh the golden file if the new output is
   intended:
   ```bash
   make pipeline                                                  # writes build/acoustic_dataset.xml
   cp build/acoustic_dataset.xml tests/golden/acoustic_dataset.xml
   ```
   Review the golden diff deliberately — it's the semantic gate.

6. **Re-run the gates.**
   ```bash
   make verify      # lint + type-check + tests + drift gate
   make pipeline    # end-to-end: map -> serialise -> validate -> round-trip
   ```

## Guard against schema-valid-but-different

If you have a **known-good** file from a prior process (e.g. one of the consumer's trial
files), drop it in `examples/reference/` and compare:

```bash
make pipeline
python -m acoustic_dataset.cli compare build/acoustic_dataset.xml examples/reference/<file>.xml
```

A clean match exits 0; a meaningful difference prints a diff and exits non-zero — catching
output that is schema-valid but differs from what a consumer depends on
(ADR 0004).

## What you should *not* touch

- Generated models (`src/acoustic_dataset/models/`) — regenerate instead.
- Generated schema reference/ERD under `reference/schema/` — regenerate instead.
- The generation code — it's schema-agnostic by design.
