# Playground — having a play with the Python pipeline

A hands-on guide to experimenting with the code in a Codespace. The example input
(`examples/calculation_input.xml`) is your sandbox: edit it, re-run the pipeline, and
watch the validated output change.

> Everything below works through one CLI (`acoustic`, i.e. `python -m acoustic_dataset.cli`).
> The `make` targets are just documented shortcuts over it.

## Step 0 — Open the Codespace and let it bootstrap

When you create the Codespace, the devcontainer automatically runs `make bootstrap`
(installs deps + generates models). Wait for the terminal to show `Bootstrap complete.`,
then confirm everything's healthy:

```bash
make verify        # ruff + mypy + pytest — should be all green
```

> If you ever recreate the venv by hand, run `make bootstrap` first — the `acoustic`
> command and `make pipeline`/`make verify` only work once the package is installed
> into the environment. In a fresh Codespace this is automatic.

## Step 1 — Run the pipeline once to see the baseline

```bash
make pipeline
```

This maps `examples/calculation_input.xml` → typed objects → XML → validates → round-trips,
and writes `build/acoustic_dataset.xml`. You'll see something like
`pipeline ok: 10 band(s) -> build/acoustic_dataset.xml`. Open `build/acoustic_dataset.xml`
to see the expanded, validated dataset.

## Step 2 — Edit the input and re-run (the fun part)

Open `examples/calculation_input.xml` and change a value — e.g. bump `<BandCount>10` to
`20`, or change `<BaseLevelDb>140.0` to `155.0`. Then:

```bash
make pipeline
```

The band count in the output message and the generated XML change accordingly. This is the
tightest feedback loop: input XML in, validated dataset out.

**Try breaking it on purpose** to see the gates work. Set `<BandCount>` to a negative number,
or put text where a number goes, and re-run — the build/validation gate rejects it, prints the
error, exits non-zero, and does **not** write a stale artifact.

## Step 3 — Poke the CLI directly

The Makefile just wraps the `acoustic` command. Call it yourself for full control over
inputs/outputs:

```bash
acoustic --help                       # see all subcommands
acoustic pipeline --input examples/calculation_input.xml --out build/mine.xml
acoustic validate --xml build/mine.xml
acoustic compare build/mine.xml examples/reference/trial_known_good.xml
```

`compare` tells you whether your output is *canonically identical* to the known-good
reference, not just schema-valid.

## Step 4 — Explore in a Python REPL

To play with the actual objects rather than the CLI:

```bash
python
```

```python
from acoustic_dataset import build, serialize
model = build.build_platform_from_file("examples/calculation_input.xml")
model.radiated_noise.band[:3]          # inspect the expanded bands
print(serialize.to_xml(model)[:500])   # see the serialized XML
```

This drops you into the dataclasses generated from the schema, so you can introspect the
data model interactively.

## Step 5 — If you change the schema

If you edit anything in `schema/*.xsd`, regenerate the typed models (otherwise CI's drift
gate will fail):

```bash
make generate          # regenerate models from the XSD
make gen-schema-docs   # regenerate the HTML schema reference
```

## Quick reference for a play session

1. Edit `examples/calculation_input.xml`
2. `make pipeline`
3. Look at `build/acoustic_dataset.xml`
4. Repeat — or drop into `python` for the object model

---

## Switching to the real schema

Everything above runs against the **placeholder** schema committed in `schema/`. The real,
proprietary XSD and corpus live in `private/` — a folder that is **entirely gitignored** and
must never reach git, CI, or the internet. (See `private/README.md`.)

The key constraint: `src/acoustic_dataset/models/` is **committed** (the placeholder-generated
models that CI drift-checks). Generating from the real schema into that location would
overwrite it with real structure, and an accidental commit would leak it. So real-generated
models go into `private/models/` instead.

Once the real material is dropped into `private/` (real XSD in `private/schema/`, real inputs
in `private/examples/`, known-good XML in `private/reference/`), point the same CLI at those
paths:

```bash
# 1. Generate typed models from the real XSD into the gitignored output dir
acoustic generate --schema private/schema/<real>.xsd --out private/models

# 2. Validate a real XML file against the real schema (structural gate + round-trip)
acoustic validate --xml private/examples/<real>.xml --schema private/schema/<real>.xsd

# 3. Migration-safety compare: generated vs known-good reference
acoustic compare private/models/<generated>.xml private/reference/<known_good>.xml
```

### Caveat: the full `pipeline` command

`acoustic pipeline` imports `acoustic_dataset.models` — the **committed** package — so it always
uses the placeholder-derived bindings, even when you pass `--schema private/...`. To run the
*full* end-to-end pipeline on real-generated models, that import would need to point at
`private/models/`. **Ask before wiring that up**, since it touches committed code and risks
leaking real structure into the repo.

In short, with the real schema you can immediately use `generate`, `validate`, and `compare`
against `private/` paths; the end-to-end `pipeline` needs a deliberate (reviewed) change first.
