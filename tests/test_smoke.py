"""Smoke tests: prove the environment is wired up and green.

These exist so a contributor opening the Codespace can run `make verify` and get a
clear pass before any pipeline code is written (validates the zero-to-green story in
docs/tutorials/01-start-here.md). They are replaced/expanded by real pipeline tests
as the implementation tasks land.
"""

from __future__ import annotations

import sys

import acoustic_dataset


def test_package_imports():
    assert acoustic_dataset.__version__


def test_running_interpreter_meets_target_floor():
    # The target system is constrained to Python 3.9; we develop on that floor.
    assert acoustic_dataset.supported_python()
    assert sys.version_info[:2] >= (3, 9)
