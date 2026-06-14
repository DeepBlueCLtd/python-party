# Onboarding

> **Start point for a new contributor.** This single page gets you to a green build and
> shows you where everything lives. For the guided, explained walkthrough, follow the
> [Start here tutorial](tutorials/01-start-here.md); for a command-by-command validation
> run, see the [quickstart](https://github.com/deepbluecltd/python-party/blob/main/specs/001-codespace-xml-scaffold/quickstart.md).

## Reach green

**GitHub Codespace (primary):** on the repository page, **Code → Codespaces → Create
codespace**. Provisioning runs `make bootstrap` for you (installs the toolchain on Python
3.9.4 and generates the models). When the terminal is ready:

```bash
make verify     # lint + tests — confirm the environment is green
make pipeline   # produce build/acoustic_dataset.xml (schema-valid, round-trip-equal)
```

**Local fallback:** you need Python 3.9.x and `make`, then run `make bootstrap` yourself
before the same `make verify` / `make pipeline`. Both paths reach the *same* green state
([ADR 0006](decisions/0006-codespaces-with-local-fallback.md)). Run `make help` to see every target.

## Where things live

| You're looking for… | It's here |
|---|---|
| The contract (the XSD) — **swap location** for the real schema | `schema/acoustic_dataset.xsd` ([how-to](how-to/swap-in-the-real-schema.md)) |
| The scientific seams (named, testable calc functions) | `src/acoustic_dataset/acoustics/` |
| The **one** place calc output becomes typed objects | `src/acoustic_dataset/mapping.py` |
| Generated models (never hand-edited — regenerate) | `src/acoustic_dataset/models/` |
| Example calculation input (placeholder) | `examples/calculation_input.json` |
| Tests (unit / integration / golden) | `tests/` |
| The plan & design artifacts | `specs/001-codespace-xml-scaffold/` (`spec.md`, `plan.md`, `tasks.md`) |
| Why each choice was made | [Decision records](decisions/index.md) |

## Build the mental model

Read these, in order — they're short:

1. [Schema as the contract](concepts/schema-as-contract.md) — the idea everything follows from.
2. [The two verification gates](concepts/two-verification-gates.md) — why schema-valid isn't the same as correct.
3. [Pipeline data flow](concepts/pipeline-data-flow.md) — how input becomes validated XML.

!!! tip "What's done, what's next"
    The environment and the end-to-end pipeline are in place. Remaining pipeline work
    (migration-safety `compare`, generated schema docs/ERD, the distribution bundle) is
    tracked in `specs/001-codespace-xml-scaffold/tasks.md`.
