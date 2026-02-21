# ADR-005: Pydantic + @validated_tool for Input Validation

## Status
Accepted

## Context
Every MCP tool receives user-provided input that must be validated before use. Options considered:

- **Manual validation**: explicit `if` checks per parameter, per tool. Verbose, inconsistent,
  error-prone to maintain across 20+ tools.
- **dataclasses**: structural typing only; no runtime validation or coercion.
- **Pydantic + validate_call**: declarative type annotations drive automatic coercion, constraint
  enforcement, and structured error messages. Already a FastMCP dependency; zero added weight.

## Decision
Wrap all tool functions with `@validated_tool`, a thin decorator defined in `settings.py`:

```python
# settings.py
def validated_tool(func):
    """Apply Pydantic validation to tool functions with Context support."""
    return validate_call(config={"arbitrary_types_allowed": True})(func)
```

`arbitrary_types_allowed=True` is required to pass FastMCP's `Context` object through
`validate_call` without Pydantic rejecting it as an unknown type.

Constraints are declared inline on function signatures using `Annotated` and `Field`:

```python
# tools/calculate.py (representative example)
async def calculate(
    expression: Annotated[str, Field(max_length=MAX_EXPRESSION_LENGTH)],
    ctx: SkipValidation[Context | None] = None,
) -> dict: ...
```

`SkipValidation[Context | None]` exempts the context parameter from Pydantic processing while
keeping it in the signature for FastMCP's dependency injection.

## Consequences

**Gained:**
- Uniform validation across all tools from a single decorator; no per-tool boilerplate
- Pydantic error messages are structured and descriptive; invalid input surfaces cleanly to callers
- Type coercion handles minor client-side type mismatches automatically
- `Field` constraints (`max_length`, `ge`, `le`) are co-located with the parameter they guard

**Accepted:**
- `validate_call` adds a thin call overhead; negligible for tool-level invocations
- `arbitrary_types_allowed=True` disables Pydantic's strict type checking for `Context`;
  this is intentional and safe because FastMCP controls context injection
