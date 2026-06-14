# How to add a decision record (ADR)

> **How-to** — capture a decision so it can be defended and revisited.

ADRs are how this project keeps its reasoning. Add one whenever you make a choice that a
future reader (or you, in three months) would otherwise have to reverse-engineer.

## When to write one

Write an ADR if the decision:

- constrains the architecture or the toolchain,
- has more than one reasonable answer, or
- you can imagine being asked "why did you do it *that* way?"

If it's a trivial, obvious choice with no alternatives, don't bother.

## Steps

1. **Pick the next number.** Look at [the overview](../decisions/index.md) and take the next
   `NNNN`.

2. **Copy the template.**
   ```bash
   cp docs/decisions/0000-template.md docs/decisions/NNNN-short-title.md
   ```

3. **Fill every section honestly** — especially **Alternatives considered**. An ADR with no
   rejected alternatives isn't defending anything. State the *trade-offs*, not just the wins.

4. **Add it to the nav** in `mkdocs.yml` under "Decisions (ADRs)" and to the table in
   `docs/decisions/index.md`.

5. **Build to check.**
   ```bash
   make docs
   ```

## Conventions

- **Append-only.** Never rewrite history. If a decision changes, write a *new* ADR and mark
  the old one `Superseded by ADR-NNNN`.
- **Status** is one of `Proposed`, `Accepted`, `Provisional` (adopted but pending validation —
  common here, pending the author/the consumer/the corpus), or `Superseded`.
- **Link** related ADRs and concept pages so the reasoning is navigable.
- Keep it short. An ADR is a decision record, not an essay.

## Why this format

The Context → Decision → Consequences → Alternatives shape forces you to write down the *why*
and the *cost*, which is exactly what you need to defend a choice or to know when changed
circumstances justify reopening it. See the [decisions overview](../decisions/index.md) for
the records so far.
