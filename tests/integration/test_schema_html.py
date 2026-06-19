"""Schema-reference (HTML) generator tests.

The reference is produced from the XSD by the vendored xs3p stylesheet (``schema_html``), not by
hand-rolled code. These tests assert it renders the schema's entities and ``xs:documentation``
prose, is deterministic, and that the committed page is byte-identical to a fresh regeneration —
the property the CI drift gate depends on.
"""

from __future__ import annotations

from acoustic_dataset import schema_html


def test_html_is_generated_and_nonempty(tmp_path, schema_path):
    out = schema_html.generate(schema_path, tmp_path / "index.html")
    html = out.read_text(encoding="utf-8")
    assert out.is_file()
    assert "<html" in html.lower()
    assert len(html) > 1000


def test_html_carries_entities_and_documentation(schema_path):
    html = schema_html.render(schema_path).decode("utf-8")
    # Entities/types declared in the schema appear in the reference...
    for name in ("Platform", "ActiveSonar", "RadiatedNoise", "SectorType"):
        assert name in html, f"missing schema component {name} in the reference"
    # ...and the xs:documentation prose is carried through.
    assert "Maximum echo detection range" in html


def test_generation_is_deterministic(schema_path):
    assert schema_html.render(schema_path) == schema_html.render(schema_path)


def test_committed_page_matches_a_fresh_regeneration(repo_root, schema_path):
    # The property the CI drift gate relies on: regeneration is byte-identical to the commit.
    committed = (repo_root / "docs" / "reference" / "schema" / "index.html").read_bytes()
    assert schema_html.render(schema_path) == committed, (
        "run `make gen-schema-docs` — the committed HTML schema reference is stale"
    )
