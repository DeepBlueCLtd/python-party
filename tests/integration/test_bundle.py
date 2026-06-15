"""Distribution-bundle tests (T030, US4 / FR-016).

The bundle must ship the three artifacts together — data + schema + generated models — and must
refuse to produce a partial bundle when a component is missing.
"""

from __future__ import annotations

import pytest

from acoustic_dataset import bundle
from acoustic_dataset.cli import main


def test_bundle_contains_data_schema_and_models(tmp_path, schema_path, golden_path, models_dir):
    out = tmp_path / "dist"
    result = bundle.build_bundle(out, schema=schema_path, data=golden_path, models_dir=models_dir)

    assert (out / "schema" / schema_path.name).is_file()
    assert (out / "data" / golden_path.name).is_file()
    assert list((out / "models").glob("*.py")), "expected the generated models in the bundle"
    assert (out / "MANIFEST.md").is_file()
    # The result object reflects what was actually written.
    assert result.schema.is_file() and result.data.is_file() and result.models


def test_bundle_data_is_copied_verbatim(tmp_path, schema_path, golden_path, models_dir):
    out = tmp_path / "dist"
    bundle.build_bundle(out, schema=schema_path, data=golden_path, models_dir=models_dir)
    assert (out / "data" / golden_path.name).read_text(encoding="utf-8") == golden_path.read_text(
        encoding="utf-8"
    )


def test_missing_data_raises_and_writes_nothing(tmp_path, schema_path, models_dir):
    out = tmp_path / "dist"
    with pytest.raises(bundle.BundleError, match="data"):
        bundle.build_bundle(
            out, schema=schema_path, data=tmp_path / "nope.xml", models_dir=models_dir
        )
    assert not out.exists(), "a partial bundle must not be left behind on failure"


def test_missing_models_raises(tmp_path, schema_path, golden_path):
    with pytest.raises(bundle.BundleError, match="models"):
        bundle.build_bundle(
            tmp_path / "dist", schema=schema_path, data=golden_path, models_dir=tmp_path / "empty"
        )


def test_cli_bundle_exits_zero_and_writes(tmp_path, schema_path, golden_path, models_dir, capsys):
    out = tmp_path / "dist"
    rc = main(
        [
            "bundle",
            "--out", str(out),
            "--schema", str(schema_path),
            "--data", str(golden_path),
            "--models", str(models_dir),
        ]
    )
    assert rc == 0
    assert "bundle ok" in capsys.readouterr().out
    assert (out / "schema" / schema_path.name).is_file()


def test_cli_bundle_missing_component_exits_nonzero(tmp_path, schema_path, models_dir, capsys):
    rc = main(
        [
            "bundle",
            "--out", str(tmp_path / "dist"),
            "--schema", str(schema_path),
            "--data", str(tmp_path / "absent.xml"),
            "--models", str(models_dir),
        ]
    )
    assert rc == 1
    assert "missing" in capsys.readouterr().err
