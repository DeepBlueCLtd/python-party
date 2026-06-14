# How to run the migration-safety comparison

> **How-to** — check freshly generated XML against a trusted known-good file and catch the
> dangerous *schema-valid-but-different* case.

Schema validity proves the output fits the contract; it does **not** prove it says the same
thing as a file a consumer already depends on. The `compare` command closes that gap
([ADR 0004](../decisions/0004-two-gate-verification.md), FR-015).

## Steps

1. **Get a known-good reference.** Drop a trusted prior-process file (e.g. one of the
   consumer's trial outputs) into `examples/reference/`. A shipped sample,
   `examples/reference/trial_known_good.xml`, is there as a template.

2. **Produce fresh output.**
   ```bash
   make pipeline      # writes build/acoustic_dataset.xml
   ```

3. **Compare.**
   ```bash
   make compare       # build/acoustic_dataset.xml vs examples/reference/trial_known_good.xml
   ```
   Point it at other files by overriding the variables:
   ```bash
   make compare COMPARE_GENERATED=build/acoustic_dataset.xml \
                COMPARE_REFERENCE=examples/reference/your-trial-file.xml
   ```
   Or call the CLI directly:
   ```bash
   python -m acoustic_dataset.cli compare <generated.xml> <reference.xml>
   ```

## How to read the result

- **Clean match** → prints `match: …` and exits `0`. The documents are identical once
  cosmetic noise is removed.
- **Meaningful difference** → prints a unified diff (reference → generated) and exits non-zero,
  so it fails CI and scripts rather than passing silently.

## What counts as cosmetic (ignored) vs meaningful (caught)

The comparison canonicalises both sides first, so these **never** cause a failure:

| Ignored (cosmetic) | Example |
|---|---|
| Attribute order | `a="1" b="2"` vs `b="2" a="1"` |
| Whitespace / indentation | pretty-printed vs single-line |
| Namespace **prefix** | default `xmlns=…` vs `ds:` prefix (same URI) |
| Comments | a `<!-- trial file -->` banner |

Anything that changes the **data** — an element value, a missing or extra element, a different
structure — is reported as a difference. For instance, a radiated-noise `Level` of `134.000`
that becomes `144.000` is still inside the schema's decibel band (so it stays schema-valid) but
is surfaced as a one-line diff.

!!! note "Why prefixes and comments are ignored"
    A reference file from another tool may be serialised in a different style. The equality
    decision is fully namespace-aware; only the *prefix label* and documentation comments are
    treated as presentation, so style differences don't drown out the differences that matter.
