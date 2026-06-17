"""Unit tests for the builder: calculation input -> a schema-conformant ``Platform`` (ADR 0010).

The acoustic seams (tested in ``test_acoustics.py``) are exercised here through the builder,
which constructs the generated model objects directly — there is no intermediate hierarchy.
"""

from __future__ import annotations

from decimal import Decimal

from acoustic_dataset import build


def test_build_produces_ten_bands_of_twelve_sectors(input_path):
    platform = build.build_platform_from_file(input_path)
    bands = platform.radiated_noise.band
    assert [b.index for b in bands] == list(range(1, 11))
    assert all(len(b.directional.sector) == 12 for b in bands)
    assert [s.bearing for s in bands[0].directional.sector][:3] == [
        Decimal("0.000"), Decimal("30.000"), Decimal("60.000")
    ]


def test_build_synthesises_characteristics_and_sensors(input_path):
    platform = build.build_platform_from_file(input_path)
    assert platform.schema_version == "0.2.0"
    assert platform.characteristics.year_introduced == 1998
    assert platform.sensors.active.name == "AS-900 Echo"
    # The derived max range falls straight out of the sonar equation, quantised to mm.
    assert platform.sensors.active.max_range == Decimal("118850.223")
    assert len(platform.sensors.passive) == 2
    assert platform.sensors.passive[1].manufacturer == "Marine Acoustics Ltd"
