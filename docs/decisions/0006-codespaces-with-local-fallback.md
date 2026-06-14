# ADR 0006: GitHub Codespaces as the primary environment, with a portable local fallback

- **Status**: Accepted
- **Date**: 2026-06-13
- **Deciders**: Project team

## Context

This repository is also a **teaching environment** — the lessons that follow are run inside
it. A contributor (or learner) should reach a green, runnable system with *no manual setup*,
regardless of their machine. At the same time, the plan's **robust-across-unknowns** principle
warns against locking ourselves to any single tool: portability must be preserved.

## Decision

We will make **GitHub Codespaces** the primary environment via a `.devcontainer/` that
provisions everything (Python, the toolchain) and runs `make bootstrap` automatically. We will
**also** document an identical local path using the same `make` targets, so nothing about being
green depends on Codespaces specifically.

## Consequences

### Positive

- Zero-to-green in minutes with no local installs — ideal for lessons and onboarding.
- The environment definition is declarative and version-controlled.
- The single `make` surface (`bootstrap`, `verify`, `docs`, …) is identical locally and in CI,
  so "works in the Codespace" implies "works in CI."

### Negative / trade-offs

- A devcontainer is another artefact to maintain.
- Codespaces cold-start/provisioning time and (for the exact-version pin,
  [ADR 0007](0007-pin-python-3-9-4.md)) a slightly heavier build.

## Alternatives considered

- **Local setup docs only** — rejected: fails the no-manual-setup goal and reproducibility.
- **A bare Dockerfile / docker-compose** — rejected: over-engineered for a single-service
  scaffold; the devcontainer gives the same isolation with editor integration for lessons.

## Notes / revisit triggers

- If the accredited/production platform mandates a specific environment, the devcontainer is a
  replaceable front-end; the portable `make` surface is what we protect.
