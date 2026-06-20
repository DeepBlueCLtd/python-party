"""Scratch file for Adventure 2 — experience editor autocomplete on a typed object.

Open this file in VS Code (the Codespace has Pylance), then follow the TODO below.
It is safe to edit freely; nothing else imports it. Run it any time with:

    python examples/explore_platform.py
"""

from acoustic_dataset import build

# `platform` is a fully-typed `Platform` built from the example input. Pylance knows
# its type from the function's return annotation — no need to run anything first.
platform = build.build_platform_from_file("examples/calculation_input.xml")

# `radiated_noise` is Optional on the schema (it may be absent), so the type checker treats
# it as possibly-None. The pipeline's gates guarantee it is populated here; this assert tells
# Pylance the same thing — after it, `.band` is a clean, fully-typed access (no squiggle).
assert platform.radiated_noise is not None

# TODO: put your cursor at the end of the next line, after the dot, and type.
# VS Code should pop up the declared attributes (band, ...).
# Keep drilling — `platform.radiated_noise.band[0].` completes too, all the way down.
# platform.radiated_noise.

# A couple of fully-typed accesses to confirm it ran (delete or extend these freely):
print("type:", type(platform).__name__)
print("first band centre frequency:", platform.radiated_noise.band[0].centre_frequency)
