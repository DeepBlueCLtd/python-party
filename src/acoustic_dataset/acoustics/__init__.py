"""Acoustic calculation seams: ``calculation_input.json`` -> ``CalculationResult``.

The recalculation/resampling-onto-bands work (FR-012): each physical step is a **discrete,
named, testable function** with the engineering "how it's computed" documented here in code
(FR-013) — definitions of *terms* live in the schema instead.

The maths is a deliberately compact analytic model. From a handful of high-level platform
parameters it synthesises:

* a geometric ladder of band centre frequencies,
* a directional radiated-noise field (a spectral roll-off with frequency plus a cardioid-ish
  directivity lobe around the platform), sampled every 30 degrees, and
* one derived sensor figure (an active sonar's maximum echo range from its source level).

It produces typed, banded numbers for the pipeline to carry. The dataclasses below are
deliberately named with a ``Result`` suffix so they never collide with the *generated* model
classes of the same domain.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SectorResult:
    """Radiated noise in one 30-degree bearing sector of a band (plain Python types)."""

    bearing_deg: float
    level_db: float


@dataclass(frozen=True)
class BandResult:
    """Directional radiated noise for one frequency band."""

    index: int
    centre_frequency_hz: float
    sectors: list[SectorResult]


@dataclass(frozen=True)
class CharacteristicsResult:
    """The platform's physical characteristics."""

    draft_m: float
    length_m: float
    weight_t: float
    year_introduced: int


@dataclass(frozen=True)
class ActiveSonarResult:
    """An active sonar: identity, transmit figures, and a derived maximum echo range."""

    name: str
    manufacturer: str
    operating_frequency_hz: float
    source_level_db: float
    beamwidth_deg: float
    pulse_length_s: float
    max_range_m: float


@dataclass(frozen=True)
class PassiveSonarResult:
    """A passive (listen-only) sonar: identity plus reception figures."""

    name: str
    manufacturer: str
    operating_frequency_hz: float
    array_gain_db: float
    detection_threshold_db: float
    bearing_accuracy_deg: float


@dataclass(frozen=True)
class CalculationResult:
    """The output of the acoustic seams: one platform's reference data."""

    schema_version: str
    name: str
    generated_utc: str
    characteristics: CharacteristicsResult
    bands: list[BandResult]
    active_sonar: ActiveSonarResult
    passive_sonars: list[PassiveSonarResult]


# ----- individual seam functions (each independently unit-tested) -----

def band_centre_hz(base_hz: float, ratio: float, index: int) -> float:
    """Centre frequency of the ``index``-th band (1-based) of a geometric ladder.

    Bands climb by a fixed ``ratio`` per step (e.g. ``ratio=2`` gives octave spacing), so
    ``f(index) = base_hz * ratio ** (index - 1)``.
    """
    return base_hz * math.pow(ratio, index - 1)


def spectral_rolloff_db(centre_hz: float, base_hz: float, rolloff_db_per_octave: float) -> float:
    """Reduction in radiated level at ``centre_hz`` relative to ``base_hz``, in dB.

    A simple high-frequency roll-off: ``rolloff_db_per_octave`` decibels are shed for every
    octave (doubling) above the base frequency, i.e. ``rolloff * log2(centre / base)``.
    """
    return rolloff_db_per_octave * math.log2(centre_hz / base_hz)


def directivity_db(bearing_deg: float, peak_bearing_deg: float, amplitude_db: float) -> float:
    """Directional modulation of the radiated level at ``bearing_deg``, in dB.

    A single cardioid-ish lobe: the level peaks at ``peak_bearing_deg`` (``+amplitude_db``) and
    troughs at the opposite bearing (``-amplitude_db``), varying as a cosine in between.
    """
    return amplitude_db * math.cos(math.radians(bearing_deg - peak_bearing_deg))


def radiated_level_db(base_level_db: float, rolloff_db: float, directivity_db: float) -> float:
    """Combine the base level, spectral roll-off and directivity into one radiated level (dB)."""
    return base_level_db - rolloff_db + directivity_db


def active_max_range_m(source_level_db: float, detection_threshold_db: float) -> float:
    """Maximum echo range of an active sonar, in metres.

    Inverts two-way spherical-spreading loss (``TL = 40 * log10(r)``): the source level above
    the detection threshold is the loss the echo can afford on its round trip, so
    ``r = 10 ** ((SL - DT) / 40)``.
    """
    return math.pow(10.0, (source_level_db - detection_threshold_db) / 40.0)


def bearings(step_deg: float) -> list[float]:
    """The bearings sampled all round the platform, from 0 up in ``step_deg`` increments.

    A 30-degree step yields the twelve sectors ``0, 30, ..., 330`` the schema expects.
    """
    count = int(round(360.0 / step_deg))
    return [round(step_deg * k, 6) for k in range(count)]


# ----- orchestration over the seams -----

def _calculate_bands(spec: dict) -> list[BandResult]:
    """Synthesise the directional radiated-noise bands from the high-level spec."""
    base_hz = float(spec["baseFrequencyHz"])
    ratio = float(spec["bandRatio"])
    band_count = int(spec["bandCount"])
    base_level = float(spec["baseLevelDb"])
    rolloff = float(spec["rolloffDbPerOctave"])
    peak_bearing = float(spec["directivity"]["peakBearingDeg"])
    amplitude = float(spec["directivity"]["amplitudeDb"])
    sampled_bearings = bearings(float(spec["bearingStepDeg"]))

    bands: list[BandResult] = []
    for index in range(1, band_count + 1):
        centre = band_centre_hz(base_hz, ratio, index)
        rolloff_db = spectral_rolloff_db(centre, base_hz, rolloff)
        sectors = [
            SectorResult(
                bearing_deg=bearing,
                level_db=radiated_level_db(
                    base_level, rolloff_db, directivity_db(bearing, peak_bearing, amplitude)
                ),
            )
            for bearing in sampled_bearings
        ]
        bands.append(BandResult(index=index, centre_frequency_hz=centre, sectors=sectors))
    return bands


def _active_sonar(spec: dict) -> ActiveSonarResult:
    return ActiveSonarResult(
        name=str(spec["name"]),
        manufacturer=str(spec["manufacturer"]),
        operating_frequency_hz=float(spec["operatingFrequencyHz"]),
        source_level_db=float(spec["sourceLevelDb"]),
        beamwidth_deg=float(spec["beamwidthDeg"]),
        pulse_length_s=float(spec["pulseLengthSeconds"]),
        max_range_m=active_max_range_m(
            float(spec["sourceLevelDb"]), float(spec["detectionThresholdDb"])
        ),
    )


def _passive_sonar(spec: dict) -> PassiveSonarResult:
    return PassiveSonarResult(
        name=str(spec["name"]),
        manufacturer=str(spec["manufacturer"]),
        operating_frequency_hz=float(spec["operatingFrequencyHz"]),
        array_gain_db=float(spec["arrayGainDb"]),
        detection_threshold_db=float(spec["detectionThresholdDb"]),
        bearing_accuracy_deg=float(spec["bearingAccuracyDeg"]),
    )


def calculate(data: dict) -> CalculationResult:
    """Run the seams over a parsed input document, producing a ``CalculationResult``."""
    characteristics = data["characteristics"]
    sensors = data["sensors"]
    return CalculationResult(
        schema_version=str(data.get("schemaVersion", "0.2.0")),
        name=str(data["name"]),
        generated_utc=str(data["generatedUtc"]),
        characteristics=CharacteristicsResult(
            draft_m=float(characteristics["draftMetres"]),
            length_m=float(characteristics["lengthMetres"]),
            weight_t=float(characteristics["weightTonnes"]),
            year_introduced=int(characteristics["yearIntroduced"]),
        ),
        bands=_calculate_bands(data["radiatedNoise"]),
        active_sonar=_active_sonar(sensors["active"]),
        passive_sonars=[_passive_sonar(p) for p in sensors["passive"]],
    )


def load_input(path: Path) -> dict:
    """Read and parse a calculation-input JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def calculate_from_file(path: Path) -> CalculationResult:
    """Convenience: load an input file and run the seams over it."""
    return calculate(load_input(path))
