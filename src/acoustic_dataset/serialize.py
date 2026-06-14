"""Serialise populated domain objects to XML text (xsdata ``XmlSerializer``).

Binding-driven: there is no hand-built XML string anywhere, so the emitted document can only
contain what the generated models (and therefore the schema) allow. The default namespace is
bound to the schema target namespace for clean, prefix-free output.
"""

from __future__ import annotations

from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from acoustic_dataset.models.acoustic_dataset import Platform

NAMESPACE = "https://deepblue.example/acoustic-dataset/v0"


def _serializer() -> XmlSerializer:
    # Pretty-print with a stable 2-space indent so the on-disk artifact and golden file are
    # human-reviewable and deterministic. SerializerConfig grew an ``indent`` field in newer
    # xsdata; fall back to the older ``pretty_print`` flag for resilience across versions.
    try:
        config = SerializerConfig(indent="  ")
    except TypeError:  # pragma: no cover - older xsdata
        config = SerializerConfig(pretty_print=True)
    return XmlSerializer(config=config)


def to_xml(model: Platform) -> str:
    """Serialise a ``Platform`` to an XML string (default-namespace bound)."""
    return _serializer().render(model, ns_map={None: NAMESPACE})
