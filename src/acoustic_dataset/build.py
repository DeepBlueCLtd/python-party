"""Build the schema's data object directly from calculation input (ADR 0010).

This is the **one builder** that produces schema-typed objects. It computes the dataset's
values with the pure seam functions in :mod:`acoustic_dataset.acoustics` and populates the
generated ``Platform`` / ``RadiatedBand`` / ``Sector`` / ... classes directly — there is no
intermediate domain hierarchy that is built only to be converted.

It enforces, at the point of construction, that every value **meets the schema**:

1. Numbers are converted to the schema's ``Decimal`` type and quantised to a fixed scale, so
   the serialised XML is deterministic (stable golden file).
2. Any value that does not fit a declared schema band/type raises a :class:`MappingError`
   *here*, before serialisation — so the pipeline never emits schema-valid-but-wrong XML, and
   the failure points at the offending location. The XSD validation gate then re-proves
   conformance on the serialised document.
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

from xsdata.models.datatype import XmlDateTime

from acoustic_dataset import acoustics
from acoustic_dataset.models.acoustic_dataset import (
    ActiveSonar,
    Directional,
    PassiveSonar,
    Platform,
    PlatformCharacteristics,
    RadiatedBand,
    RadiatedNoise,
    Sector,
    SensorSuite,
)

# Declared schema bands (kept in step with schema/acoustic_dataset.xsd). These mirror the
# XSD facets so a violation is caught at build time with a clear, location-aware message.
_DECIBELS_RANGE: tuple[Decimal, Decimal] = (Decimal("-200"), Decimal("300"))
_DEGREES_RANGE: tuple[Decimal, Decimal] = (Decimal("0"), Decimal("360"))  # inclusive both ends
_BEARING_RANGE: tuple[Decimal, Decimal] = (Decimal("0"), Decimal("360"))  # high end EXCLUSIVE
_YEAR_RANGE: tuple[int, int] = (1900, 2100)
_NON_NEGATIVE = Decimal("0")

# Fixed quantisation keeps serialised output deterministic across platforms (stable golden).
_Q_GENERAL = Decimal("0.001")


class MappingError(ValueError):
    """Raised when a calculated value does not fit a declared schema band/type."""


def _dec(value: float) -> Decimal:
    return Decimal(str(value)).quantize(_Q_GENERAL, rounding=ROUND_HALF_EVEN)


def _require_in_range(
    value: Decimal, low: Decimal, high: Decimal, *, where: str, field: str
) -> Decimal:
    if value < low or value > high:
        raise MappingError(f"{where}: {field}={value} is outside the schema band [{low}, {high}]")
    return value


def _require_below(
    value: Decimal, low: Decimal, high: Decimal, *, where: str, field: str
) -> Decimal:
    """Half-open band ``[low, high)`` — used for ``Bearing`` (0 <= x < 360)."""
    if value < low or value >= high:
        raise MappingError(f"{where}: {field}={value} is outside the schema band [{low}, {high})")
    return value


def _require_min(value: Decimal, low: Decimal, *, where: str, field: str) -> Decimal:
    if value < low:
        raise MappingError(f"{where}: {field}={value} is below the schema minimum {low}")
    return value


def _require_int_in_range(value: int, low: int, high: int, *, where: str, field: str) -> int:
    if value < low or value > high:
        raise MappingError(f"{where}: {field}={value} is outside the schema band [{low}, {high}]")
    return value


def _build_characteristics(spec: dict) -> PlatformCharacteristics:
    where = "characteristics"
    return PlatformCharacteristics(
        draft=_require_min(
            _dec(float(spec["draftMetres"])), _NON_NEGATIVE, where=where, field="Draft"
        ),
        length=_require_min(
            _dec(float(spec["lengthMetres"])), _NON_NEGATIVE, where=where, field="Length"
        ),
        weight=_require_min(
            _dec(float(spec["weightTonnes"])), _NON_NEGATIVE, where=where, field="Weight"
        ),
        year_introduced=_require_int_in_range(
            int(spec["yearIntroduced"]), *_YEAR_RANGE, where=where, field="YearIntroduced"
        ),
    )


def _build_sector(band_index: int, bearing_deg: float, level_db: float) -> Sector:
    where = f"band {band_index} bearing {bearing_deg:g}"
    return Sector(
        bearing=_require_below(_dec(bearing_deg), *_BEARING_RANGE, where=where, field="Bearing"),
        level=_require_in_range(_dec(level_db), *_DECIBELS_RANGE, where=where, field="Level"),
    )


def _build_bands(spec: dict) -> list[RadiatedBand]:
    """Synthesise the directional radiated-noise bands and build them into schema objects."""
    base_hz = float(spec["baseFrequencyHz"])
    ratio = float(spec["bandRatio"])
    band_count = int(spec["bandCount"])
    base_level = float(spec["baseLevelDb"])
    rolloff = float(spec["rolloffDbPerOctave"])
    peak_bearing = float(spec["directivity"]["peakBearingDeg"])
    amplitude = float(spec["directivity"]["amplitudeDb"])
    sampled_bearings = acoustics.bearings(float(spec["bearingStepDeg"]))

    bands: list[RadiatedBand] = []
    for index in range(1, band_count + 1):
        centre = acoustics.band_centre_hz(base_hz, ratio, index)
        rolloff_db = acoustics.spectral_rolloff_db(centre, base_hz, rolloff)
        sectors = [
            _build_sector(
                index,
                bearing,
                acoustics.radiated_level_db(
                    base_level,
                    rolloff_db,
                    acoustics.directivity_db(bearing, peak_bearing, amplitude),
                ),
            )
            for bearing in sampled_bearings
        ]
        bands.append(
            RadiatedBand(
                centre_frequency=_require_min(
                    _dec(centre), _NON_NEGATIVE, where=f"band {index}", field="CentreFrequency"
                ),
                directional=Directional(sector=sectors),
                index=index,
            )
        )
    return bands


def _build_active(spec: dict) -> ActiveSonar:
    where = "active sonar"
    source_level = float(spec["sourceLevelDb"])
    max_range = acoustics.active_max_range_m(source_level, float(spec["detectionThresholdDb"]))
    return ActiveSonar(
        name=str(spec["name"]),
        manufacturer=str(spec["manufacturer"]),
        operating_frequency=_require_min(
            _dec(float(spec["operatingFrequencyHz"])),
            _NON_NEGATIVE,
            where=where,
            field="OperatingFrequency",
        ),
        source_level=_require_in_range(
            _dec(source_level), *_DECIBELS_RANGE, where=where, field="SourceLevel"
        ),
        beamwidth=_require_in_range(
            _dec(float(spec["beamwidthDeg"])), *_DEGREES_RANGE, where=where, field="Beamwidth"
        ),
        pulse_length=_require_min(
            _dec(float(spec["pulseLengthSeconds"])),
            _NON_NEGATIVE,
            where=where,
            field="PulseLength",
        ),
        max_range=_require_min(_dec(max_range), _NON_NEGATIVE, where=where, field="MaxRange"),
    )


def _build_passive(ordinal: int, spec: dict) -> PassiveSonar:
    where = f"passive sonar {ordinal}"
    return PassiveSonar(
        name=str(spec["name"]),
        manufacturer=str(spec["manufacturer"]),
        operating_frequency=_require_min(
            _dec(float(spec["operatingFrequencyHz"])),
            _NON_NEGATIVE,
            where=where,
            field="OperatingFrequency",
        ),
        array_gain=_require_in_range(
            _dec(float(spec["arrayGainDb"])), *_DECIBELS_RANGE, where=where, field="ArrayGain"
        ),
        detection_threshold=_require_in_range(
            _dec(float(spec["detectionThresholdDb"])),
            *_DECIBELS_RANGE,
            where=where,
            field="DetectionThreshold",
        ),
        bearing_accuracy=_require_in_range(
            _dec(float(spec["bearingAccuracyDeg"])),
            *_DEGREES_RANGE,
            where=where,
            field="BearingAccuracy",
        ),
    )


def build_platform(data: dict) -> Platform:
    """Build a populated, schema-conformant ``Platform`` from a parsed input document.

    Computes the dataset's values and constructs the generated model objects directly,
    converting to the schema's types, quantising, and range-checking on the way (raising
    :class:`MappingError` on any value that does not meet the schema).
    """
    bands = _build_bands(data["radiatedNoise"])
    if not bands:
        raise MappingError("calculation produced no bands; nothing to build")
    return Platform(
        schema_version=str(data.get("schemaVersion", "0.2.0")),
        name=str(data["name"]),
        generated_utc=XmlDateTime.from_string(str(data["generatedUtc"])),
        characteristics=_build_characteristics(data["characteristics"]),
        radiated_noise=RadiatedNoise(band=bands),
        sensors=SensorSuite(
            active=_build_active(data["sensors"]["active"]),
            passive=[
                _build_passive(i, p) for i, p in enumerate(data["sensors"]["passive"], start=1)
            ],
        ),
    )


def build_platform_from_file(path: Path) -> Platform:
    """Convenience: load an input file and build the schema's ``Platform`` from it."""
    return build_platform(acoustics.load_input(path))
