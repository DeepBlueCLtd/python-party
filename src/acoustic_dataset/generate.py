"""Generate typed dataclass models from the XSD via xsdata.

This is the *only* code that turns the schema into Python. It is schema-agnostic: it
hard-codes no element names, so swapping in the real XSD (contracts/pipeline-contract.md)
needs no edits here — just re-run ``make generate``.

Two deliberate post-processing steps make the output fit our constraints:

1. **3.9 compatibility** — xsdata (>=26) emits ``@dataclass(kw_only=True)`` unconditionally,
   but ``kw_only`` is Python 3.10+. The target system is pinned to 3.9.4
   (docs/decisions/0007), so we strip it. The schema is modelled so field ordering stays
   valid without ``kw_only`` (no required field follows a defaulted one).
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
from pathlib import Path

# src/acoustic_dataset/generate.py -> parents: [acoustic_dataset, src, <repo root>]
_PKG_DIR = Path(__file__).resolve().parent
_SRC_DIR = _PKG_DIR.parent
_REPO_ROOT = _SRC_DIR.parent

DEFAULT_SCHEMA = _REPO_ROOT / "schema" / "acoustic_dataset.xsd"
DEFAULT_OUT = _PKG_DIR / "models"
_TARGET_PACKAGE = "acoustic_dataset.models"

_HEADER = (
    "# DO NOT EDIT BY HAND.\n"
    "# Generated from schema/acoustic_dataset.xsd by `make generate` (xsdata).\n"
    "# Regenerate after any schema change; CI fails on drift. See docs/decisions/0008.\n"
)

# xsdata >=26 always emits kw_only=True; strip it for the Python 3.9 target.
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


def _postprocess(out_dir: Path) -> None:
    for py in sorted(out_dir.glob("*.py")):
        original = py.read_text(encoding="utf-8")
        body = _make_39_compatible(original)
        if not body.startswith(_HEADER):
            body = _HEADER + body
        py.write_text(body, encoding="utf-8")


def _import_check() -> None:
    """Import the freshly generated package so broken output fails loudly."""
    importlib.invalidate_caches()
    mod_name = f"{_TARGET_PACKAGE}.acoustic_dataset"
    sys.modules.pop(_TARGET_PACKAGE, None)
    sys.modules.pop(mod_name, None)
    try:
        importlib.import_module(mod_name)
    except Exception as exc:  # noqa: BLE001 - re-raised as a typed error with context
        raise GenerationError(
            f"Generated models failed to import ({exc!r}). "
            "The schema may need different field ordering for the 3.9 target."
        ) from exc


def generate(schema: Path = DEFAULT_SCHEMA, out: Path = DEFAULT_OUT) -> Path:
    """Regenerate typed models from ``schema`` into ``out``.

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
    # run it from the src/ root to land output at src/acoustic_dataset/models/.
    cmd = [
        sys.executable, "-m", "xsdata", "generate", str(schema),
        "--package", _TARGET_PACKAGE,
        "--structure-style", "filenames",
        "--no-include-header",  # deterministic output (no version/timestamp) for the drift gate
    ]
    proc = subprocess.run(cmd, cwd=str(_SRC_DIR), capture_output=True, text=True)
    if proc.returncode != 0 or not out.is_dir():
        raise GenerationError(
            "xsdata generation failed:\n"
            f"  cmd: {' '.join(cmd)}\n"
            f"  stdout: {proc.stdout.strip()}\n"
            f"  stderr: {proc.stderr.strip()}"
        )

    _postprocess(out)
    _import_check()
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acoustic generate", description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA,
                        help="Path to the XSD (default: schema/acoustic_dataset.xsd)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="Output package dir (default: src/acoustic_dataset/models)")
    args = parser.parse_args(argv)
    try:
        out = generate(args.schema, args.out)
    except GenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    rel = out.relative_to(_REPO_ROOT) if out.is_relative_to(_REPO_ROOT) else out
    print(f"Generated models in {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
