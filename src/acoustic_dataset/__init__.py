"""Acoustic Reference Book — Phase 1 schema-driven XML Acoustic Dataset pipeline (scaffold).

This package is intentionally minimal right now: it establishes a green, runnable
environment (see docs/tutorials/01-start-here.md). The Phase 1 pipeline modules
(mapping, serialize, validate, compare, cli) are added by the implementation tasks
in specs/001-codespace-xml-scaffold/tasks.md.
"""

from __future__ import annotations

__version__ = "0.0.1"

# Minimum Python the target system supports; the scaffold is developed on this floor.
MIN_PYTHON = (3, 9)


def supported_python() -> bool:
    """Return True if the running interpreter meets the target floor (3.9).

    A tiny, honest smoke function: it gives the scaffold something real to test
    before any pipeline code exists, and documents the 3.9 constraint in code.
    """
    import sys

    return sys.version_info[:2] >= MIN_PYTHON
