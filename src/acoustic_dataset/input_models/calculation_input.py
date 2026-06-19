# DO NOT EDIT BY HAND.
# Generated from schema/calculation_input.xsd by `make generate` (xsdata).
# Regenerate after any schema change; CI fails on drift. See docs/decisions/0008.
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from xsdata.models.datatype import XmlDateTime


@dataclass
class ActiveBeamwidthDeg:
    """
    Transmit/receive beamwidth of the active sonar, in degrees.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("360"),
        },
    )


@dataclass
class ActiveDetectionThresholdDb:
    """Signal-to-noise ratio the active sonar needs to detect an echo, in decibels.

    Consumed to derive the maximum echo range; not emitted verbatim in
    the output.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        },
    )


@dataclass
class ActiveManufacturer:
    """
    Manufacturer of the active sonar.
    """

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class ActiveName:
    """
    Model name of the active sonar.
    """

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class ActiveOperatingFrequencyHz:
    """
    Nominal operating (centre) frequency of the active sonar, in hertz.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class ActivePulseLengthSeconds:
    """
    Transmit pulse length of the active sonar, in seconds.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class ActiveSourceLevelDb:
    """
    Transmit source level of the active sonar, in decibels.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        },
    )


@dataclass
class AmplitudeDb:
    """
    Peak-to-mean amplitude of the directivity lobe, in decibels.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        },
    )


@dataclass
class BandCount:
    """
    How many frequency bands to synthesise (1-based ladder length).
    """

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )


@dataclass
class BandRatio:
    """
    Geometric step between successive band centre frequencies (2 = octave spacing).
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_exclusive": Decimal("0"),
        },
    )


@dataclass
class BaseFrequencyHz:
    """
    Centre frequency of the first (lowest) radiated-noise band, in hertz.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class BaseLevelDb:
    """
    Radiated noise level at the base frequency, before roll-off and directivity, in
    decibels.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        },
    )


@dataclass
class BearingStepDeg:
    """
    Angular step at which each band is sampled all round the platform, in degrees
    (30 = twelve sectors).
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_exclusive": Decimal("0"),
            "max_inclusive": Decimal("360"),
        },
    )


@dataclass
class DraftMetres:
    """
    Draft (depth of the lowest point below the waterline), in metres.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class GeneratedUtc:
    """
    UTC timestamp identifying when these input parameters were produced.
    """

    value: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "required": True,
        },
    )


@dataclass
class LengthMetres:
    """
    Overall length of the platform, in metres.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class Name:
    """
    Human-readable name of the platform the parameters describe.
    """

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class PassiveArrayGainDb:
    """
    Array gain of the passive sonar's receiving array, in decibels.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        },
    )


@dataclass
class PassiveBearingAccuracyDeg:
    """
    1-sigma bearing accuracy of the passive sonar, in degrees.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("360"),
        },
    )


@dataclass
class PassiveDetectionThresholdDb:
    """
    Signal-to-noise ratio the passive sonar needs for detection, in decibels.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        },
    )


@dataclass
class PassiveManufacturer:
    """
    Manufacturer of the passive sonar.
    """

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class PassiveName:
    """
    Model name of the passive sonar.
    """

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class PassiveOperatingFrequencyHz:
    """
    Nominal operating (centre) frequency of the passive sonar, in hertz.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class PeakBearingDeg:
    """
    Bearing at which the directivity lobe peaks, in degrees [0, 360).
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
            "max_exclusive": Decimal("360"),
        },
    )


@dataclass
class RolloffDbPerOctave:
    """
    High-frequency spectral roll-off applied per octave above the base frequency,
    in decibels.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class SchemaVersion:
    """
    Version of the input schema this document targets.
    """

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class WeightTonnes:
    """
    Displacement (weight) of the platform, in tonnes.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class YearIntroduced:
    """
    Calendar year the platform class entered service.
    """

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": 1900,
            "max_inclusive": 2100,
        },
    )


@dataclass
class ActiveSonar:
    """Parameters of the platform's active sonar.

    The detection threshold is consumed to derive the output's maximum
    echo range.
    """

    active_name: Optional[ActiveName] = field(
        default=None,
        metadata={
            "name": "ActiveName",
            "type": "Element",
            "required": True,
        },
    )
    active_manufacturer: Optional[ActiveManufacturer] = field(
        default=None,
        metadata={
            "name": "ActiveManufacturer",
            "type": "Element",
            "required": True,
        },
    )
    active_operating_frequency_hz: Optional[ActiveOperatingFrequencyHz] = (
        field(
            default=None,
            metadata={
                "name": "ActiveOperatingFrequencyHz",
                "type": "Element",
                "required": True,
            },
        )
    )
    active_source_level_db: Optional[ActiveSourceLevelDb] = field(
        default=None,
        metadata={
            "name": "ActiveSourceLevelDb",
            "type": "Element",
            "required": True,
        },
    )
    active_beamwidth_deg: Optional[ActiveBeamwidthDeg] = field(
        default=None,
        metadata={
            "name": "ActiveBeamwidthDeg",
            "type": "Element",
            "required": True,
        },
    )
    active_pulse_length_seconds: Optional[ActivePulseLengthSeconds] = field(
        default=None,
        metadata={
            "name": "ActivePulseLengthSeconds",
            "type": "Element",
            "required": True,
        },
    )
    active_detection_threshold_db: Optional[ActiveDetectionThresholdDb] = (
        field(
            default=None,
            metadata={
                "name": "ActiveDetectionThresholdDb",
                "type": "Element",
                "required": True,
            },
        )
    )


@dataclass
class Characteristics:
    """
    The physical characteristics of the platform (passed through to the output
    unchanged).
    """

    draft_metres: Optional[DraftMetres] = field(
        default=None,
        metadata={
            "name": "DraftMetres",
            "type": "Element",
            "required": True,
        },
    )
    length_metres: Optional[LengthMetres] = field(
        default=None,
        metadata={
            "name": "LengthMetres",
            "type": "Element",
            "required": True,
        },
    )
    weight_tonnes: Optional[WeightTonnes] = field(
        default=None,
        metadata={
            "name": "WeightTonnes",
            "type": "Element",
            "required": True,
        },
    )
    year_introduced: Optional[YearIntroduced] = field(
        default=None,
        metadata={
            "name": "YearIntroduced",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Directivity:
    """The directional lobe applied to the radiated-noise field: a single peak bearing and its amplitude."""

    peak_bearing_deg: Optional[PeakBearingDeg] = field(
        default=None,
        metadata={
            "name": "PeakBearingDeg",
            "type": "Element",
            "required": True,
        },
    )
    amplitude_db: Optional[AmplitudeDb] = field(
        default=None,
        metadata={
            "name": "AmplitudeDb",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class PassiveSonar:
    """
    Parameters of one passive sonar carried by the platform.
    """

    passive_name: Optional[PassiveName] = field(
        default=None,
        metadata={
            "name": "PassiveName",
            "type": "Element",
            "required": True,
        },
    )
    passive_manufacturer: Optional[PassiveManufacturer] = field(
        default=None,
        metadata={
            "name": "PassiveManufacturer",
            "type": "Element",
            "required": True,
        },
    )
    passive_operating_frequency_hz: Optional[PassiveOperatingFrequencyHz] = (
        field(
            default=None,
            metadata={
                "name": "PassiveOperatingFrequencyHz",
                "type": "Element",
                "required": True,
            },
        )
    )
    passive_array_gain_db: Optional[PassiveArrayGainDb] = field(
        default=None,
        metadata={
            "name": "PassiveArrayGainDb",
            "type": "Element",
            "required": True,
        },
    )
    passive_detection_threshold_db: Optional[PassiveDetectionThresholdDb] = (
        field(
            default=None,
            metadata={
                "name": "PassiveDetectionThresholdDb",
                "type": "Element",
                "required": True,
            },
        )
    )
    passive_bearing_accuracy_deg: Optional[PassiveBearingAccuracyDeg] = field(
        default=None,
        metadata={
            "name": "PassiveBearingAccuracyDeg",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class RadiatedNoise:
    """
    Parameters of the directional radiated-noise model, expanded by the acoustics
    seams into the output's bands and sectors.

    :ivar base_frequency_hz:
    :ivar band_ratio:
    :ivar band_count:
    :ivar bearing_step_deg:
    :ivar base_level_db:
    :ivar rolloff_db_per_octave:
    :ivar directivity: The directivity lobe applied across all bearings.
    """

    base_frequency_hz: Optional[BaseFrequencyHz] = field(
        default=None,
        metadata={
            "name": "BaseFrequencyHz",
            "type": "Element",
            "required": True,
        },
    )
    band_ratio: Optional[BandRatio] = field(
        default=None,
        metadata={
            "name": "BandRatio",
            "type": "Element",
            "required": True,
        },
    )
    band_count: Optional[BandCount] = field(
        default=None,
        metadata={
            "name": "BandCount",
            "type": "Element",
            "required": True,
        },
    )
    bearing_step_deg: Optional[BearingStepDeg] = field(
        default=None,
        metadata={
            "name": "BearingStepDeg",
            "type": "Element",
            "required": True,
        },
    )
    base_level_db: Optional[BaseLevelDb] = field(
        default=None,
        metadata={
            "name": "BaseLevelDb",
            "type": "Element",
            "required": True,
        },
    )
    rolloff_db_per_octave: Optional[RolloffDbPerOctave] = field(
        default=None,
        metadata={
            "name": "RolloffDbPerOctave",
            "type": "Element",
            "required": True,
        },
    )
    directivity: Optional[Directivity] = field(
        default=None,
        metadata={
            "name": "Directivity",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Sensors:
    """The sonar fit to be described: one active sonar and one or more passive sonars.

    :ivar active_sonar: The platform's single active sonar.
    :ivar passive_sonar: The platform's passive sonars.
    """

    active_sonar: Optional[ActiveSonar] = field(
        default=None,
        metadata={
            "name": "ActiveSonar",
            "type": "Element",
            "required": True,
        },
    )
    passive_sonar: list[PassiveSonar] = field(
        default_factory=list,
        metadata={
            "name": "PassiveSonar",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class CalculationInput:
    """Root element: the calculation parameters for one platform — its physical characteristics, its radiated-noise model parameters, and its sonar fit. The pipeline expands these into a validated Platform dataset.

    :ivar schema_version:
    :ivar name:
    :ivar generated_utc:
    :ivar characteristics: The platform's physical characteristics.
    :ivar radiated_noise: The platform's radiated-noise model
        parameters.
    :ivar sensors: The platform's sonar fit.
    """

    schema_version: Optional[SchemaVersion] = field(
        default=None,
        metadata={
            "name": "SchemaVersion",
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[Name] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "required": True,
        },
    )
    generated_utc: Optional[GeneratedUtc] = field(
        default=None,
        metadata={
            "name": "GeneratedUtc",
            "type": "Element",
            "required": True,
        },
    )
    characteristics: Optional[Characteristics] = field(
        default=None,
        metadata={
            "name": "Characteristics",
            "type": "Element",
            "required": True,
        },
    )
    radiated_noise: Optional[RadiatedNoise] = field(
        default=None,
        metadata={
            "name": "RadiatedNoise",
            "type": "Element",
            "required": True,
        },
    )
    sensors: Optional[Sensors] = field(
        default=None,
        metadata={
            "name": "Sensors",
            "type": "Element",
            "required": True,
        },
    )
