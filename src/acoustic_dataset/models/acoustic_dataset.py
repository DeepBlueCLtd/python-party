# DO NOT EDIT BY HAND.
# Generated from schema/acoustic_dataset.xsd by `make generate` (xsdata).
# Regenerate after any schema change; CI fails on drift. See docs/decisions/0008.
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional
from xsdata.models.datatype import XmlDateTime


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
class ActiveOperatingFrequency:
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
class ArrayGain:
    """
    Array gain of the receiving array, in decibels.
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
class BandIndex:
    """
    1-based ordinal of the band within the signature.
    """

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )


@dataclass
class Beamwidth:
    """
    Transmit/receive beamwidth, in degrees.
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
class BearingAccuracy:
    """
    1-sigma bearing accuracy of the sonar, in degrees.
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
class CentreFrequency:
    """
    Centre frequency of the band, in hertz.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )


@dataclass
class DetectionThreshold:
    """
    Signal-to-noise ratio required for detection, in decibels.
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
class Draft:
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
    UTC timestamp identifying when the document was produced.
    """

    value: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "required": True,
        },
    )


@dataclass
class Length:
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
class MaxRange:
    """
    Maximum echo detection range, in metres.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
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
class PassiveOperatingFrequency:
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
class PlatformName:
    """
    Human-readable name of the platform.
    """

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class PulseLength:
    """
    Transmit pulse length, in seconds.
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
    Version of the schema this document targets.
    """

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class SectorBearing:
    """
    Centre bearing of the sector, in degrees [0, 360).
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
class SectorLevel:
    """
    Radiated noise level in this sector, in decibels.
    """

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        },
    )


class SignatureQuality(Enum):
    """How a radiated-noise signature was obtained: measured at sea, modelled, or
    estimated."""

    MEASURED = "measured"
    MODELLED = "modelled"
    ESTIMATED = "estimated"


@dataclass
class SourceLevel:
    """
    Transmit source level, in decibels.
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
class Weight:
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
    """An active sonar: it transmits, so it carries a source level, beam/pulse figures, and a derived maximum (echo) detection range."""

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
    active_operating_frequency: Optional[ActiveOperatingFrequency] = field(
        default=None,
        metadata={
            "name": "ActiveOperatingFrequency",
            "type": "Element",
            "required": True,
        },
    )
    source_level: Optional[SourceLevel] = field(
        default=None,
        metadata={
            "name": "SourceLevel",
            "type": "Element",
            "required": True,
        },
    )
    beamwidth: Optional[Beamwidth] = field(
        default=None,
        metadata={
            "name": "Beamwidth",
            "type": "Element",
            "required": True,
        },
    )
    pulse_length: Optional[PulseLength] = field(
        default=None,
        metadata={
            "name": "PulseLength",
            "type": "Element",
            "required": True,
        },
    )
    max_range: Optional[MaxRange] = field(
        default=None,
        metadata={
            "name": "MaxRange",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Characteristics:
    """
    The physical characteristics of the platform.
    """

    draft: Optional[Draft] = field(
        default=None,
        metadata={
            "name": "Draft",
            "type": "Element",
            "required": True,
        },
    )
    length: Optional[Length] = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        },
    )
    weight: Optional[Weight] = field(
        default=None,
        metadata={
            "name": "Weight",
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
class PassiveSonar:
    """A passive sonar: it only listens, so it carries array gain, a detection threshold and a bearing accuracy rather than a transmit source level."""

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
    passive_operating_frequency: Optional[PassiveOperatingFrequency] = field(
        default=None,
        metadata={
            "name": "PassiveOperatingFrequency",
            "type": "Element",
            "required": True,
        },
    )
    array_gain: Optional[ArrayGain] = field(
        default=None,
        metadata={
            "name": "ArrayGain",
            "type": "Element",
            "required": True,
        },
    )
    detection_threshold: Optional[DetectionThreshold] = field(
        default=None,
        metadata={
            "name": "DetectionThreshold",
            "type": "Element",
            "required": True,
        },
    )
    bearing_accuracy: Optional[BearingAccuracy] = field(
        default=None,
        metadata={
            "name": "BearingAccuracy",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Quality:
    """
    How this signature was obtained.
    """

    value: Optional[SignatureQuality] = field(
        default=None,
        metadata={
            "required": True,
        },
    )


@dataclass
class SectorType:
    """
    The radiated noise level in one directional bearing sector of a band.
    """

    sector_bearing: Optional[SectorBearing] = field(
        default=None,
        metadata={
            "name": "SectorBearing",
            "type": "Element",
            "required": True,
        },
    )
    sector_level: Optional[SectorLevel] = field(
        default=None,
        metadata={
            "name": "SectorLevel",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Sector(SectorType):
    pass


@dataclass
class Sensors:
    """The sonar fit carried by the platform: one active sonar and one or more passive sonars.

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
class Directional:
    """The all-round radiated noise for one band: the directional sectors in ascending bearing order.

    :ivar sector: One directional bearing sector.
    """

    sector: list[Sector] = field(
        default_factory=list,
        metadata={
            "name": "Sector",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class Band:
    """
    The directional radiated noise for one frequency band.

    :ivar band_index:
    :ivar centre_frequency:
    :ivar directional: The directional noise sectors for this band.
    """

    band_index: Optional[BandIndex] = field(
        default=None,
        metadata={
            "name": "BandIndex",
            "type": "Element",
            "required": True,
        },
    )
    centre_frequency: Optional[CentreFrequency] = field(
        default=None,
        metadata={
            "name": "CentreFrequency",
            "type": "Element",
            "required": True,
        },
    )
    directional: Optional[Directional] = field(
        default=None,
        metadata={
            "name": "Directional",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class RadiatedNoise:
    """
    The platform's radiated-noise signature: one or more frequency bands in
    ascending index order.

    :ivar quality: Optional provenance of the signature.
    :ivar band: One frequency band of the radiated-noise signature.
    """

    quality: Optional[Quality] = field(
        default=None,
        metadata={
            "name": "Quality",
            "type": "Element",
        },
    )
    band: list[Band] = field(
        default_factory=list,
        metadata={
            "name": "Band",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class Platform:
    """Root element: titled, timestamped reference data for one platform in three parts — physical characteristics, directional radiated noise, and the sonar fit.

    :ivar schema_version:
    :ivar platform_name:
    :ivar generated_utc:
    :ivar characteristics: The platform's physical characteristics.
    :ivar radiated_noise: The platform's directional radiated-noise
        signature.
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
    platform_name: Optional[PlatformName] = field(
        default=None,
        metadata={
            "name": "PlatformName",
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
