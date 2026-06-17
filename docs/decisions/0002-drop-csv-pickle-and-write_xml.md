# ADR 0002: Drop the CSV, the pickle hand-off, and hand-rolled write_xml.py

- **Status**: Accepted
- **Date**: 2026-06-13
- **Deciders**: Project team

## Context

The current pipeline is `generate_params → CSV → pickle → write_xml → XML`. Each stage
carries a cost:

- The **CSV** is a high-volume, unscrutinised, transient placeholder. It never appears in
  the human-readable Acoustic Reference Book, and it is a poor medium for typed numerics — it stringifies
  everything and forces a re-parse downstream.
- The **pickle hand-off** is fragile and Python-version-bound; it only ever passed a baton
  between two scripts.
- **`write_xml.py`** is hand-assembled and edited per type — the programmer-as-bottleneck
  antipattern, and the seed of N drifting de-facto schemas.

## Decision

We will **remove all three** and replace the chain with a single mapping from calculation
output onto schema-generated objects (see [ADR 0001](0001-schema-driven-generation-with-xsdata.md)),
serialised once to XML.

## Consequences

### Positive

- Eliminates two lossy/fragile intermediates and one source of drift.
- Removes a whole class of "stringify then re-parse" type bugs.
- The typed, pre-serialise objects become the testable boundary — no separate intermediate
  is needed to get testability.

### Negative / trade-offs

- Any consumer or script that secretly depended on the intermediate CSV/pickle must be found
  and migrated. (We don't believe any *external* consumer does — the CSV never ships.)
- Loses the incidental "inspect the CSV by eye" debugging affordance; replaced by asserting
  on typed objects and golden-file XML diffs.

## Alternatives considered

- **Keep the CSV as a debugging convenience** — rejected: it re-introduces stringified
  numerics and a re-parse, for a benefit better served by typed-object assertions.
- **Replace pickle with JSON between scripts** — rejected: still an unnecessary inter-script
  baton; a single in-process mapping removes the hand-off entirely.

## Notes / revisit triggers

- **Refined by [ADR 0010](0010-build-schema-object-directly.md)**: the "single mapping from
  calculation output onto schema-generated objects" is replaced by building the schema object
  *directly* (no intermediate domain hierarchy). The removal of CSV/pickle/`write_xml` and the
  serialise-once decision here still stand.
- If profiling later shows the single in-process flow can't hold the full corpus in memory,
  revisit with a streaming approach — but not by resurrecting CSV/pickle.
