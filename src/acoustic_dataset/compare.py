"""Migration-safety comparison: catch *schema-valid-but-different* output (US3, FR-015).

Schema validity proves a document fits the contract; it does **not** prove the document says
the same thing as a trusted prior-process file (e.g. a consumer's trial output). This module
canonicalises both sides — sorting attributes, normalising namespace prefixes, and stripping
cosmetic whitespace — so that only *meaningful* differences survive, then reports a
human-readable unified diff.

Why two canonicalisations (contracts/cli-commands.md §compare):

* The **equality key** uses C14N with ``rewrite_prefixes=True`` so a file that uses a namespace
  prefix compares equal to one using the default namespace. lxml emits an invalid empty-prefix
  declaration for unprefixed attributes under that flag, so the key is only ever *string*
  compared — never re-parsed.
* The **diff rendering** uses plain C14N (valid, re-parseable XML with attributes already
  sorted and cosmetic whitespace removed), pretty-printed so the diff is line-oriented and
  readable rather than one long line.

Both are pure functions over XML text, so the CLI and tests share them.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

from lxml import etree


@dataclass
class CompareResult:
    """Outcome of a migration-safety comparison."""

    equal: bool
    diff: str = ""  # empty when equal; a unified diff (reference -> generated) otherwise

    @property
    def ok(self) -> bool:
        return self.equal


def _read(xml: str | Path) -> str:
    if isinstance(xml, Path):
        return xml.read_text(encoding="utf-8")
    return xml


def _canonical(xml_text: str) -> str:
    """Prefix-, attribute- and whitespace-independent canonical form (the equality key).

    Comments are dropped: they are documentation, not data, so a banner on a reference file
    must not register as a migration difference.
    """
    return etree.canonicalize(
        xml_text, strip_text=True, rewrite_prefixes=True, with_comments=False
    )


def _pretty_lines(xml_text: str) -> list[str]:
    """Attribute-sorted, whitespace-normalised, indented lines for a readable unified diff.

    Namespace prefixes are stripped for display so a prefix-only difference (e.g. a ``ds:``
    reference vs default-namespace output) does not swamp the diff — without it, every line
    would read as changed. The equality verdict is decided separately and stays fully
    namespace-aware (:func:`_canonical`); this rendering is only a human aid.
    """
    canon = etree.canonicalize(xml_text, strip_text=True, with_comments=False)
    tree = etree.fromstring(canon.encode("utf-8"))
    for el in tree.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    etree.cleanup_namespaces(tree)
    return etree.tostring(tree, pretty_print=True, encoding="unicode").splitlines()


def _label(xml: str | Path, fallback: str) -> str:
    return xml.name if isinstance(xml, Path) else fallback


def compare(generated: str | Path, reference: str | Path) -> CompareResult:
    """Compare two XML documents, ignoring cosmetic differences only.

    Returns ``equal=True`` when the documents are canonically identical (a clean match);
    otherwise ``equal=False`` with a unified diff of the normalised forms, oriented as
    reference -> generated so additions are what the new output introduced.
    """
    gen_text = _read(generated)
    ref_text = _read(reference)
    if _canonical(gen_text) == _canonical(ref_text):
        return CompareResult(equal=True)
    diff = "\n".join(
        difflib.unified_diff(
            _pretty_lines(ref_text),
            _pretty_lines(gen_text),
            fromfile=f"reference:{_label(reference, 'reference')}",
            tofile=f"generated:{_label(generated, 'generated')}",
            lineterm="",
        )
    )
    return CompareResult(equal=False, diff=diff)
