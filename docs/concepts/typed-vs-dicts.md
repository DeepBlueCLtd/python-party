# Typed objects vs. dictionaries

> **Explanation** — why the pipeline carries data in typed objects generated from the schema,
> not in generic `dict`s. See [ADR 0002](../decisions/0002-drop-csv-pickle-and-write_xml.md): we
> deliberately dropped the CSV/pickle/dict baton-pass.

The example input arrives as JSON, which Python loads into nested `dict`s. It would be tempting
to thread those dicts straight through to the XML. We don't — the pipeline maps them **once**
onto the [generated dataclasses](../reference/schema/index.md) and works with those. Here's why.

## The generic dictionary (what we avoid)

```python
from acoustic_dataset import acoustics

raw = acoustics.load_input("examples/calculation_input.json")   # nested dicts

raw["sensors"]["active"]["sourceLevelDb"]   # 215.0  — a float; the unit lives only in the key
raw["snesors"]                              # KeyError — a typo anywhere fails only at runtime
raw["sensors"]["active"].get("srcLevel")    # None   — or fails *silently*, with no error at all
```

A `dict` is an opaque bag of `Any`:

- **No structure** — every access is a stringly-typed guess; the editor can't autocomplete and a
  typo (`snesors`, `srcLevel`) isn't caught until that line runs — or never, if you used `.get`.
- **No types** — values are `float`/`str`/`Any`; nothing says `sourceLevelDb` is decibels, and a
  bare `7.5` could be metres, feet, or a mistake.
- **No validation** — a nonsense value (a 9999 dB source level) flows straight through; nothing
  stops it becoming schema-invalid XML downstream.

## The typed object (what the pipeline uses)

```python
from acoustic_dataset import acoustics, serialize
from acoustic_dataset.mapping import to_model

platform = to_model(acoustics.calculate_from_file("examples/calculation_input.json"))

platform.sensors.active.source_level   # Decimal('215.000') — the exact type the schema declares
platform.sensors.active.sourceLevel    # AttributeError + a mypy error — the typo is caught
xml = serialize.to_xml(platform)       # the object graph *is* the document
```

The generated dataclasses encode the contract:

- **Typos are caught** — statically by `mypy` and at runtime by `AttributeError`, never silently.
- **Precise types** — `Decimal` (exact, not a lossy `float`); the field name plus its docstring
  (lifted from the XSD's `xs:documentation`) carry the meaning, and the
  [schema reference](../reference/schema/index.md) documents the whole shape.
- **Validated at one boundary** — the single mapping rejects anything outside the schema's bands
  *before* serialisation:

```python
import dataclasses
from acoustic_dataset.mapping import to_model, MappingError

result = acoustics.calculate_from_file("examples/calculation_input.json")
# the schema bounds Decibels to [-200, 300]; force an impossible source level:
bad = dataclasses.replace(
    result, active_sonar=dataclasses.replace(result.active_sonar, source_level_db=9999.0)
)
to_model(bad)        # raises MappingError — a dict would have passed 9999 straight through
```

## The pay-off

| | `dict` | Typed object |
|---|---|---|
| Find a field | guess a string key | attribute + autocomplete |
| Wrong name | `KeyError` / silent `None`, at runtime | `mypy` error + `AttributeError` |
| Value type | `Any` / `float` | `Decimal`, schema-banded |
| Units / meaning | only in the key name | field name + generated docstring |
| Bad value | flows through | `MappingError` at the boundary |
| Is it the contract? | no — an ad-hoc shape | yes — generated from the XSD |

This is the **typed, testable boundary** the pipeline is built around (FR-010): tests assert on
these objects directly, and they serialise straight to validated XML. Every behaviour shown here
is checked in `tests/unit/test_typed_vs_dict.py`, so the comparison can't quietly rot.
