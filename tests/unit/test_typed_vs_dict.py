"""Back the 'Typed objects vs. dictionaries' concept page with executable proof.

Each test pins one behaviour the page describes about storing data, so the comparison stays
accurate (FR-010, ADR 0002).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from acoustic_dataset import acoustics, build
from acoustic_dataset.models.acoustic_dataset import Sector


def test_a_dict_stores_anything_silently():
    record: dict = {}
    record["sourceLevel"] = 215.0
    record["sorceLevel"] = 9999  # a misspelled key is just another entry
    record["sourceLevel"] = "loud"  # a wrong type replaces the value, no error
    assert record == {"sourceLevel": "loud", "sorceLevel": 9999}


def test_an_unknown_field_is_rejected_when_constructing():
    # The declared shape is accepted...
    Sector(bearing=Decimal("30.000"), level=Decimal("134.000"))
    # ...but a name that is not a field fails at construction (a dict would just store it).
    with pytest.raises(TypeError):
        Sector(bering=Decimal("30.000"), level=Decimal("134.000"))


def test_a_stored_field_has_the_schema_declared_type(input_path):
    platform = build.build_platform_from_file(input_path)
    level = platform.radiated_noise.band[0].directional.sector[0].level
    assert isinstance(level, Decimal)  # stored as the schema's Decimal, not a bare float


def test_out_of_range_value_is_rejected_as_it_is_stored(input_path):
    data = acoustics.load_input(input_path)
    # The schema bounds Decibels to [-200, 300]; a dict would carry 9999 straight through.
    data["sensors"]["active"]["sourceLevelDb"] = 9999.0
    with pytest.raises(build.MappingError, match="SourceLevel"):
        build.build_platform(data)
