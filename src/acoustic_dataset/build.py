"""Build the schema's data object directly from calculation input (ADR 0010).

This is the **one builder** that produces schema-typed objects. It computes the dataset's
values with the pure seam functions in :mod:`acoustic_dataset.acoustics` and populates the
generated ``Platform`` / ``Band`` / ``Sector`` / ... classes directly — there is no intermediate
domain hierarchy that is built only to be converted.

The schema is in the "salami-slice" idiom (every element global; complex types hold
``xs:element ref=...``), so xsdata emits a wrapper dataclass per element. Each scalar is therefore
constructed as ``ElementClass(value=...)`` rather than assigned bare.

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
from typing import Any

from xsdata.formats.dataclass.parsers import XmlParser

from acoustic_dataset import acoustics, validate
from acoustic_dataset.input_models import calculation_input as cin
from acoustic_dataset.models.acoustic_dataset import (
    ActiveManufacturer,
    ActiveName,
    ActiveOperatingFrequency,
    ActiveSonar,
    ArrayGain,
    Band,
    BandIndex,
    Beamwidth,
    BearingAccuracy,
    CentreFrequency,
    Characteristics,
    DetectionThreshold,
    Directional,
    Draft,
    GeneratedUtc,
    Length,
    MaxRange,
    PassiveManufacturer,
    PassiveName,
    PassiveOperatingFrequency,
    PassiveSonar,
    Platform,
    PlatformName,
    PulseLength,
    RadiatedNoise,
    SchemaVersion,
    Sector,
    SectorBearing,
    SectorLevel,
    Sensors,
    SourceLevel,
    Weight,
    YearIntroduced,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_SCHEMA = _REPO_ROOT / "schema" / "calculation_input.xsd"

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


# --- reading the typed input ---------------------------------------------------------------
# Each input element is a generated wrapper carrying its scalar on ``.value``. The fields are
# typed ``Optional`` (xsdata's default) but the input schema marks them required, and
# :func:`load_input` runs the XSD gate before parsing, so by here every value is present. The
# accessors take ``Any`` so we read across that generated-binding boundary without fighting the
# Optional types.


def _f(node: Any) -> float:
    """The wrapper's scalar value as a ``float`` (for the acoustic seams)."""
    return float(node.value)


def _s(node: Any) -> str:
    """The wrapper's scalar value as a ``str``."""
    return str(node.value)


def _i(node: Any) -> int:
    """The wrapper's scalar value as an ``int``."""
    return int(node.value)


def _build_characteristics(spec: Any) -> Characteristics:  # spec: cin.Characteristics
    where = "characteristics"
    return Characteristics(
        draft=Draft(
            _require_min(
                _dec(_f(spec.draft_metres)), _NON_NEGATIVE, where=where, field="Draft"
            )
        ),
        length=Length(
            _require_min(
                _dec(_f(spec.length_metres)), _NON_NEGATIVE, where=where, field="Length"
            )
        ),
        weight=Weight(
            _require_min(
                _dec(_f(spec.weight_tonnes)), _NON_NEGATIVE, where=where, field="Weight"
            )
        ),
        year_introduced=YearIntroduced(
            _require_int_in_range(
                _i(spec.year_introduced), *_YEAR_RANGE, where=where, field="YearIntroduced"
            )
        ),
    )


def _build_sector(band_index: int, bearing_deg: float, level_db: float) -> Sector:
    where = f"band {band_index} bearing {bearing_deg:g}"
    return Sector(
        sector_bearing=SectorBearing(
            _require_below(_dec(bearing_deg), *_BEARING_RANGE, where=where, field="Bearing")
        ),
        sector_level=SectorLevel(
            _require_in_range(_dec(level_db), *_DECIBELS_RANGE, where=where, field="Level")
        ),
    )


def _build_bands(spec: Any) -> list[Band]:  # spec: cin.RadiatedNoise
    """Synthesise the directional radiated-noise bands and build them into schema objects."""
    base_hz = _f(spec.base_frequency_hz)
    ratio = _f(spec.band_ratio)
    band_count = _i(spec.band_count)
    base_level = _f(spec.base_level_db)
    rolloff = _f(spec.rolloff_db_per_octave)
    peak_bearing = _f(spec.directivity.peak_bearing_deg)
    amplitude = _f(spec.directivity.amplitude_db)
    sampled_bearings = acoustics.bearings(_f(spec.bearing_step_deg))

    bands: list[Band] = []
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
            Band(
                band_index=BandIndex(index),
                centre_frequency=CentreFrequency(
                    _require_min(
                        _dec(centre), _NON_NEGATIVE, where=f"band {index}", field="CentreFrequency"
                    )
                ),
                directional=Directional(sector=sectors),
            )
        )
    return bands


def _build_active(spec: Any) -> ActiveSonar:  # spec: cin.ActiveSonar
    where = "active sonar"
    source_level = _f(spec.active_source_level_db)
    max_range = acoustics.active_max_range_m(source_level, _f(spec.active_detection_threshold_db))
    return ActiveSonar(
        active_name=ActiveName(_s(spec.active_name)),
        active_manufacturer=ActiveManufacturer(_s(spec.active_manufacturer)),
        active_operating_frequency=ActiveOperatingFrequency(
            _require_min(
                _dec(_f(spec.active_operating_frequency_hz)),
                _NON_NEGATIVE,
                where=where,
                field="OperatingFrequency",
            )
        ),
        source_level=SourceLevel(
            _require_in_range(
                _dec(source_level), *_DECIBELS_RANGE, where=where, field="SourceLevel"
            )
        ),
        beamwidth=Beamwidth(
            _require_in_range(
                _dec(_f(spec.active_beamwidth_deg)), *_DEGREES_RANGE, where=where, field="Beamwidth"
            )
        ),
        pulse_length=PulseLength(
            _require_min(
                _dec(_f(spec.active_pulse_length_seconds)),
                _NON_NEGATIVE,
                where=where,
                field="PulseLength",
            )
        ),
        max_range=MaxRange(
            _require_min(_dec(max_range), _NON_NEGATIVE, where=where, field="MaxRange")
        ),
    )


def _build_passive(ordinal: int, spec: Any) -> PassiveSonar:  # spec: cin.PassiveSonar
    where = f"passive sonar {ordinal}"
    return PassiveSonar(
        passive_name=PassiveName(_s(spec.passive_name)),
        passive_manufacturer=PassiveManufacturer(_s(spec.passive_manufacturer)),
        passive_operating_frequency=PassiveOperatingFrequency(
            _require_min(
                _dec(_f(spec.passive_operating_frequency_hz)),
                _NON_NEGATIVE,
                where=where,
                field="OperatingFrequency",
            )
        ),
        array_gain=ArrayGain(
            _require_in_range(
                _dec(_f(spec.passive_array_gain_db)), *_DECIBELS_RANGE, where=where,
                field="ArrayGain"
            )
        ),
        detection_threshold=DetectionThreshold(
            _require_in_range(
                _dec(_f(spec.passive_detection_threshold_db)),
                *_DECIBELS_RANGE,
                where=where,
                field="DetectionThreshold",
            )
        ),
        bearing_accuracy=BearingAccuracy(
            _require_in_range(
                _dec(_f(spec.passive_bearing_accuracy_deg)),
                *_DEGREES_RANGE,
                where=where,
                field="BearingAccuracy",
            )
        ),
    )


def load_input(path: Path, *, schema: Path = DEFAULT_INPUT_SCHEMA) -> cin.CalculationInput:
    """Read, validate and parse a calculation-input XML file into the typed input model.

    The input is held to its own contract (``schema/calculation_input.xsd``): the XSD gate runs
    *before* parsing, so a malformed or out-of-range parameter is rejected up front (mirroring the
    structural gate on the output). On success the document is parsed into a
    :class:`~acoustic_dataset.input_models.calculation_input.CalculationInput`.
    """
    path = Path(path)
    errors = validate.schema_errors(path, schema)
    if errors:
        raise MappingError(
            f"input {path} is not valid against {schema.name}: " + "; ".join(errors)
        )
    return XmlParser().parse(str(path), cin.CalculationInput)


def build_platform(data: cin.CalculationInput) -> Platform:
    """Build a populated, schema-conformant ``Platform`` from the typed calculation input.

    Computes the dataset's values and constructs the generated model objects directly,
    converting to the schema's types, quantising, and range-checking on the way (raising
    :class:`MappingError` on any value that does not meet the schema).
    """
    src: Any = data  # generated wrappers carry Optional fields; load_input's gate guarantees them.
    bands = _build_bands(src.radiated_noise)
    if not bands:
        raise MappingError("calculation produced no bands; nothing to build")
    return Platform(
        schema_version=SchemaVersion(_s(src.schema_version)),
        platform_name=PlatformName(_s(src.name)),
        generated_utc=GeneratedUtc(src.generated_utc.value),
        characteristics=_build_characteristics(src.characteristics),
        radiated_noise=RadiatedNoise(band=bands),
        sensors=Sensors(
            active_sonar=_build_active(src.sensors.active_sonar),
            passive_sonar=[
                _build_passive(i, p) for i, p in enumerate(src.sensors.passive_sonar, start=1)
            ],
        ),
    )


def build_platform_from_file(path: Path) -> Platform:
    """Convenience: load an input file and build the schema's ``Platform`` from it."""
    return build_platform(load_input(path))
