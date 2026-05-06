# Prefer Generators Over Complex Loop Logic

Using generators improves readability, composability, and memory efficiency.
Functions built as generators are often simpler to test, debug, and refactor.
This guidance encourages breaking apart complex `for`-loops into generator
expressions or functions using `yield`.

## Why Prefer Generators?

- **Clarity:** Isolating data flow from control flow clarifies logic.
- **Efficiency:** Generators are lazy; they avoid building intermediate data
  structures unless needed.
- **Composability:** Generators can be pipelined with other iterators using
  `itertools` or comprehensions.

## Example: Filtering and Transforming

### Complex Loop (harder to read/test)

```python
def get_names(users):
    result = []
    for user in users:
        if user.active and user.name:
            result.append(user.name.upper())
    return result
```

### Generator-Based Version (clearer)

```python
def iter_user_names(users):
    for user in users:
        if user.active and user.name:
            yield user.name.upper()

def get_names(users):
    return list(iter_user_names(users))
```

Or with a comprehension:

```python
def get_names(users):
    return [user.name.upper() for user in users if user.active and user.name]
```

## Example: Chaining Filters and Mappings

```python
from itertools import islice

def top_active_emails(users):
    emails = (
        user.email.lower()
        for user in users
        if user.active and user.email is not None
    )
    return list(islice(emails, 10))
```

## Use Generators When

- You're iterating and filtering/mapping data.
- You want to make early returns or short-circuit behaviour clearer.
- The function logically produces a sequence over time.

## Avoid Overcomplicating

Don't convert everything into generators unnecessarily. Use them to simplify
logic—not obscure it.

### BAD

```python
def iter_numbers():
    yield from (x * 2 for x in range(10) if x % 2 == 0)
```

### BETTER

```python
def iter_even_doubles():
    for x in range(10):
        if x % 2 == 0:
            yield x * 2
```

______________________________________________________________________

**Rule of thumb:** If your `for` loop has multiple branches, mutations, or is
hard to explain in one sentence—try rewriting it as a generator.

Prefer clear, linear data flows over deeply nested conditionals and loop bodies.
