"""Unit tests for the acoustic seam functions (T018).

Each seam is exercised directly so the engineering logic has fast, focused coverage,
independent of mapping/serialisation.
"""

from __future__ import annotations

import pytest

from acoustic_dataset import acoustics


def test_band_centres_climb_geometrically():
    # ratio=2 (octave spacing): f(index) = base * 2 ** (index - 1)
    assert acoustics.band_centre_hz(50.0, 2.0, 1) == pytest.approx(50.0)
    assert acoustics.band_centre_hz(50.0, 2.0, 2) == pytest.approx(100.0)
    assert acoustics.band_centre_hz(50.0, 2.0, 10) == pytest.approx(25600.0)


def test_spectral_rolloff_sheds_db_per_octave():
    # No roll-off at the base frequency; each octave up sheds exactly one step.
    assert acoustics.spectral_rolloff_db(50.0, 50.0, 5.0) == pytest.approx(0.0)
    assert acoustics.spectral_rolloff_db(100.0, 50.0, 5.0) == pytest.approx(5.0)
    assert acoustics.spectral_rolloff_db(200.0, 50.0, 5.0) == pytest.approx(10.0)


def test_directivity_peaks_at_peak_bearing_and_troughs_opposite():
    amp = 6.0
    assert acoustics.directivity_db(180.0, 180.0, amp) == pytest.approx(amp)             # peak
    assert acoustics.directivity_db(0.0, 180.0, amp) == pytest.approx(-amp)              # trough
    assert acoustics.directivity_db(90.0, 180.0, amp) == pytest.approx(0.0, abs=1e-9)    # beam


def test_radiated_level_combines_base_rolloff_and_directivity():
    # base - rolloff + directivity
    assert acoustics.radiated_level_db(140.0, 45.0, -6.0) == pytest.approx(89.0)


def test_active_max_range_inverts_two_way_spreading():
    # r = 10 ** ((SL - DT) / 40)
    assert acoustics.active_max_range_m(215.0, 12.0) == pytest.approx(10.0 ** (203.0 / 40.0))
    # An 80 dB two-way budget recovers a 100 m range.
    assert acoustics.active_max_range_m(80.0, 0.0) == pytest.approx(100.0)


def test_bearings_sample_all_round_in_30_degree_sectors():
    assert acoustics.bearings(30.0) == [
        0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0
    ]
    assert acoustics.bearings(90.0) == [0.0, 90.0, 180.0, 270.0]


def test_calculate_produces_ten_bands_of_twelve_sectors(input_path):
    result = acoustics.calculate_from_file(input_path)
    assert [b.index for b in result.bands] == list(range(1, 11))
    assert all(len(b.sectors) == 12 for b in result.bands)
    assert [s.bearing_deg for s in result.bands[0].sectors][:3] == [0.0, 30.0, 60.0]


def test_calculate_synthesises_characteristics_and_sensors(input_path):
    result = acoustics.calculate_from_file(input_path)
    assert result.schema_version == "0.2.0"
    assert result.characteristics.year_introduced == 1998
    assert result.active_sonar.name == "AS-900 Echo"
    assert result.active_sonar.max_range_m == pytest.approx(10.0 ** (203.0 / 40.0))
    assert len(result.passive_sonars) == 2
    assert result.passive_sonars[1].manufacturer == "Marine Acoustics Ltd"
