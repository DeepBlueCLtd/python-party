"""Generate the schema reference as HTML via the vendored xs3p XSLT stylesheet.

We do not parse the XSD ourselves — ``tools/xs3p/xs3p.xsl`` renders any XSD into a single
self-contained HTML reference, and we drive it through ``lxml``'s XSLT engine. This honours the
"configure, don't create" principle: an off-the-shelf tool owns the schema semantics (refs,
groups, ``xs:all``, XSD 1.1, types), we only wire it up. xs3p output is byte-deterministic, so the
committed page is drift-checked in CI. See ``tools/xs3p/README.md`` (provenance + DPL 1.1 licence).
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree

_PKG_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PKG_DIR.parent.parent

#: The vendored xs3p stylesheet — the single source of the reference's HTML rendering.
XS3P_XSL = _REPO_ROOT / "tools" / "xs3p" / "xs3p.xsl"


def render(schema_path: Path, stylesheet: Path | None = None) -> bytes:
    """Transform ``schema_path`` to HTML bytes with xs3p (no filesystem writes)."""
    transform = etree.XSLT(etree.parse(str(stylesheet or XS3P_XSL)))
    return bytes(transform(etree.parse(str(schema_path))))


def generate(schema_path: Path, out_file: Path, stylesheet: Path | None = None) -> Path:
    """Render ``schema_path`` to a single HTML file at ``out_file``; return ``out_file``."""
    html = render(schema_path, stylesheet)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(html)
    return out_file
