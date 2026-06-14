# ADR 0007: Pin to exactly Python 3.9.4 to match the target system

- **Status**: Accepted
- **Date**: 2026-06-13
- **Deciders**: Project team (constraint supplied by the target-system owner)

## Context

The **target system is constrained to Python 3.9.4**. If we develop on a newer interpreter,
we risk shipping code that uses syntax or stdlib unavailable on the target (e.g. `X | Y`
union syntax in runtime positions from 3.10, `match` statements, newer stdlib APIs). The plan
favours moves that are robust and that don't create nasty surprises late.

## Decision

We will **pin the development and demo interpreter to exactly 3.9.4**, where matching the
target system actually matters, and run **CI on the latest 3.9.x patch**:

- The devcontainer installs `3.9.4` via the devcontainers Python feature — this is the
  environment a contributor develops and runs the demo in, so it matches the target exactly.
- CI runs `actions/setup-python` with `python-version: "3.9"` (latest 3.9.x) and also builds
  the docs. GitHub's hosted runners no longer ship a 3.9.4 binary (it exists only for retired
  Ubuntu images), and CI's job is to catch *version-line* incompatibilities, which the 3.9
  line and the tooling floor below already do.
- Tooling enforces the floor independently: `ruff target-version = "py39"` flags 3.10+ syntax,
  and `mypy python_version = "3.9"` type-checks against 3.9. The package metadata keeps a
  `requires-python = ">=3.9"` floor.

## Consequences

### Positive

- "Runs in dev/CI" genuinely implies "runs on the target" — the version gap can't bite late.
- `ruff`/`mypy` catch accidental 3.10+ usage at lint time, not in production.
- All chosen dependencies (`xsdata >= 24`, `xmlschema`, `mkdocs-material`) support 3.9.

### Negative / trade-offs

- We forgo newer-Python conveniences (structural pattern matching, built-in generic syntax
  at runtime, `tomllib`, etc.).
- Exact-patch provisioning depends on 3.9.4 being available to the devcontainer feature (it
  is). It is **not** available on current GitHub-hosted runners, which is why CI tracks the
  3.9 line rather than the exact patch — a small, accepted gap between CI and the target.
- 3.9.4 is an old patch (missing later 3.9.x security fixes). Accepted because **matching the
  target is the requirement**; if the target moves, this ADR is superseded.

## Alternatives considered

- **Develop on latest 3.9.x** — closer, but still risks depending on stdlib behaviour fixed
  after 3.9.4; rejected in favour of exact match.
- **Develop on 3.11/3.12 with `requires-python` floor only** — rejected: nothing stops a
  contributor using 3.10+ features that fail on the target.

## Notes / revisit triggers

- If the target system upgrades its Python, bump the pin here (devcontainer + tooling, and
  the CI 3.9 line) in one change and supersede this ADR.
