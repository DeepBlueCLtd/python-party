# Start here: zero to green

> **Tutorial** — follow these steps in order; by the end you'll have the environment running
> and you'll understand what you're looking at.

This tutorial gets you from *nothing* to a **green, runnable scaffold** and an **HTML docs
site you can browse** — all on the target's Python (3.9.4). It assumes no prior setup.

## What you're building toward

A schema-driven pipeline that turns acoustic calculation output into validated Sonar
Performance XML: generate typed models from the XSD, map calculation output onto them once,
serialise, then validate and round-trip.

## Step 1 — Open the environment

The fastest path is a **GitHub Codespace** (no local installs):

1. On the repository page: **Code → Codespaces → Create codespace**.
2. Wait for it to provision. It runs `make bootstrap` for you (installs the toolchain on
   Python 3.9.4) — see [Use the Codespace](../how-to/use-the-codespace.md) for detail.

Prefer local? You need Python 3.9.x and `make`, then run `make bootstrap` yourself. Either
way the commands below are identical ([ADR 0006](../decisions/0006-codespaces-with-local-fallback.md)).

## Step 2 — Verify it's green

```bash
make verify
```

This runs the linter and the test suite. You should see the tests pass. One of them asserts
the interpreter meets the 3.9 floor — a tiny, honest check that there's something real to run
before any pipeline code exists.

??? question "Why is there so little code yet?"
    The scaffold deliberately starts minimal. The pipeline modules (mapping, serialise,
    validate, compare) are added by the implementation tasks listed in
    `specs/001-codespace-xml-scaffold/tasks.md`. What's green today is the *environment* and
    the *documentation system* — the runway, not the aircraft.

## Step 3 — Build and browse the docs

```bash
make docs-serve
```

Open <http://localhost:8000>. This is the very site you're reading, rendered by MkDocs
Material — including the **Mermaid diagrams** (try the
[pipeline ERD](../concepts/pipeline-data-flow.md)). The docs are generated from the same
Markdown that lives next to the code, so they travel with the project
([ADR 0009](../decisions/0009-mkdocs-material-mermaid-html-docs.md)).

## Step 4 — Build the mental model

Read these short pages, in order:

1. [Schema as the contract](../concepts/schema-as-contract.md) — the one idea everything
   follows from.
2. [Typed data, end to end](../concepts/typed-vs-dicts.md) — how you write Python here: start
   from a structured set of parameters and keep the data in typed objects all the way to XML.
3. [The two verification gates](../concepts/two-verification-gates.md) — why schema-valid
   isn't the same as correct.

Then skim the [decisions overview](../decisions/index.md). Each ADR tells you *why* a choice
was made and *what was rejected* — that's the material you'll use to defend the design.

## Where to go next

- Want to do a specific task? → [How-to guides](../how-to/use-the-codespace.md)
- Need to change the schema? → [Change the schema](../how-to/change-the-schema.md)
- Want to record your own decision? → [Add a decision record](../how-to/add-a-decision-record.md)

!!! tip "This set grows with you"
    As you learn, add a concept page; as you find a recipe, add a how-to; as you decide
    something, add an ADR. The structure is designed to absorb that growth without reshaping.
