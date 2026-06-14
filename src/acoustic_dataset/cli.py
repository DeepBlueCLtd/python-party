"""``acoustic`` command-line surface (contracts/cli-commands.md).

The subcommand names, argument names and exit-code semantics are the contract that tests
and CI bind to; internal module layout is not. Each command stays a thin wrapper that
dispatches to a focused module.

Exit codes: 0 = success; 1 = a real failure (validation, mapping, generation, a missing
bundle component, or a meaningful comparison difference); 2 = an argparse usage error.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PKG_DIR.parent.parent

DEFAULT_SCHEMA = _REPO_ROOT / "schema" / "acoustic_dataset.xsd"
DEFAULT_INPUT = _REPO_ROOT / "examples" / "calculation_input.json"
DEFAULT_OUT = _REPO_ROOT / "build" / "acoustic_dataset.xml"


def cmd_generate(args: argparse.Namespace) -> int:
    from acoustic_dataset import generate

    return generate.main(
        ["--schema", str(args.schema), "--out", str(args.out)]
        if args.out
        else ["--schema", str(args.schema)]
    )


def cmd_pipeline(args: argparse.Namespace) -> int:
    """Map input -> objects -> XML -> validate -> round-trip; write only if both gates pass."""
    from acoustic_dataset import acoustics, serialize, validate
    from acoustic_dataset.mapping import MappingError, to_model

    result = acoustics.calculate_from_file(args.input)
    try:
        model = to_model(result)
    except MappingError as exc:
        print(f"error: mapping rejected a value before serialisation: {exc}", file=sys.stderr)
        return 1

    xml = serialize.to_xml(model)
    report = validate.validate(xml, args.schema)
    if not report.ok:
        print("error: structural gate failed; no artifact written:", file=sys.stderr)
        for err in report.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml, encoding="utf-8")
    # radiated_noise is Optional on the generated model (3.9-compatible, no kw_only); the gates
    # above guarantee it is populated by the time we get here.
    bands = model.radiated_noise.band if model.radiated_noise else []
    print(f"pipeline ok: {len(bands)} band(s) -> {out} (schema-valid, round-trip-equal)")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Run the structural gate (XSD validity + round-trip) on an existing XML file."""
    from acoustic_dataset import validate

    report = validate.validate(Path(args.xml), args.schema)
    if report.ok:
        print(f"valid: {args.xml} is schema-valid and round-trip-equal")
        return 0
    print(f"invalid: {args.xml}", file=sys.stderr)
    for err in report.errors:
        print(f"  - {err}", file=sys.stderr)
    return 1


def cmd_gen_schema_docs(args: argparse.Namespace) -> int:
    """Generate the schema reference + Mermaid ERD from the enriched XSD."""
    from acoustic_dataset import schema_docs

    out_file = schema_docs.generate(args.schema, args.out)
    print(f"schema docs ok: generated {out_file} from {args.schema}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Migration-safety diff: catch schema-valid-but-different output vs a reference."""
    from lxml import etree

    from acoustic_dataset import compare as compare_mod

    generated, reference = args.generated, args.reference
    for path in (generated, reference):
        if not path.is_file():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1

    try:
        result = compare_mod.compare(generated, reference)
    except etree.XMLSyntaxError as exc:
        print(f"error: could not parse XML: {exc}", file=sys.stderr)
        return 1

    if result.equal:
        print(f"match: {generated} is canonically identical to {reference}")
        return 0
    print(
        f"different: {generated} is schema-shaped but differs from {reference}",
        file=sys.stderr,
    )
    print(result.diff, file=sys.stderr)
    return 1


def cmd_bundle(args: argparse.Namespace) -> int:
    """Assemble the distribution bundle: data + schema + generated models."""
    from acoustic_dataset import bundle

    try:
        result = bundle.build_bundle(
            args.out, schema=args.schema, data=args.data, models_dir=args.models
        )
    except bundle.BundleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"bundle ok: {result.out_dir} "
        f"(schema + data + {len(result.models)} generated model file(s))"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acoustic", description="XML Acoustic Dataset pipeline (Phase 1)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Regenerate typed models from the XSD (xsdata).")
    p_gen.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    p_gen.add_argument("--out", type=Path, default=None)
    p_gen.set_defaults(func=cmd_generate)

    p_pipe = sub.add_parser("pipeline", help="End-to-end map -> serialise -> validate.")
    p_pipe.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p_pipe.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    p_pipe.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p_pipe.set_defaults(func=cmd_pipeline)

    p_val = sub.add_parser("validate", help="Structural gate (XSD + round-trip) on an XML file.")
    p_val.add_argument("--xml", type=Path, required=True)
    p_val.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    p_val.set_defaults(func=cmd_validate)

    p_doc = sub.add_parser(
        "gen-schema-docs", help="Generate schema reference + Mermaid ERD from the XSD (US5)."
    )
    p_doc.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    p_doc.add_argument("--out", type=Path, default=_REPO_ROOT / "docs" / "reference" / "schema")
    p_doc.set_defaults(func=cmd_gen_schema_docs)

    p_cmp = sub.add_parser("compare", help="Migration-safety diff vs a reference (US3).")
    p_cmp.add_argument("generated", type=Path, help="The freshly generated XML to check.")
    p_cmp.add_argument(
        "reference", type=Path, help="The known-good reference XML to compare against."
    )
    p_cmp.set_defaults(func=cmd_compare)

    p_bun = sub.add_parser("bundle", help="Distribution bundle: data + schema + models (US4).")
    p_bun.add_argument("--data", type=Path, default=DEFAULT_OUT, help="The XML artifact to ship.")
    p_bun.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    p_bun.add_argument("--models", type=Path, default=_PKG_DIR / "models")
    p_bun.add_argument("--out", type=Path, default=_REPO_ROOT / "build" / "dist")
    p_bun.set_defaults(func=cmd_bundle)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
