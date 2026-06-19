"""Generate typed dataclass models from the XSD via xsdata.

This is the *only* code that turns the schema into Python. It is schema-agnostic: it
hard-codes no element names, so changing the schema needs no edits here — just re-run
``make generate``.

Two deliberate post-processing steps make the output fit our constraints:

1. **3.9 compatibility & determinism** — xsdata auto-toggles ``slots`` / ``kw_only`` / PEP-604
   unions by the *generating* interpreter's version, so we pass explicit ``--no-*`` flags to
   force 3.9-compatible output whether models are regenerated on a dev 3.10+ box or the 3.9 CI
   runner — without that, the drift gate would flap across Python versions. (``kw_only``
   stripping below is kept as defence-in-depth.) The target system is pinned to 3.9.4
   (docs/decisions/0007); the schema is modelled so field ordering stays valid without
   ``kw_only`` (no required field follows a defaulted one).
2. **No-drift discipline** — each module gets a deterministic "do not edit" header
   (docs/decisions/0008). Generation is reproducible byte-for-byte, so CI can diff-gate it.

After writing, we import the package to guarantee we never leave broken/partial bindings.
"""

from __future__ import annotations

import argparse
import importlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# src/acoustic_dataset/generate.py -> parents: [acoustic_dataset, src, <repo root>]
_PKG_DIR = Path(__file__).resolve().parent
_SRC_DIR = _PKG_DIR.parent
_REPO_ROOT = _SRC_DIR.parent
_SCHEMA_DIR = _REPO_ROOT / "schema"


@dataclass(frozen=True)
class SchemaSpec:
    """One XSD and where its generated binding lands.

    Each schema generates into its *own* package: the input and output schemas share element
    names (Characteristics, Sensors, RadiatedNoise, ...), so a shared package's ``__init__``
    re-exports would collide. Separate packages keep both bindings unambiguous.
    """

    schema: Path
    out: Path
    package: str  # dotted target package xsdata writes into
    module: str  # module to import-check (xsdata names it after the schema file stem)


# The output dataset schema and the calculation-input schema. ``make generate`` regenerates both.
SCHEMAS = (
    SchemaSpec(
        schema=_SCHEMA_DIR / "acoustic_dataset.xsd",
        out=_PKG_DIR / "models",
        package="acoustic_dataset.models",
        module="acoustic_dataset",
    ),
    SchemaSpec(
        schema=_SCHEMA_DIR / "calculation_input.xsd",
        out=_PKG_DIR / "input_models",
        package="acoustic_dataset.input_models",
        module="calculation_input",
    ),
)

# Kept for back-compat with callers that target the output schema directly.
DEFAULT_SCHEMA = SCHEMAS[0].schema
DEFAULT_OUT = SCHEMAS[0].out


def _header(schema_name: str) -> str:
    return (
        "# DO NOT EDIT BY HAND.\n"
        f"# Generated from schema/{schema_name} by `make generate` (xsdata).\n"
        "# Regenerate after any schema change; CI fails on drift. See docs/decisions/0008.\n"
    )

# Defence-in-depth: strip kw_only if a future xsdata bump emits it despite --no-kw-only.
_KW_ONLY_PATTERNS = (
    "@dataclass(kw_only=True)",  # the common case we emit
)


class GenerationError(RuntimeError):
    """Raised when model generation fails; callers should exit non-zero."""


def _make_39_compatible(text: str) -> str:
    """Remove ``kw_only=True`` so the dataclasses import on Python 3.9."""
    for pat in _KW_ONLY_PATTERNS:
        text = text.replace(pat, "@dataclass")
    # Defensive: handle kw_only combined with other dataclass args, e.g.
    # @dataclass(frozen=True, kw_only=True) -> @dataclass(frozen=True).
    text = re.sub(r",\s*kw_only=True", "", text)
    text = re.sub(r"kw_only=True,\s*", "", text)
    text = text.replace("@dataclass(kw_only=True)", "@dataclass")
    return text


def _postprocess(out_dir: Path, schema_name: str) -> None:
    header = _header(schema_name)
    for py in sorted(out_dir.glob("*.py")):
        original = py.read_text(encoding="utf-8")
        body = _make_39_compatible(original)
        if not body.startswith(header):
            body = header + body
        py.write_text(body, encoding="utf-8")


def _import_check(package: str, module: str) -> None:
    """Import the freshly generated package so broken output fails loudly."""
    importlib.invalidate_caches()
    mod_name = f"{package}.{module}"
    sys.modules.pop(package, None)
    sys.modules.pop(mod_name, None)
    try:
        importlib.import_module(mod_name)
    except Exception as exc:  # noqa: BLE001 - re-raised as a typed error with context
        raise GenerationError(
            f"Generated models failed to import ({exc!r}). "
            "The schema may need different field ordering for the 3.9 target."
        ) from exc


def generate(
    schema: Path = DEFAULT_SCHEMA,
    out: Path = DEFAULT_OUT,
    *,
    package: str = SCHEMAS[0].package,
    module: str = SCHEMAS[0].module,
) -> Path:
    """Regenerate typed models from ``schema`` into ``out`` (package ``package``).

    Returns the output directory. Raises :class:`GenerationError` on any failure,
    never leaving partial output (the target directory is rebuilt atomically-ish:
    cleared, regenerated, then post-processed and import-checked).
    """
    schema = Path(schema).resolve()
    out = Path(out).resolve()
    if not schema.is_file():
        raise GenerationError(f"Schema not found: {schema}")

    # Clean slate so removed schema types never linger as stale modules.
    if out.exists():
        shutil.rmtree(out)

    # xsdata maps the dotted package onto the filesystem relative to its cwd, so we
    # run it from the src/ root to land output at src/<package path>/.
    cmd = [
        sys.executable, "-m", "xsdata", "generate", str(schema),
        "--package", package,
        "--structure-style", "filenames",
        "--no-include-header",  # deterministic output (no version/timestamp) for the drift gate
        # Force 3.9-compatible output regardless of the generating interpreter, so the committed
        # models are byte-identical whether regenerated on a dev 3.10+ box or the 3.9 CI runner
        # (xsdata otherwise auto-toggles these by sys.version_info). See docs/decisions/0007.
        "--no-slots",
        "--no-kw-only",
        "--no-union-type",
        "--no-postponed-annotations",
    ]
    proc = subprocess.run(cmd, cwd=str(_SRC_DIR), capture_output=True, text=True)
    if proc.returncode != 0 or not out.is_dir():
        raise GenerationError(
            "xsdata generation failed:\n"
            f"  cmd: {' '.join(cmd)}\n"
            f"  stdout: {proc.stdout.strip()}\n"
            f"  stderr: {proc.stderr.strip()}"
        )

    _postprocess(out, schema.name)
    _import_check(package, module)
    return out


def generate_all(specs: tuple[SchemaSpec, ...] = SCHEMAS) -> list[Path]:
    """Regenerate every project schema, each into its own package."""
    return [
        generate(s.schema, s.out, package=s.package, module=s.module) for s in specs
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acoustic generate", description=__doc__)
    parser.add_argument("--schema", type=Path, default=None,
                        help="Path to a single XSD (default: regenerate all schema/*.xsd).")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output package dir for a single --schema run.")
    args = parser.parse_args(argv)
    try:
        if args.schema is None:
            outs = generate_all()
        else:
            # Single-schema run: infer the package from --out (default: the output schema's).
            out = args.out or DEFAULT_OUT
            package = ".".join(["acoustic_dataset", *out.resolve().relative_to(_PKG_DIR).parts]) \
                if out.resolve().is_relative_to(_PKG_DIR) else SCHEMAS[0].package
            outs = [generate(args.schema, out, package=package, module=args.schema.stem)]
    except GenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for out in outs:
        rel = out.relative_to(_REPO_ROOT) if out.is_relative_to(_REPO_ROOT) else out
        print(f"Generated models in {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
