# Advanced Typing and Language Features (Python 3.13)

> This section documents forward-looking Python 3.13 typing features and best
> practices to improve clarity, correctness, and tooling support. Use these
> features to write expressive, modern Python.

## `enum.Enum`, `enum.IntEnum`, `enum.StrEnum`

Use `Enum` for fixed sets of related constants. Use `enum.auto()` to avoid
repeating values manually. Use `IntEnum` or `StrEnum` when interoperability
with integers or strings is required (e.g. for database or JSON serialisation).

```python
import enum

class Status(enum.Enum):
    PENDING = enum.auto()
    COMPLETE = enum.auto()

class ErrorCode(enum.IntEnum):
    OK = 0
    NOT_FOUND = 404

class Role(enum.StrEnum):
    ADMIN = enum.auto()
    GUEST = enum.auto()
```

Use `auto()` when exact values are unimportant and you want to avoid
duplication. Avoid `auto()` in `IntEnum` where numeric meaning matters.

## `match` / `case` (Structural Pattern Matching)

Use structural pattern matching for branching over structured data. This is
especially useful for enums, discriminated unions, or pattern-rich data
structures.

```python
def handle_status(status: Status) -> str:
    match status:
        case Status.PENDING:
            return "Still processing"
        case Status.COMPLETE:
            return "Done"
```

## Generic Class Declarations (PEP 695)

Use bracketed class-level type variables directly for generic class
declarations.

```python
class Box[T]:
    def __init__(self, value: T):
        self.value = value
```

This is cleaner and avoids the indirection of separate `TypeVar` declarations.

## `Self` Type (PEP 673)

Use `Self` in fluent interfaces and builder-style APIs to indicate the method
returns the same instance.

```python
import typing

class Builder:
    def add(self, value: int) -> typing.Self:
        self.values.append(value)
        return self
```

This improves tool support and enforces correct chaining semantics.

## `@override` Decorator (PEP 698)

Use `@override` to indicate that a method overrides one from a superclass. This
enables static analysis tools to detect typos and signature mismatches.

```python
import typing

class Base:
    def run(self) -> None:
        ...

class Child(Base):
    @typing.override
    def run(self) -> None:
        print("Running")
```

This decorator is a no-op at runtime but improves tooling correctness.

## `TypeIs` (PEP 742)

Use `TypeIs[T]` to define custom runtime type guards that narrow types in type
checkers.

```python
import typing

def is_str_list(val: list[object]) -> typing.TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)
```

Unlike `isinstance`, this informs the type checker that `val` is now
`list[str]`.

## Defaults for TypeVars (PEP 696)

Allow generic classes/functions to fall back to default types when no specific
type is provided.

```python
T = typing.TypeVar("T", default=int)

class Box[T]:
    def __init__(self, value: T | None = None):
        # Fallback to the TypeVar default (int in this example)
        self.value: T = value if value is not None else int()  # type: ignore[arg-type]
```

This makes APIs more ergonomic while retaining type safety.

## Standard Library Generics (PEP 585)

Use built-in generics from the standard library (`list`, `dict`, `tuple`, etc.)
instead of `typing.List`, `typing.Dict`, etc.

```python
names: list[str] = ["Alice", "Bob"]
```

This reduces imports and reflects the modern style.

## Union Syntax and Optional (PEP 604)

Use `|` to write union types, and `A | None` instead of `Optional[A]`.

```python
value: int | None = None
```

This is more concise and readable, especially for nested types.

## Type Aliases using `type`

Use the `type` keyword to create type aliases with better IDE and runtime
support.

```python
type StrDict = dict[str, str]
```

This replaces `StrDict = TypeAlias = ...` and is preferred in modern Python.

When compatibility with Python < 3.12 is required, keep the older
`typing.TypeAlias` syntax and add `# noqa: UP040` so `ruff` does not flag it.
Place alias definitions after the import block and group shared aliases in
`bournemouth.types` to avoid duplication.

## `from __future__ import annotations`

Use this import in modules with type annotations to defer evaluation of
annotation expressions to runtime. This prevents issues with forward references
and circular imports.

```python
from __future__ import annotations
```

Recommended in all modern Python files using type hints.

## `if typing.TYPE_CHECKING`

Use this conditional to guard imports required only for static typing.

```python
import typing

if typing.TYPE_CHECKING:
    from mypackage.internal import InternalType
```

This avoids runtime import costs or circular imports.

## Standard Aliases

Use the following import aliases consistently:

```python
import datetime as dt
import collections.abc as cabc
```

This simplifies common types such as `dt.datetime`, `cabc.Iterable`,
`cabc.Callable`, and helps disambiguate usage.

______________________________________________________________________

These conventions promote clarity, tool compatibility, and future-ready Python.
