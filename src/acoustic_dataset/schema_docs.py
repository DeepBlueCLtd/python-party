"""Generate the schema reference + Mermaid ERD from the enriched XSD (US5, FR-020/021/022).

The enriched XSD is the single source of truth. This walks it and emits a Markdown reference —
a Mermaid ``erDiagram`` of the entities and their relationships, a per-complex-type field
reference carrying the ``xs:documentation`` prose, and a catalogue of the banded numeric types —
into ``docs/reference/schema/``. The page is a *generated artifact*, never hand-edited, so the
reference and the diagram cannot drift from the contract (ADR 0008/0009); the CI drift gate
regenerates it and fails on any diff.
"""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

_XS = "http://www.w3.org/2001/XMLSchema"
_NS = {"xs": _XS}

_FACET_ORDER = ("minInclusive", "minExclusive", "maxInclusive", "maxExclusive")
_FACET_OP = {
    "minInclusive": "≥",
    "minExclusive": ">",
    "maxInclusive": "≤",
    "maxExclusive": "<",
}


@dataclass
class SchemaField:
    """One element or attribute of a complex type."""

    name: str
    type_ref: str  # raw @type, e.g. "Metres" or "xs:string"
    is_attribute: bool
    min_occurs: int
    max_occurs: str  # an int as a string, or "unbounded"
    required: bool
    doc: str
    inherited_from: str = ""

    @property
    def type_local(self) -> str:
        return self.type_ref.split(":")[-1] if self.type_ref else ""


@dataclass
class ComplexType:
    name: str
    doc: str
    base: str  # base complex-type name, or ""
    fields: list[SchemaField]


@dataclass
class SimpleType:
    name: str
    base: str
    facets: dict[str, str]
    doc: str


@dataclass
class SchemaModel:
    version: str
    doc: str
    simple_types: list[SimpleType]
    complex_types: list[ComplexType]
    root_element: str
    root_type: str


# --------------------------------------------------------------------------- parsing


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _doc(node: etree._Element) -> str:
    doc = node.find("xs:annotation/xs:documentation", _NS)
    return _collapse("".join(doc.itertext())) if doc is not None else ""


def _parse_fields(ct: etree._Element) -> tuple[str, list[SchemaField]]:
    """Return (base_type_name, fields) for a complex type, flattening xs:extension."""
    extension = ct.find("xs:complexContent/xs:extension", _NS)
    base = extension.get("base", "") if extension is not None else ""
    container = extension if extension is not None else ct

    fields: list[SchemaField] = []
    sequence = container.find("xs:sequence", _NS)
    if sequence is not None:
        for el in sequence.findall("xs:element", _NS):
            fields.append(
                SchemaField(
                    name=el.get("name", ""),
                    type_ref=el.get("type", ""),
                    is_attribute=False,
                    min_occurs=int(el.get("minOccurs", "1")),
                    max_occurs=el.get("maxOccurs", "1"),
                    required=True,
                    doc=_doc(el),
                )
            )
    for at in container.findall("xs:attribute", _NS):
        required = at.get("use", "optional") == "required"
        fields.append(
            SchemaField(
                name=at.get("name", ""),
                type_ref=at.get("type", ""),
                is_attribute=True,
                min_occurs=1 if required else 0,
                max_occurs="1",
                required=required,
                doc=_doc(at),
            )
        )
    return base, fields


def parse_schema(xsd_path: Path) -> SchemaModel:
    """Parse the enriched XSD into a small, render-ready model (document order preserved)."""
    root = etree.parse(str(xsd_path)).getroot()

    simple_types = [
        SimpleType(
            name=st.get("name", ""),
            base=(r := st.find("xs:restriction", _NS)) is not None and r.get("base", "") or "",
            facets={
                etree.QName(f).localname: f.get("value", "")
                for f in (r if r is not None else [])
                if etree.QName(f).localname in _FACET_OP
            },
            doc=_doc(st),
        )
        for st in root.findall("xs:simpleType", _NS)
    ]

    complex_types = []
    for ct in root.findall("xs:complexType", _NS):
        base, fields = _parse_fields(ct)
        complex_types.append(
            ComplexType(name=ct.get("name", ""), doc=_doc(ct), base=base, fields=fields)
        )

    root_el = root.find("xs:element", _NS)
    return SchemaModel(
        version=root.get("version", ""),
        doc=_doc(root),
        simple_types=simple_types,
        complex_types=complex_types,
        root_element=root_el.get("name", "") if root_el is not None else "",
        root_type=root_el.get("type", "") if root_el is not None else "",
    )


# --------------------------------------------------------------------------- rendering


def _entity_id(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()


def _mermaid_comment(text: str) -> str:
    return text.replace('"', "'")


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _all_fields(ct: ComplexType, by_name: dict[str, ComplexType]) -> list[SchemaField]:
    """Fields of a type including those flattened in from its base, marked as inherited."""
    out: list[SchemaField] = []
    if ct.base in by_name:
        base = by_name[ct.base]
        for bf in _all_fields(base, by_name):
            out.append(dataclasses.replace(bf, inherited_from=bf.inherited_from or base.name))
    out.extend(ct.fields)
    return out


def _relationship(parent_id: str, child_id: str, f: SchemaField) -> str:
    many = f.max_occurs == "unbounded" or int(f.max_occurs) > 1
    right = ("|{" if f.min_occurs >= 1 else "o{") if many else ("||" if f.min_occurs >= 1 else "o|")
    if f.max_occurs == "unbounded":
        label = f"{f.name} ({'1+' if f.min_occurs >= 1 else 'many'})"
    elif int(f.max_occurs) > 1:
        label = f"{f.name} ({f.max_occurs})"
    else:
        label = f.name
    return f'    {parent_id} ||--{right} {child_id} : "{label}"'


def _cardinality(f: SchemaField) -> str:
    if f.is_attribute:
        return "1 (attribute)" if f.required else "0..1 (attribute)"
    if f.max_occurs == "unbounded":
        return f"{f.min_occurs}..*"
    if str(f.min_occurs) == str(f.max_occurs):
        return str(f.min_occurs)
    return f"{f.min_occurs}..{f.max_occurs}"


def _render_erd(model: SchemaModel) -> list[str]:
    by_name = {ct.name: ct for ct in model.complex_types}
    referenced = {
        f.type_local
        for ct in model.complex_types
        for f in ct.fields
        if not f.is_attribute and f.type_local in by_name
    }
    entities = [
        ct for ct in model.complex_types if ct.name == model.root_type or ct.name in referenced
    ]

    lines = ["```mermaid", "erDiagram"]
    for ct in entities:
        pid = _entity_id(ct.name)
        for f in _all_fields(ct, by_name):
            if not f.is_attribute and f.type_local in by_name:
                lines.append(_relationship(pid, _entity_id(f.type_local), f))
    for ct in entities:
        scalars = [f for f in _all_fields(ct, by_name) if f.type_local not in by_name]
        if not scalars:
            continue
        lines.append(f"    {_entity_id(ct.name)} {{")
        for f in scalars:
            lines.append(f'        {f.type_local} {f.name} "{_mermaid_comment(f.doc)}"')
        lines.append("    }")
    lines.append("```")
    return lines


def _type_md(f: SchemaField, complex_names: set[str], simple_names: set[str]) -> str:
    local = f.type_local
    if local in complex_names:
        return f"[`{local}`](#{local.lower()})"
    if local in simple_names:
        return f"[`{local}`](#banded-numeric-types)"
    return f"`{f.type_ref}`"


def render_markdown(model: SchemaModel) -> str:
    by_name = {ct.name: ct for ct in model.complex_types}
    simple_names = {st.name for st in model.simple_types}

    lines = [
        "<!-- DO NOT EDIT BY HAND. Generated from schema/acoustic_dataset.xsd by "
        "`make gen-schema-docs`. -->",
        "<!-- Regenerate after any schema change; CI fails on drift. See docs/decisions/0008 "
        "and 0009. -->",
        "# Schema reference",
        "",
        "> **Reference (generated)** — produced from `schema/acoustic_dataset.xsd` "
        f"(version `{model.version}`) by `make gen-schema-docs`. Every entity, field, range and "
        "definition below is read from the XSD's `xs:annotation/xs:documentation`, so this page "
        "cannot drift from the contract.",
        "",
    ]
    if model.doc:
        lines += [model.doc, ""]

    lines += ["## Entity-relationship diagram", ""]
    lines += _render_erd(model)
    lines += [
        "",
        "Legend: `||--||` one-to-one, `||--|{` one-to-(one-or-many), `||--o{` "
        "one-to-(zero-or-many). The number in each label is the exact cardinality the schema "
        "enforces. Sonar sub-types show their inherited fields inline.",
        "",
        "## Entities",
        "",
    ]
    for ct in model.complex_types:
        suffix = f" (root element `{model.root_element}`)" if ct.name == model.root_type else ""
        section = [f"### {ct.name}{suffix}", ""]
        if ct.doc:
            section += [ct.doc, ""]
        if ct.base:
            section += [
                f"Extends [`{ct.base}`](#{ct.base.lower()}); inherited fields are marked below.",
                "",
            ]
        section += ["| Field | Type | Cardinality | Definition |", "|---|---|---|---|"]
        for f in _all_fields(ct, by_name):
            inherited = f" *(from {f.inherited_from})*" if f.inherited_from else ""
            name_cell = f"`{f.name}`{inherited}"
            section.append(
                f"| {name_cell} | {_type_md(f, set(by_name), simple_names)} "
                f"| {_cardinality(f)} | {_cell(f.doc)} |"
            )
        section.append("")
        lines += section

    lines += [
        "## Banded numeric types",
        "",
        "The numeric primitives below carry real XSD range facets, so an out-of-band value fails "
        "the validation gate.",
        "",
        "| Type | Base | Range | Definition |",
        "|---|---|---|---|",
    ]
    for st in model.simple_types:
        range_text = ", ".join(
            f"{_FACET_OP[k]} {st.facets[k]}" for k in _FACET_ORDER if k in st.facets
        ) or "—"
        lines.append(f"| `{st.name}` | `{st.base}` | {range_text} | {_cell(st.doc)} |")
    lines.append("")

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- entry point


def _render_examples(example_input: Path) -> list[str]:
    """Worked examples generated from the canonical pipeline run, so they cannot drift:

    a trimmed sample document, typed-object usage, and a field *derived* from elementary physics.
    """
    from acoustic_dataset import acoustics, serialize
    from acoustic_dataset.mapping import to_model

    raw = acoustics.load_input(example_input)
    platform = to_model(acoustics.calculate(raw))
    xml = serialize.to_xml(platform)

    characteristics = platform.characteristics
    radiated = platform.radiated_noise
    sensors = platform.sensors
    assert characteristics is not None and radiated is not None and sensors is not None
    active = sensors.active
    assert active is not None and active.source_level is not None and active.max_range is not None

    # Trim the document to a compact but representative excerpt (the bulk is radiated noise).
    ns = serialize.NAMESPACE
    root = etree.fromstring(xml.encode("utf-8"), etree.XMLParser(remove_blank_text=True))
    rn = root.find(f"{{{ns}}}RadiatedNoise")
    if rn is not None:
        bands = rn.findall(f"{{{ns}}}Band")
        for extra in bands[1:]:
            rn.remove(extra)
        rn.append(etree.Comment(" bands 2-10 omitted for brevity "))
        directional = bands[0].find(f"{{{ns}}}Directional") if bands else None
        if directional is not None:
            for extra in directional.findall(f"{{{ns}}}Sector")[2:]:
                directional.remove(extra)
            directional.append(etree.Comment(" sectors 3-12 omitted for brevity "))
    excerpt = etree.tostring(root, pretty_print=True, encoding="unicode").rstrip()

    sl = float(active.source_level)
    dt = float(raw["sensors"]["active"]["detectionThresholdDb"])
    derived = acoustics.active_max_range_m(sl, dt)

    return [
        "## Example document",
        "",
        "A validated document produced by `make pipeline` from "
        "`examples/calculation_input.json` (most radiated-noise detail elided):",
        "",
        "```xml",
        excerpt,
        "```",
        "",
        "## Working with the typed objects",
        "",
        "The pipeline maps calculation output **once** onto the generated dataclasses; tests "
        "assert on those typed objects (the testable boundary) and they serialise straight to XML:",
        "",
        "```python",
        "from acoustic_dataset import acoustics, serialize",
        "from acoustic_dataset.mapping import to_model",
        "",
        'result = acoustics.calculate_from_file("examples/calculation_input.json")',
        "platform = to_model(result)            # a generated Platform object",
        "",
        f"platform.name                          # {platform.name!r}",
        f"platform.characteristics.draft         # Decimal('{characteristics.draft}')",
        f"len(platform.radiated_noise.band)      # {len(radiated.band)}",
        f"platform.sensors.active.max_range      # Decimal('{active.max_range}')",
        "",
        "xml = serialize.to_xml(platform)       # -> the validated document shown above",
        "```",
        "",
        "## Worked example: deriving a value from elementary physics",
        "",
        "Not every element is copied from the input — some are **computed** from typed inputs. "
        "The active sonar's maximum echo range is one: it falls out of the sonar equation under "
        "two-way spherical spreading.",
        "",
        "An echo travels out *and back*, so transmission loss is `TL = 40 * log10(r)` dB at "
        "range `r` metres. The platform can just detect the returning echo when its source level, "
        "less that loss, reaches the detection threshold — solve for `r`:",
        "",
        "```text",
        "SL - 40*log10(r) = DT     =>     r = 10 ** ((SL - DT) / 40)",
        "```",
        "",
        f"This platform's active sonar transmits at `SL = {sl:g}` dB with a detection threshold "
        f"`DT = {dt:g}` dB, so:",
        "",
        "```python",
        "from acoustic_dataset.acoustics import active_max_range_m",
        f"active_max_range_m({sl:g}, {dt:g})   # => {derived:.3f}  (metres)",
        "```",
        "",
        f"That typed result is exactly what serialises into the document as "
        f"`<MaxRange>{active.max_range}</MaxRange>` — elementary physics over typed inputs, "
        "schema-valid XML out.",
        "",
    ]


def generate(schema_path: Path, out_dir: Path, example_input: Path | None = None) -> Path:
    """Write the generated schema reference to ``<out_dir>/index.md`` and return its path.

    When ``example_input`` is given, append worked examples (a sample document, typed-object
    usage, and a physics-derived field) computed from that input via the pipeline.
    """
    model = parse_schema(schema_path)
    md = render_markdown(model)
    if example_input is not None:
        md = md.rstrip("\n") + "\n\n" + "\n".join(_render_examples(example_input)) + "\n"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.md"
    out_file.write_text(md, encoding="utf-8")
    return out_file
