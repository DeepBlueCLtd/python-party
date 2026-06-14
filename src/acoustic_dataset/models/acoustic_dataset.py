# DO NOT EDIT BY HAND.
# Generated from schema/acoustic_dataset.xsd by `make generate` (xsdata).
# Regenerate after any schema change; CI fails on drift. See docs/decisions/0008.
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from xsdata.models.datatype import XmlDateTime

__NAMESPACE__ = "https://deepblue.example/acoustic-dataset/v0"


@dataclass
class PlatformCharacteristics:
    """
    The physical characteristics of the platform.

    :ivar draft: Draft (depth of the lowest point below the waterline),
        in metres.
    :ivar length: Overall length of the platform, in metres.
    :ivar weight: Displacement (weight) of the platform, in tonnes.
    :ivar year_introduced: Calendar year the platform class entered
        service.
    """

    draft: Decimal = field(
        metadata={
            "name": "Draft",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
        }
    )
    length: Decimal = field(
        metadata={
            "name": "Length",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
        }
    )
    weight: Decimal = field(
        metadata={
            "name": "Weight",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
        }
    )
    year_introduced: int = field(
        metadata={
            "name": "YearIntroduced",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": 1900,
            "max_inclusive": 2100,
        }
    )


@dataclass
class Sector:
    """
    The radiated noise level in one 30-degree bearing sector of a band.

    :ivar bearing: Centre bearing of the sector, in degrees [0, 360).
    :ivar level: Radiated noise level in this sector, in decibels.
    """

    bearing: Decimal = field(
        metadata={
            "name": "Bearing",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
            "max_exclusive": Decimal("360"),
        }
    )
    level: Decimal = field(
        metadata={
            "name": "Level",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        }
    )


@dataclass
class Sonar:
    """
    Fields common to every sonar: identity plus a nominal operating
    frequency.

    :ivar name: Model name of the sonar.
    :ivar manufacturer: Manufacturer of the sonar.
    :ivar operating_frequency: Nominal operating (centre) frequency of
        the sonar, in hertz.
    """

    name: str = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    manufacturer: str = field(
        metadata={
            "name": "Manufacturer",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    operating_frequency: Decimal = field(
        metadata={
            "name": "OperatingFrequency",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
        }
    )


@dataclass
class ActiveSonar(Sonar):
    """
    An active sonar: it transmits, so it carries a source level and
    beam/pulse figures, and a derived maximum (echo) detection range.

    :ivar source_level: Transmit source level, in decibels.
    :ivar beamwidth: Transmit/receive beamwidth, in degrees.
    :ivar pulse_length: Transmit pulse length, in seconds.
    :ivar max_range: Maximum echo detection range, in metres.
    """

    source_level: Decimal = field(
        metadata={
            "name": "SourceLevel",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        }
    )
    beamwidth: Decimal = field(
        metadata={
            "name": "Beamwidth",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("360"),
        }
    )
    pulse_length: Decimal = field(
        metadata={
            "name": "PulseLength",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
        }
    )
    max_range: Decimal = field(
        metadata={
            "name": "MaxRange",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
        }
    )


@dataclass
class Directional:
    """
    The all-round radiated noise for one band: exactly twelve sectors at
    30-degree intervals, in ascending bearing order (0, 30, ..., 330).

    :ivar sector: One 30-degree bearing sector.
    """

    sector: list[Sector] = field(
        default_factory=list,
        metadata={
            "name": "Sector",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_occurs": 12,
            "max_occurs": 12,
        },
    )


@dataclass
class PassiveSonar(Sonar):
    """
    A passive sonar: it only listens, so it carries array gain, a detection
    threshold and a bearing accuracy rather than a transmit source level.

    :ivar array_gain: Array gain of the receiving array, in decibels.
    :ivar detection_threshold: Signal-to-noise ratio required for
        detection, in decibels.
    :ivar bearing_accuracy: 1-sigma bearing accuracy of the sonar, in
        degrees.
    """

    array_gain: Decimal = field(
        metadata={
            "name": "ArrayGain",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        }
    )
    detection_threshold: Decimal = field(
        metadata={
            "name": "DetectionThreshold",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("-200"),
            "max_inclusive": Decimal("300"),
        }
    )
    bearing_accuracy: Decimal = field(
        metadata={
            "name": "BearingAccuracy",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("360"),
        }
    )


@dataclass
class RadiatedBand:
    """
    The directional radiated noise for one frequency band.

    :ivar centre_frequency: Centre frequency of the band, in hertz.
    :ivar directional: The twelve 30-degree directional noise sectors
        for this band.
    :ivar index: 1-based ordinal of the band within the signature.
    """

    centre_frequency: Decimal = field(
        metadata={
            "name": "CentreFrequency",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_inclusive": Decimal("0"),
        }
    )
    directional: Directional = field(
        metadata={
            "name": "Directional",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    index: int = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class SensorSuite:
    """
    The sonar fit carried by the platform: one active sonar and two passive
    sonars.

    :ivar active: The platform's single active sonar.
    :ivar passive: The platform's two passive sonars.
    """

    active: ActiveSonar = field(
        metadata={
            "name": "Active",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    passive: list[PassiveSonar] = field(
        default_factory=list,
        metadata={
            "name": "Passive",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_occurs": 2,
            "max_occurs": 2,
        },
    )


@dataclass
class RadiatedNoise:
    """
    The platform's radiated-noise signature: exactly ten frequency bands,
    in ascending index order.

    :ivar band: One frequency band of the radiated-noise signature.
    """

    band: list[RadiatedBand] = field(
        default_factory=list,
        metadata={
            "name": "Band",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
            "min_occurs": 10,
            "max_occurs": 10,
        },
    )


@dataclass
class PlatformType:
    """
    A single platform: titled, timestamped reference data in three parts —
    physical characteristics, directional radiated noise, and the sonar
    fit.

    :ivar schema_version: Version of the schema this document targets.
    :ivar name: Human-readable name of the platform.
    :ivar generated_utc: UTC timestamp identifying when the document was
        produced.
    :ivar characteristics: The platform's physical characteristics.
    :ivar radiated_noise: The platform's directional radiated-noise
        signature.
    :ivar sensors: The platform's sonar fit.
    """

    schema_version: str = field(
        metadata={
            "name": "SchemaVersion",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    generated_utc: XmlDateTime = field(
        metadata={
            "name": "GeneratedUtc",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    characteristics: PlatformCharacteristics = field(
        metadata={
            "name": "Characteristics",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    radiated_noise: RadiatedNoise = field(
        metadata={
            "name": "RadiatedNoise",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )
    sensors: SensorSuite = field(
        metadata={
            "name": "Sensors",
            "type": "Element",
            "namespace": "https://deepblue.example/acoustic-dataset/v0",
        }
    )


@dataclass
class Platform(PlatformType):
    """
    Root element: the reference data for one platform.
    """

    class Meta:
        namespace = "https://deepblue.example/acoustic-dataset/v0"
