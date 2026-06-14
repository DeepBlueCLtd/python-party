"""The single mapping: ``CalculationResult`` -> populated generated models.

This is the **one place schema-aware logic lives** (contracts/pipeline-contract.md). It is
the only place to touch when the schema changes; nothing else references schema element names.

Two rules it enforces:

1. The mapping happens **exactly once** — no reshape-twice, no intermediate CSV/pickle/string.
2. Any value that does not fit a declared schema band/type is raised as a
   :class:`MappingError` *here*, before serialisation — so the pipeline never emits
   schema-valid-but-wrong XML, and the failure points at the offending location.
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal

from xsdata.models.datatype import XmlDateTime

from acoustic_dataset.acoustics import (
    ActiveSonarResult,
    BandResult,
    CalculationResult,
    CharacteristicsResult,
    PassiveSonarResult,
    SectorResult,
)
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
# XSD facets so a violation is caught at mapping time with a clear, location-aware message.
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
        raise MappingError(
            f"{where}: {field}={value} is outside the schema band [{low}, {high}]"
        )
    return value


def _require_below(
    value: Decimal, low: Decimal, high: Decimal, *, where: str, field: str
) -> Decimal:
    """Half-open band ``[low, high)`` — used for ``Bearing`` (0 <= x < 360)."""
    if value < low or value >= high:
        raise MappingError(
            f"{where}: {field}={value} is outside the schema band [{low}, {high})"
        )
    return value


def _require_min(value: Decimal, low: Decimal, *, where: str, field: str) -> Decimal:
    if value < low:
        raise MappingError(f"{where}: {field}={value} is below the schema minimum {low}")
    return value


def _require_int_in_range(value: int, low: int, high: int, *, where: str, field: str) -> int:
    if value < low or value > high:
        raise MappingError(
            f"{where}: {field}={value} is outside the schema band [{low}, {high}]"
        )
    return value


def _map_characteristics(result: CharacteristicsResult) -> PlatformCharacteristics:
    where = "characteristics"
    return PlatformCharacteristics(
        draft=_require_min(_dec(result.draft_m), _NON_NEGATIVE, where=where, field="Draft"),
        length=_require_min(_dec(result.length_m), _NON_NEGATIVE, where=where, field="Length"),
        weight=_require_min(_dec(result.weight_t), _NON_NEGATIVE, where=where, field="Weight"),
        year_introduced=_require_int_in_range(
            result.year_introduced, *_YEAR_RANGE, where=where, field="YearIntroduced"
        ),
    )


def _map_sector(band_index: int, sector: SectorResult) -> Sector:
    where = f"band {band_index} bearing {sector.bearing_deg:g}"
    return Sector(
        bearing=_require_below(
            _dec(sector.bearing_deg), *_BEARING_RANGE, where=where, field="Bearing"
        ),
        level=_require_in_range(
            _dec(sector.level_db), *_DECIBELS_RANGE, where=where, field="Level"
        ),
    )


def _map_band(band: BandResult) -> RadiatedBand:
    centre = _require_min(
        _dec(band.centre_frequency_hz), _NON_NEGATIVE,
        where=f"band {band.index}", field="CentreFrequency",
    )
    return RadiatedBand(
        centre_frequency=centre,
        directional=Directional(sector=[_map_sector(band.index, s) for s in band.sectors]),
        index=band.index,
    )


def _map_active(result: ActiveSonarResult) -> ActiveSonar:
    where = "active sonar"
    return ActiveSonar(
        name=result.name,
        manufacturer=result.manufacturer,
        operating_frequency=_require_min(
            _dec(result.operating_frequency_hz), _NON_NEGATIVE,
            where=where, field="OperatingFrequency",
        ),
        source_level=_require_in_range(
            _dec(result.source_level_db), *_DECIBELS_RANGE, where=where, field="SourceLevel"
        ),
        beamwidth=_require_in_range(
            _dec(result.beamwidth_deg), *_DEGREES_RANGE, where=where, field="Beamwidth"
        ),
        pulse_length=_require_min(
            _dec(result.pulse_length_s), _NON_NEGATIVE, where=where, field="PulseLength"
        ),
        max_range=_require_min(
            _dec(result.max_range_m), _NON_NEGATIVE, where=where, field="MaxRange"
        ),
    )


def _map_passive(ordinal: int, result: PassiveSonarResult) -> PassiveSonar:
    where = f"passive sonar {ordinal}"
    return PassiveSonar(
        name=result.name,
        manufacturer=result.manufacturer,
        operating_frequency=_require_min(
            _dec(result.operating_frequency_hz), _NON_NEGATIVE,
            where=where, field="OperatingFrequency",
        ),
        array_gain=_require_in_range(
            _dec(result.array_gain_db), *_DECIBELS_RANGE, where=where, field="ArrayGain"
        ),
        detection_threshold=_require_in_range(
            _dec(result.detection_threshold_db), *_DECIBELS_RANGE,
            where=where, field="DetectionThreshold",
        ),
        bearing_accuracy=_require_in_range(
            _dec(result.bearing_accuracy_deg), *_DEGREES_RANGE,
            where=where, field="BearingAccuracy",
        ),
    )


def to_model(result: CalculationResult) -> Platform:
    """Map a ``CalculationResult`` onto a populated ``Platform`` (raises on bad values)."""
    if not result.bands:
        raise MappingError("calculation produced no bands; nothing to map")
    return Platform(
        schema_version=result.schema_version,
        name=result.name,
        generated_utc=XmlDateTime.from_string(result.generated_utc),
        characteristics=_map_characteristics(result.characteristics),
        radiated_noise=RadiatedNoise(band=[_map_band(b) for b in result.bands]),
        sensors=SensorSuite(
            active=_map_active(result.active_sonar),
            passive=[
                _map_passive(i, p) for i, p in enumerate(result.passive_sonars, start=1)
            ],
        ),
    )
