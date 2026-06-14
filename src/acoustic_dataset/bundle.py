"""Assemble the distribution bundle: data + schema + generated models (US4, FR-016).

The schema is the language-agnostic contract, the generated models are its bindings, and the
emitted XML is the data. Shipping them together gives a consumer the dataset, the contract it
conforms to, and a ready-to-use binding in one place; the CI drift gate guarantees the bindings
match the schema. Output is a plain directory (contracts/cli-commands.md §bundle) so it is
trivial to inspect and to archive downstream.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

_MANIFEST = "MANIFEST.md"


class BundleError(RuntimeError):
    """Raised when a required component is missing; callers should exit non-zero."""


@dataclass
class BundleResult:
    """What a successful bundle contains (paths inside the bundle directory)."""

    out_dir: Path
    schema: Path
    data: Path
    models: list[Path]


def build_bundle(out_dir: Path, *, schema: Path, data: Path, models_dir: Path) -> BundleResult:
    """Assemble data + schema + generated models into ``out_dir``.

    Validates all three components up front and raises :class:`BundleError` before writing
    anything, so a partial/misleading bundle is never produced.
    """
    out_dir, schema, data, models_dir = (Path(p) for p in (out_dir, schema, data, models_dir))
    model_files = sorted(models_dir.glob("*.py")) if models_dir.is_dir() else []

    missing: list[str] = []
    if not schema.is_file():
        missing.append(f"schema ({schema})")
    if not data.is_file():
        missing.append(f"data ({data}) — run `make pipeline` first")
    if not model_files:
        missing.append(f"generated models ({models_dir}) — run `make generate` first")
    if missing:
        raise BundleError("cannot build bundle, missing: " + "; ".join(missing))

    if out_dir.exists():
        shutil.rmtree(out_dir)
    schema_dir, data_dir, models_out = out_dir / "schema", out_dir / "data", out_dir / "models"
    for d in (schema_dir, data_dir, models_out):
        d.mkdir(parents=True)

    shutil.copy2(schema, schema_dir / schema.name)
    shutil.copy2(data, data_dir / data.name)
    copied = []
    for py in model_files:
        dest = models_out / py.name
        shutil.copy2(py, dest)
        copied.append(dest)

    (out_dir / _MANIFEST).write_text(_render_manifest(schema, data, copied), encoding="utf-8")
    return BundleResult(
        out_dir=out_dir,
        schema=schema_dir / schema.name,
        data=data_dir / data.name,
        models=copied,
    )


def _render_manifest(schema: Path, data: Path, models: list[Path]) -> str:
    lines = [
        "# Acoustic Dataset distribution bundle",
        "",
        "The data, its contract, and a ready-to-use binding shipped together so they travel as "
        "one unit (FR-016). The bindings are generated from the schema and kept in sync by the "
        "CI drift gate.",
        "",
        "| Component | File |",
        "|---|---|",
        f"| Schema (contract) | `schema/{schema.name}` |",
        f"| Data (XML Acoustic Dataset) | `data/{data.name}` |",
    ]
    lines += [f"| Generated model | `models/{m.name}` |" for m in models]
    return "\n".join(lines) + "\n"
