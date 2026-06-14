"""Schema-docs generator tests (T027, US5 / FR-020/021/022, SC-008/SC-009).

The schema reference + ERD are generated from the enriched XSD so they cannot drift from the
contract. These tests assert the generator emits the entities, the ``xs:documentation`` prose,
and a Mermaid ``erDiagram`` — and that the committed page is byte-identical to a fresh
regeneration (the property the CI drift gate depends on).
"""

from __future__ import annotations

from acoustic_dataset import schema_docs


def _generate(base, schema_path) -> str:
    return schema_docs.generate(schema_path, base / "schema").read_text(encoding="utf-8")


def test_output_contains_a_mermaid_erdiagram(tmp_path, schema_path):
    md = _generate(tmp_path, schema_path)
    assert "```mermaid" in md
    assert "erDiagram" in md


def test_output_contains_every_complex_type_entity(tmp_path, schema_path):
    md = _generate(tmp_path, schema_path)
    model = schema_docs.parse_schema(schema_path)
    assert model.complex_types, "expected the schema to declare complex types"
    for ct in model.complex_types:
        assert f"### {ct.name}" in md, f"missing entity section for {ct.name}"


def test_output_carries_xs_documentation_prose(tmp_path, schema_path):
    # Prose that lives only in the XSD's xs:annotation/xs:documentation (FR-022).
    md = _generate(tmp_path, schema_path)
    assert "Centre bearing of the sector, in degrees [0, 360)." in md
    assert "Maximum echo detection range, in metres." in md


def test_output_lists_banded_types_with_ranges(tmp_path, schema_path):
    md = _generate(tmp_path, schema_path)
    assert "## Banded numeric types" in md
    assert "≥ -200" in md and "≤ 300" in md  # Decibels facet range
    assert "< 360" in md  # Bearing's maxExclusive


def test_erd_shows_relationships_and_cardinalities(tmp_path, schema_path):
    md = _generate(tmp_path, schema_path)
    assert "RADIATED_NOISE ||--|{ RADIATED_BAND" in md  # one-to-many (10 bands)
    assert "PLATFORM_TYPE ||--|| SENSOR_SUITE" in md  # one-to-one


def test_inheritance_is_flattened_in_derived_entities(tmp_path, schema_path):
    md = _generate(tmp_path, schema_path)
    assert "Extends [`Sonar`]" in md
    assert "*(from Sonar)*" in md  # inherited fields marked in ActiveSonar/PassiveSonar


def test_generation_is_idempotent(tmp_path, schema_path):
    assert _generate(tmp_path / "a", schema_path) == _generate(tmp_path / "b", schema_path)


def test_committed_page_matches_a_fresh_regeneration(repo_root, schema_path, tmp_path):
    # The property the CI drift gate relies on: regeneration is byte-identical to the commit.
    committed = (repo_root / "docs" / "reference" / "schema" / "index.md").read_text(
        encoding="utf-8"
    )
    assert _generate(tmp_path, schema_path) == committed, (
        "run `make gen-schema-docs` — the committed schema reference is stale"
    )
