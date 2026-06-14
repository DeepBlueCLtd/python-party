"""Back the 'Typed objects vs. dictionaries' concept page with executable proof.

Each test pins one claim the page makes, so the comparison can't quietly rot (FR-010, ADR 0002).
"""

from __future__ import annotations

import dataclasses
from decimal import Decimal

import pytest

from acoustic_dataset import acoustics
from acoustic_dataset.mapping import MappingError, to_model


def test_typed_value_is_a_precise_decimal(input_path):
    platform = to_model(acoustics.calculate_from_file(input_path))
    source_level = platform.sensors.active.source_level
    assert isinstance(source_level, Decimal)  # not a lossy float
    assert source_level == Decimal("215.000")  # the exact, schema-banded value


def test_dict_access_is_stringly_typed_and_unsafe(input_path):
    raw = acoustics.load_input(input_path)
    # A real value — but keyed by an ad-hoc string and typed only as float.
    assert raw["sensors"]["active"]["sourceLevelDb"] == 215.0
    # A typo in the path explodes only at runtime...
    with pytest.raises(KeyError):
        _ = raw["snesors"]
    # ...or, with .get, silently returns None — wrong, with no error at all.
    assert raw["sensors"]["active"].get("srcLevel") is None


def test_typed_attribute_typo_is_caught(input_path):
    platform = to_model(acoustics.calculate_from_file(input_path))
    with pytest.raises(AttributeError):
        _ = platform.sensors.active.sourceLevel  # not a field — mypy + runtime catch it


def test_out_of_band_value_is_rejected_at_the_typed_boundary(input_path):
    result = acoustics.calculate_from_file(input_path)
    # The schema bounds Decibels to [-200, 300]; a dict would carry 9999 straight through.
    bad = dataclasses.replace(
        result, active_sonar=dataclasses.replace(result.active_sonar, source_level_db=9999.0)
    )
    with pytest.raises(MappingError, match="SourceLevel"):
        to_model(bad)
