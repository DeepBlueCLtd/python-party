# ADR 0010: Generate the schema reference as HTML with xs3p

**Status:** Accepted (supersedes the schema-reference/ERD portion of
[ADR 0009](0009-mkdocs-material-mermaid-html-docs.md))

## Context

[ADR 0009](0009-mkdocs-material-mermaid-html-docs.md) chose to generate the schema reference as
Markdown — entity tables plus a hand-shaped Mermaid ERD — by walking the XSD in our own code
(`schema_docs.py`). When that code was first pointed at a **real** XSD (no-namespace, XSD 1.1,
"salami-slice": every element global, complex types built from `xs:all` and `xs:element ref="..."`,
documentation on the global elements / ref sites), it produced almost nothing: the hand-rolled
walker assumed `xs:sequence` + inline-named elements + `xs:extension` inheritance and silently
skipped everything else.

That is a direct violation of the project's **"configure, don't create"** principle: we were
hand-implementing XSD semantics (ref resolution, model groups, type resolution, XSD 1.1) — the
exact thing a real schema library or tool does correctly. Re-implementing it is both effort and a
standing source of bugs.

## Decision

Generate the schema reference as **HTML** using the off-the-shelf **xs3p** XSLT stylesheet,
driven through `lxml`'s XSLT engine (`make gen-schema-docs` → `schema_html.py`):

- xs3p (`tools/xs3p/xs3p.xsl`, vendored unmodified) renders any XSD — including the real idiom —
  into a single self-contained HTML reference. We own no XSD-parsing code.
- Output is **byte-deterministic** (no embedded timestamp/path), so the committed
  `docs/reference/schema/index.html` is **drift-checked** in CI exactly as the generated models are.
- The hand-rolled `schema_docs.py` and its Mermaid ERD are removed. The remaining Mermaid diagrams
  in the *concept* pages are hand-drawn illustrations and stay.

xs3p is licensed under the **DSTC Public License (DPL) 1.1** (an MPL-1.1-derived weak copyleft);
its `LICENSE.html` is vendored alongside the stylesheet and the file is kept unmodified
(`tools/xs3p/README.md`).

## Consequences

- The reference is robust to real-world XSD idioms by construction — no parser to maintain.
- We trade the MkDocs-integrated Markdown + Mermaid ERD for a standalone HTML page linked from the
  site. No entity-relationship *diagram* of the contract is generated anymore.
- A new, file-level-copyleft licence (DPL 1.1) enters the tree, scoped to `tools/xs3p/`.
- ADR 0009's choice of MkDocs Material + Mermaid for the rest of the site still stands; only its
  "schema reference + ERD generated as Markdown" portion is superseded here.
