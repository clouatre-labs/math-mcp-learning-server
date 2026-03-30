# ADR-008: Annotation Quality Enforcement via Introspection Tests

## Status
Accepted

## Context
MCP tool and parameter descriptions are the primary routing and usage signal for the LLM
calling the server. A parameter defined as `name: str` with no `Field(description=...)` produces
`{"type": "string"}` in the JSON Schema -- no guidance for the model. No MCP ecosystem linter
exists for this (MCP Inspector checks protocol compliance; mcp-scan checks security; neither
checks annotation quality).

Audit of the codebase found 17 parameters missing descriptions and 5 enum-like parameters
missing `examples` arrays. These gaps accumulated silently because nothing caught them at test
time. The same pattern was identified and addressed in
[code-analyze-mcp PR #590](https://github.com/clouatre-labs/code-analyze-mcp/pull/590).

## Decision
Add `tests/test_annotations.py` that introspects the live MCP schema via
`async with Client(mcp) as client: tools = await client.list_tools()` and asserts:

1. Every tool has a non-empty `description`.
2. Every parameter in `inputSchema.properties` has a non-empty `description`.
3. Every string-typed parameter has a non-empty `description` (tighter regression guard).
4. Known enum-like parameters have `examples` or `enum` in their schema entry.

Tests are data-driven: violations are collected into a list and the assertion prints all
offenders at once, not just the first.

Fix all 17 missing descriptions and 5 missing examples in the same PR so the tests pass
immediately and serve as a regression guard going forward.

## Consequences
- Any parameter added without `Field(description=...)` fails CI.
- New enum-like parameters must be added to the `enum_like_params` dict in the test; this
  is a manual step documented in the test's docstring.
- No new dependencies; uses the existing `fastmcp.client.Client` already in the test suite.
