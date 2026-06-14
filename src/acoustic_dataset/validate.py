"""The structural verification gate: XSD validity AND round-trip equivalence.

Schema-validity alone is explicitly *not* sufficient (contracts/pipeline-contract.md): a
document must also survive parse -> re-serialise -> canonical compare with no binding loss.
Both checks are pure functions over XML text so tests and the CLI share them.

The semantic gate (golden-file diff + human sign-off) lives in the tests, not here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree
from xsdata.formats.dataclass.parsers import XmlParser

from acoustic_dataset.models.acoustic_dataset import Platform
from acoustic_dataset.serialize import to_xml


@dataclass
class ValidationReport:
    """Outcome of the structural gate: valid only if schema-valid AND round-trip-equal."""

    schema_valid: bool
    round_trip_equal: bool
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.schema_valid and self.round_trip_equal


def _read(xml: str | Path) -> str:
    if isinstance(xml, Path):
        return xml.read_text(encoding="utf-8")
    return xml


def _canonical(xml_text: str) -> str:
    """Canonicalise (C14N) so cosmetic differences don't mask real ones."""
    return etree.canonicalize(xml_text)


def schema_errors(xml: str | Path, schema: Path) -> list[str]:
    """Return XSD validation error messages (empty list == valid)."""
    # Imported lazily so a missing/old xmlschema only bites when the gate actually runs.
    import xmlschema

    xsd = xmlschema.XMLSchema11(str(schema))
    xml_text = _read(xml)
    return [f"schema: {e.reason or e.message}" for e in xsd.iter_errors(xml_text)]


def round_trip_equal(xml: str | Path) -> bool:
    """True if ``serialize(parse(xml))`` canonical-equals the input (no binding loss)."""
    xml_text = _read(xml)
    parsed = XmlParser().from_string(xml_text, Platform)
    reserialised = to_xml(parsed)
    return _canonical(xml_text) == _canonical(reserialised)


def validate(xml: str | Path, schema: Path) -> ValidationReport:
    """Run both structural gates over an XML document and report the combined result."""
    schema_problems = schema_errors(xml, schema)
    rt = round_trip_equal(xml)
    errors = list(schema_problems)
    if not rt:
        errors.append("round-trip: re-serialised XML is not canonical-equal to the input")
    return ValidationReport(
        schema_valid=not schema_problems,
        round_trip_equal=rt,
        errors=errors,
    )
