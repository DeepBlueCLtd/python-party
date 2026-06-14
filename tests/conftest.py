"""Shared fixtures: the on-disk artifacts the pipeline tests read."""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return _REPO_ROOT


@pytest.fixture(scope="session")
def schema_path() -> Path:
    return _REPO_ROOT / "schema" / "acoustic_dataset.xsd"


@pytest.fixture(scope="session")
def input_path() -> Path:
    return _REPO_ROOT / "examples" / "calculation_input.json"


@pytest.fixture(scope="session")
def golden_path() -> Path:
    return _REPO_ROOT / "tests" / "golden" / "acoustic_dataset.xml"
