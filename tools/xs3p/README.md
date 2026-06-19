# xs3p — vendored XSD → HTML documentation stylesheet

`xs3p.xsl` renders an XML Schema (XSD) into a single self-contained HTML reference. We run it
through `lxml`'s XSLT engine (`make gen-schema-docs`) so the schema reference is produced by an
off-the-shelf tool rather than hand-rolled XSD-walking code ("configure, don't create").

## Provenance
- Source: <https://github.com/bitfehler/xs3p> (maintained fork of the original DSTC xs3p).
- Vendored file: `xs3p.xsl` (unmodified).

## License — note
`xs3p.xsl` is licensed under the **DSTC Public License (DPL) v1.1** (an MPL-1.1-derived,
file-level weak-copyleft license) — see `LICENSE.html`. This is a *different* license from this
repository's own. It permits use, modification and distribution provided the license travels with
the file; if `xs3p.xsl` is ever modified, the DPL requires those modifications be made available.
We keep the file unmodified to avoid that obligation.

## Determinism
xs3p output is byte-deterministic for a given input schema (no embedded timestamp), so the
generated HTML is committed and the CI drift gate can assert it matches a fresh regeneration.
