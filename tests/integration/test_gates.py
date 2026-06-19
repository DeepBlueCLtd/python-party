"""Structural-gate tests (T020): schema validity + round-trip, and the mapping guard.

These encode the contract that schema-validity alone is not sufficient, and that a value
outside a declared band is rejected at mapping time — never emitted as schema-valid-but-wrong.
"""

from __future__ import annotations

import dataclasses

import pytest

from acoustic_dataset import acoustics, serialize, validate
from acoustic_dataset.mapping import MappingError, to_model


def test_golden_passes_both_structural_gates(golden_path, schema_path):
    report = validate.validate(golden_path, schema_path)
    assert report.schema_valid
    assert report.round_trip_equal
    assert report.ok
    assert report.errors == []


def test_pipeline_output_passes_both_gates(input_path, schema_path):
    xml = serialize.to_xml(to_model(acoustics.calculate_from_file(input_path)))
    report = validate.validate(xml, schema_path)
    assert report.ok


def test_schema_invalid_document_is_caught(input_path, schema_path):
    # Push a bearing past the schema's [0, 360) band: must fail the structural gate.
    xml = serialize.to_xml(to_model(acoustics.calculate_from_file(input_path)))
    bad = xml.replace(
        "<SectorBearing>0.000</SectorBearing>", "<SectorBearing>400.000</SectorBearing>", 1
    )
    assert bad != xml, "expected to find a bearing to tamper with"
    report = validate.validate(bad, schema_path)
    assert not report.schema_valid
    assert not report.ok
    assert any("schema" in e for e in report.errors)


def test_mapping_rejects_out_of_band_value_before_serialisation(input_path):
    result = acoustics.calculate_from_file(input_path)
    # Force an impossible source level past the schema's decibel band: the guard must fire.
    tampered_active = dataclasses.replace(result.active_sonar, source_level_db=9999.0)
    tampered = dataclasses.replace(result, active_sonar=tampered_active)
    with pytest.raises(MappingError, match="SourceLevel"):
        to_model(tampered)
