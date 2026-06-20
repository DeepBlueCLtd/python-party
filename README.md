# python-playground

Playground for developing / demonstrating python dev techniques.

This repository hosts **Acoustic Reference Book — Phase 1**: a schema-driven pipeline that turns acoustic
calculation output into validated **XML Acoustic Dataset**, built as a *learning* project
where every decision is documented and defensible.

## Quick start

Open in a **GitHub Codespace** (Code → Codespaces → Create codespace). It provisions
**Python 3.9.4** (matching the target system) and runs `make bootstrap` automatically. Then:

```bash
make verify        # lint + tests — confirm the environment is green
make docs-serve    # browse the docs at http://localhost:8000
```

Working locally instead? You need Python 3.9.x and `make`, then `make bootstrap`. Run `make`
to see all targets.

## Self-guided adventures

New here? Work through these in order. Each is a short, hands-on loop — run a command,
look at what it produced, then peek at the code that did it. Everything below has been
run end-to-end, so the output you see should match.

> All commands assume `make bootstrap` has finished (it runs automatically in a Codespace).
> If `acoustic` isn't found, the package is exposed as a module too: replace `acoustic`
> with `python -m acoustic_dataset.cli`.

### Adventure 1 — Run the whole pipeline and watch the gates

```bash
make verify                                  # lint + type-check + tests: is the env green?
acoustic pipeline                            # input XML -> typed objects -> XML -> validate
```

You should see something like:

```
pipeline ok: 10 band(s) -> build/acoustic_dataset.xml (schema-valid, round-trip-equal)
```

Open the file it wrote (`build/acoustic_dataset.xml`) and compare it to the input
(`examples/calculation_input.xml`). Then run the structural gate on its own and the
migration-safety diff against the known-good reference:

```bash
acoustic validate --xml build/acoustic_dataset.xml
acoustic compare build/acoustic_dataset.xml examples/reference/trial_known_good.xml
```

**Now read why:** [`docs/concepts/two-verification-gates.md`](docs/concepts/two-verification-gates.md)
explains why "schema-valid" and "correct" are two different checks. The code lives in
`src/acoustic_dataset/validate.py` and `compare.py`, dispatched from
[`cli.py`](src/acoustic_dataset/cli.py).

### Adventure 2 — Explore a typed Python data class

The pipeline never carries data in a loose `dict`; it builds **one typed object that
meets the schema**. Feel the difference yourself.

**First, experience editor autocomplete.** Open
[`examples/explore_platform.py`](examples/explore_platform.py) in VS Code (the Codespace
ships Pylance). Find the `# platform.` line, delete the `#`, put your cursor right after the
dot, and type: VS Code pops up the object's *declared* attributes (`radiated_noise`,
`sensors`, …) — statically, before the code has even run. Keep drilling
(`platform.radiated_noise.band[0].`) and it completes all the way down. That instant,
schema-shaped autocomplete is the real payoff of declared fields. Run the file any time with:

```bash
python examples/explore_platform.py
```

> If autocomplete doesn't appear, give Pylance a moment to index, and make sure VS Code's
> Python interpreter is set to the Codespace's 3.9 (bottom-right status bar / *Python: Select
> Interpreter*).

**Then poke at it in the REPL:**

```bash
python
```

```python
>>> from acoustic_dataset import build
>>> platform = build.build_platform_from_file("examples/calculation_input.xml")
>>> type(platform).__name__
'Platform'
>>> platform.radiated_noise.band[0].centre_frequency      # a Decimal, not a string
>>> from acoustic_dataset.models.acoustic_dataset import Sector
>>> Sector(bering=1, level=2)        # a typo is a TypeError, not a silent new key
```

The REPL can also complete attributes, but that's a separate `readline`/`rlcompleter`
feature that introspects the live object at runtime — not the static, declared-field
completion you saw in the editor. If `<TAB>` doesn't complete, enable it for the session
with `import readline, rlcompleter; readline.parse_and_bind("tab: complete")`.

Read [`docs/concepts/typed-vs-dicts.md`](docs/concepts/typed-vs-dicts.md) for what declared
fields buy you over a dictionary, then look at how the builder rejects out-of-range values in
`src/acoustic_dataset/build.py`.

### Adventure 3 — Reverse-engineer the data classes from the schema

Those data classes aren't hand-written — they're **generated from the XSD** by
[`xsdata`](https://xsdata.readthedocs.io/). The XSD is the single source of truth; the
Python is a build artifact (note the `# DO NOT EDIT BY HAND` header on every model file).

```bash
acoustic generate                            # regenerate models from every schema/*.xsd
```

Trace the chain for one element:

1. Open `schema/acoustic_dataset.xsd` and find an element, e.g. `Sector`.
2. Open the generated `src/acoustic_dataset/models/acoustic_dataset.py` and find the
   matching `@dataclass`. Notice how XSD types, ranges, and docs became Python `field`
   metadata.
3. Read `src/acoustic_dataset/generate.py` to see the exact `xsdata` invocation — and the
   two post-processing steps that keep the output deterministic and Python-3.9-compatible.

Want to *see* generation in action? Change a `<xs:documentation>` string in the XSD, run
`acoustic generate`, and `git diff` the models — the docstring tracks the schema. (Revert
the XSD edit afterward; CI fails if committed models drift from the schema — ADR 0008.)

### Adventure 4 — Generate and view the XSD documentation

Two complementary docs come out of this repo. First, a standalone **HTML schema reference**
rendered straight from the XSD (via the vendored `xs3p` stylesheet):

```bash
acoustic gen-schema-docs --out build/schema-preview.html
```

Open `build/schema-preview.html` (in a Codespace: right-click the file → *Download*, or use
the *Live Preview* extension) to browse every element, type, and constraint of the contract.
The pre-built version is committed at
[`docs/reference/schema/index.html`](docs/reference/schema/index.html). The generator lives
in `src/acoustic_dataset/schema_html.py`.

Second, the **full project site** — tutorials, concepts, ADRs, and a Mermaid ERD — served
by MkDocs Material:

```bash
make docs-serve                              # browse at http://localhost:8000
```

In a Codespace, when the port-forward notification appears, click **Open in Browser**.

### Where to go next

Follow the guided tutorial that ties all of this together:
[`docs/tutorials/01-start-here.md`](docs/tutorials/01-start-here.md), then skim the decision
records in [`docs/decisions/`](docs/decisions/index.md) — each says *why* a choice was made
and *what was rejected*.

## Documentation

The full, navigable documentation — tutorials, how-to guides, concepts, decision records
(ADRs), and a Mermaid schema ERD — lives in [`docs/`](docs/index.md) and renders as an
attractive HTML site via MkDocs Material (`make docs`).

**Start here:** [`docs/tutorials/01-start-here.md`](docs/tutorials/01-start-here.md).

## Spec-driven development

This project uses [GitHub Spec Kit](https://github.com/github/spec-kit). The active feature's
specification, plan, and design artifacts are under
[`specs/001-codespace-xml-scaffold/`](specs/001-codespace-xml-scaffold/). Use the
`/speckit-*` skills (`specify`, `plan`, `tasks`, `implement`) to drive development.

## Layout

| Path | What it is |
|---|---|
| `.devcontainer/` | Codespaces environment (Python 3.9.4) |
| `schema/` | The XSD contract |
| `src/acoustic_dataset/` | The pipeline package (`models/` is generated, never hand-edited) |
| `examples/` | Example calculation input + `reference/` known-good files |
| `tests/` | Unit, integration, and golden-file tests |
| `docs/` | The documentation site (MkDocs Material) |
| `specs/` | Spec Kit feature specs, plans, and contracts |
