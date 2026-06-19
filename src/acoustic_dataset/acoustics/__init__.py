"""Acoustic calculation seams: the pure functions that compute the dataset's values.

The recalculation/resampling-onto-bands work (FR-012): each physical step is a **discrete,
named, testable function** with the engineering "how it's computed" documented here in code
(FR-013) — definitions of *terms* live in the schema instead.

The maths is a deliberately compact analytic model. From a handful of high-level platform
parameters it synthesises:

* a geometric ladder of band centre frequencies,
* a directional radiated-noise field (a spectral roll-off with frequency plus a cardioid-ish
  directivity lobe around the platform), sampled every 30 degrees, and
* one derived sensor figure (an active sonar's maximum echo range from its source level).

These functions return **plain ``float``s** — the arithmetic, not a data structure. The builder
in :mod:`acoustic_dataset.build` calls them to populate the schema-generated data object
directly (see ADR 0010); there is no intermediate domain hierarchy.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

# ----- individual seam functions (each independently unit-tested) -----


def band_centre_hz(base_hz: float, ratio: float, index: int) -> float:
    """Centre frequency of the ``index``-th band (1-based) of a geometric ladder.

    Bands climb by a fixed ``ratio`` per step (e.g. ``ratio=2`` gives octave spacing), so
    ``f(index) = base_hz * ratio ** (index - 1)``.
    """
    return base_hz * math.pow(ratio, index - 1)


def spectral_rolloff_db(centre_hz: float, base_hz: float, rolloff_db_per_octave: float) -> float:
    """Reduction in radiated level at ``centre_hz`` relative to ``base_hz``, in dB.

    A simple high-frequency roll-off: ``rolloff_db_per_octave`` decibels are shed for every
    octave (doubling) above the base frequency, i.e. ``rolloff * log2(centre / base)``.
    """
    return rolloff_db_per_octave * math.log2(centre_hz / base_hz)


def directivity_db(bearing_deg: float, peak_bearing_deg: float, amplitude_db: float) -> float:
    """Directional modulation of the radiated level at ``bearing_deg``, in dB.

    A single cardioid-ish lobe: the level peaks at ``peak_bearing_deg`` (``+amplitude_db``) and
    troughs at the opposite bearing (``-amplitude_db``), varying as a cosine in between.
    """
    return amplitude_db * math.cos(math.radians(bearing_deg - peak_bearing_deg))


def radiated_level_db(base_level_db: float, rolloff_db: float, directivity_db: float) -> float:
    """Combine the base level, spectral roll-off and directivity into one radiated level (dB)."""
    return base_level_db - rolloff_db + directivity_db


def active_max_range_m(source_level_db: float, detection_threshold_db: float) -> float:
    """Maximum echo range of an active sonar, in metres.

    Inverts two-way spherical-spreading loss (``TL = 40 * log10(r)``): the source level above
    the detection threshold is the loss the echo can afford on its round trip, so
    ``r = 10 ** ((SL - DT) / 40)``.
    """
    return math.pow(10.0, (source_level_db - detection_threshold_db) / 40.0)


def bearings(step_deg: float) -> list[float]:
    """The bearings sampled all round the platform, from 0 up in ``step_deg`` increments.

    A 30-degree step yields the twelve sectors ``0, 30, ..., 330`` the schema expects.
    """
    count = int(round(360.0 / step_deg))
    return [round(step_deg * k, 6) for k in range(count)]


# ----- input loading -----


def load_input(path: Path) -> dict:
    """Read and parse a calculation-input JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
