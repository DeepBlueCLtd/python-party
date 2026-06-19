# How to change the schema

> **How-to** — evolve the XSD and propagate the change through the schema-driven pipeline.

The schema is the single source of truth, so changing it is a *configuration change, not a
redesign*: models, validation, bindings and the schema docs all regenerate from it.

There are **two** schemas, regenerated together by `make generate`: `schema/acoustic_dataset.xsd`
(the output dataset) and `schema/calculation_input.xsd` (the calculation parameters). They are
different shapes — the builder *expands* the input parameters into the output dataset — so an
output change usually means touching the output schema, the builder, and possibly the input
schema if a new parameter is needed.

## Steps

1. **Edit the schema(s).**
   Change `schema/acoustic_dataset.xsd` and/or `schema/calculation_input.xsd` (the contracts).
   When you add or rename a type/element, put its definition prose in
   `xs:annotation/xs:documentation` so it rides through to the generated model docstrings and the
   schema reference.

2. **Regenerate the models.**
   ```bash
   make generate
   ```
   Runs `xsdata` over both schemas and rewrites `src/acoustic_dataset/models/` (output) and
   `src/acoustic_dataset/input_models/` (input). **Do not hand-edit** the result — it's a
   generated artifact (ADR 0008). Generation is pinned to the 3.9 toolchain so the output is
   byte-reproducible for the drift gate.

3. **Regenerate the schema reference.**
   ```bash
   make gen-schema-docs
   ```
   Produces the HTML reference from the schema via xs3p
   (ADR 0011).

4. **Update the builder.**
   `src/acoustic_dataset/build.py` is the **one place** that knows element names — update it
   for any added/renamed/retyped fields. Generation code does *not* change.

5. **Update the example and golden file.**
   Adjust `examples/calculation_input.xml` (it must stay valid against
   `schema/calculation_input.xsd`), then refresh the golden file if the new output is intended:
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

- Generated models (`src/acoustic_dataset/models/`, `src/acoustic_dataset/input_models/`) —
  regenerate instead.
- Generated HTML schema reference under `reference/schema/` — regenerate instead.
- The generation code — it's schema-agnostic by design.
