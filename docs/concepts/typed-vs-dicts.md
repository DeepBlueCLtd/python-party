# Typed data, end to end

> **Explanation** — once you are writing Python in this pipeline the data lives in a **typed
> object that meets the schema**, not a loosely-typed `dict`. The only loosely-typed moment is
> the raw JSON at the very edge, parsed *once* inside the pipeline. This page shows what strong
> typing buys you over a generic `dict`. See ADR 0002.

## Work with the schema's data object

The pipeline turns the calculation into **one typed data object that meets the schema** — a
`Platform` generated from the XSD. You work with that object directly: every field is declared,
typed, and documented by the contract, so values never have to live in a loosely-typed `dict`.

```python
from acoustic_dataset import build

input_path = "examples/calculation_input.xml"

# Build the schema's data object directly from the input:
platform = build.build_platform_from_file(input_path)

# It is generated from the XSD; explore it by attribute.
# The IDE autocompletes each step and the values carry
# the schema's Decimal type — no raw JSON key in sight:
print(type(platform).__name__)
# Platform

print(platform.radiated_noise.band[0].centre_frequency)
# 50.000

sector = platform.radiated_noise.band[0].directional.sector[0]
print(sector.bearing, sector.level)
# 0.000 134.000
```

Every value here is a typed attribute of the schema's data object, not a `dict` key. Your IDE
autocompletes each step and a type checker flags a wrong one; the values carry the schema's
`Decimal` type. The raw JSON is parsed once, inside the pipeline, and you never index it by key.

## Storing data in a dictionary

A `dict` places no constraints on what it holds: keys are arbitrary strings and values are `Any`.

```python
record = {}
record["sourceLevel"] = 215.0   # any key, any value type
record["sorceLevel"] = 9999     # misspelled key, stored anyway
record["sourceLevel"] = "loud"  # a string replaces the number
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

# The declared fields are accepted:
Sector(bearing=Decimal("30.000"), level=Decimal("134.000"))

# An unknown field fails at construction:
Sector(bering=Decimal("30.000"), level=Decimal("134.000"))
#   -> TypeError: unexpected keyword argument 'bering'
```

- A name that is not a declared field is rejected when the object is constructed (`TypeError`),
  where a `dict` would store it under a new key.
- Each field has a declared type — here `Decimal`, as the schema specifies. A type checker
  (`mypy`, run by `make verify`) reports a wrong-typed value before the code runs:

  ```python
  # mypy flags a wrong-typed value before the code runs:
  Sector(bearing="thirty", level=Decimal("134.000"))
  #   -> mypy: incompatible type "str"
  ```

- The fields and their documentation are generated from the schema, so the stored object follows
  the contract rather than an ad-hoc shape.

## Checking values as they are stored

Field names and types define the *shape*. The builder is where each value is stored into the
schema object, and it also enforces the schema's numeric **ranges** at that point — a value that
does not meet the schema is rejected before serialisation:

```python
from decimal import Decimal

from acoustic_dataset import build

data = build.load_input("examples/calculation_input.xml")

# Decibels are bounded to [-200, 300]. Force an impossible
# source level into the input, then build the schema object:
data.sensors.active_sonar.active_source_level_db.value = Decimal("9999")
build.build_platform(data)
#   -> MappingError: rejected as it is built,
#      not left for a later stage
```

A `dict` would hold `9999` and pass it on; the builder rejects it because it does not meet the
schema.

## Summary

| At the point data is stored | `dict` | Typed object |
|---|---|---|
| Field names | any string accepted | declared; an unknown name is a `TypeError` |
| Value types | `Any` | declared (e.g. `Decimal`), checked by `mypy` |
| Out-of-range values | stored as-is | rejected by the builder (`MappingError`) |
| Relationship to the schema | convention only | generated from it |
| What downstream stages receive | a shape to trust on faith | a declared structure, all the way to XML |

Hold the whole flow in typed data and these guarantees compound at every stage instead of
having to be re-checked. The behaviours above are checked in `tests/unit/test_typed_vs_dict.py`.
