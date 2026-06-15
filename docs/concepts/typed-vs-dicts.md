# Typed data, end to end

> **Explanation** — once you are writing Python in this pipeline the data lives in **typed
> objects from start to finish**: a structured set of parameters, the calculation result, the
> generated models, then XML. The only loosely-typed moment is the raw JSON at the very edge,
> parsed *once* at a single boundary. This page shows that end-to-end typed flow, and what
> strong typing buys you over a generic `dict`. See
> [ADR 0002](../decisions/0002-drop-csv-pickle-and-write_xml.md).

## Start from a structure, not a bag of keys

If you begin from a **set of parameters held in a structure**, every later stage can stay
typed — there is never a point where the data degrades into an untyped `dict` you have to
trust by convention. The pipeline already works this way: the acoustic seams return a typed
`CalculationResult`, the single mapping turns that into generated model objects, and only those
objects are serialised.

```python
from acoustic_dataset import acoustics
from acoustic_dataset.mapping import to_model

result = acoustics.calculate_from_file("examples/calculation_input.json")
#   result                     -> acoustics.CalculationResult   (a typed dataclass)
#   result.active_sonar        -> acoustics.ActiveSonarResult    (.source_level_db is a float)
#   result.bands[0].sectors[0] -> acoustics.SectorResult(bearing_deg=..., level_db=...)

platform = to_model(result)
#   platform                                              -> models.Platform  (from the schema)
#   platform.radiated_noise.band[0].directional.sector[0] -> models.Sector
```

Each arrow hands a **declared shape** to the next stage. Nothing in this chain is a `dict`: a
field that does not exist is an error on the line that names it, not a surprise three stages
later. Raw JSON is parsed into typed objects at exactly one place, and from there the whole
flow is typed data — which is the whole point of the sections below.

## Storing data in a dictionary

A `dict` places no constraints on what it holds: keys are arbitrary strings and values are `Any`.

```python
record = {}
record["sourceLevel"] = 215.0      # any key, any value type
record["sorceLevel"] = 9999        # a misspelled key is just another entry
record["sourceLevel"] = "loud"     # a string replaces the number, with no objection
```

The structure exists only by convention. A misspelled key, a wrong value type, or an omitted
field is stored as readily as correct data, so a mistake surfaces later — when something reads
the value, when the XML fails validation, or not at all. Carry data this way and *every* stage
downstream inherits that uncertainty; start from a typed structure and none of it does.

## Storing data in a typed object

The generated dataclasses declare which fields exist and the type of each, so the shape of what
is stored is defined up front:

```python
from decimal import Decimal
from acoustic_dataset.models.acoustic_dataset import Sector

Sector(bearing=Decimal("30.000"), level=Decimal("134.000"))   # the declared fields
Sector(bering=Decimal("30.000"), level=Decimal("134.000"))    # TypeError: unexpected 'bering'
```

- A name that is not a declared field is rejected when the object is constructed (`TypeError`),
  where a `dict` would store it under a new key.
- Each field has a declared type — here `Decimal`, as the schema specifies. A type checker
  (`mypy`, run by `make verify`) reports a wrong-typed value before the code runs:

  ```python
  Sector(bearing="thirty", level=Decimal("134.000"))   # mypy: incompatible type "str"
  ```

- The fields and their documentation are generated from the schema, so the stored object follows
  the contract rather than an ad-hoc shape.

## Checking values as they are stored

Field names and types define the *shape*. The single mapping (`to_model`) is where calculation
output is stored into these objects, and it also enforces the schema's numeric **ranges** at that
point:

```python
import dataclasses
from acoustic_dataset import acoustics
from acoustic_dataset.mapping import to_model, MappingError

result = acoustics.calculate_from_file("examples/calculation_input.json")
# Decibels are bounded to [-200, 300]; attempt to store an impossible source level:
bad = dataclasses.replace(
    result, active_sonar=dataclasses.replace(result.active_sonar, source_level_db=9999.0)
)
to_model(bad)        # MappingError — rejected as it is stored, not left for a later stage
```

A `dict` would hold `9999` and pass it on; the typed boundary rejects it.

## Summary

| At the point data is stored | `dict` | Typed object |
|---|---|---|
| Field names | any string accepted | declared; an unknown name is a `TypeError` |
| Value types | `Any` | declared (e.g. `Decimal`), checked by `mypy` |
| Out-of-range values | stored as-is | rejected by the mapping (`MappingError`) |
| Relationship to the schema | convention only | generated from it |
| What downstream stages receive | a shape to trust on faith | a declared structure, all the way to XML |

Hold the whole flow in typed data and these guarantees compound at every stage instead of
having to be re-checked. The behaviours above are checked in `tests/unit/test_typed_vs_dict.py`.
