"""Integration test for the pipeline (T019).

Asserts on BOTH boundaries the spec cares about (FR-010):
1. the schema data object the builder populates directly, and
2. the serialised XML, diffed against the trusted golden file (the semantic gate).
"""

from __future__ import annotations

from decimal import Decimal

from lxml import etree

from acoustic_dataset import build, serialize


def _build_xml(input_path):
    model = build.build_platform_from_file(input_path)
    return model, serialize.to_xml(model)


def test_populated_objects_carry_the_expected_typed_values(input_path):
    model = build.build_platform_from_file(input_path)

    assert model.schema_version == "0.2.0"

    # Platform characteristics: Decimals (the typed boundary the schema declares), not floats.
    assert model.characteristics.draft == Decimal("7.500")
    assert model.characteristics.weight == Decimal("2400.000")
    assert model.characteristics.year_introduced == 1998

    # Radiated noise: exactly ten bands, each with twelve directional sectors.
    assert [b.index for b in model.radiated_noise.band] == list(range(1, 11))
    band1 = model.radiated_noise.band[0]
    assert band1.centre_frequency == Decimal("50.000")
    assert len(band1.directional.sector) == 12
    # Directivity peaks astern (180 deg) and troughs ahead (0 deg).
    assert band1.directional.sector[0].bearing == Decimal("0.000")
    assert band1.directional.sector[0].level == Decimal("134.000")
    assert band1.directional.sector[6].bearing == Decimal("180.000")
    assert band1.directional.sector[6].level == Decimal("146.000")

    # Sensor fit: one active sonar (with a derived max range) and two passive sonars.
    assert model.sensors.active.name == "AS-900 Echo"
    assert model.sensors.active.max_range == Decimal("118850.223")
    assert [p.name for p in model.sensors.passive] == [
        "PA-110 Flank Array",
        "PA-220 Towed Array",
    ]


def test_serialised_xml_matches_the_golden_file(input_path, golden_path):
    _result, xml = _build_xml(input_path)
    produced = etree.canonicalize(xml)
    golden = etree.canonicalize(golden_path.read_text(encoding="utf-8"))
    assert produced == golden, "pipeline output drifted from tests/golden/acoustic_dataset.xml"
