---
name: Feature
about: Propose a new feature or enhancement
title: "[FEATURE] "
labels: enhancement
assignees: ""
---

## Summary
<!-- 1-2 sentences: what to build and what user need it addresses. Be specific. -->

Example: "Add a `statistics` tool exposing mean, median, and standard deviation. Enables basic statistical analysis without leaving the MCP client."

## Context
<!-- Why does this matter? What depends on it? Link to related issues or ADRs. -->

- Problem solved:
- Users or workflows that benefit:
- Blocking dependencies (if any):

## Prerequisites

- Depends on: #N (if applicable)

## Implementation Notes
<!-- Key decisions, patterns to follow, relevant file paths and line ranges. -->

### Strategy

1.

### Code Examples

```python
# expected usage or API pattern
```

### Integration Notes

- Tool registration: `src/math_mcp/server.py`
- Follow existing tool pattern: `src/math_mcp/tools/calculate.py`
- Error handling: raise `ValueError` with descriptive message
- Testing: add tests under `tests/`

## Acceptance Criteria

- [ ] Feature implemented per summary
- [ ] Follows project conventions (`docs/ARCHITECTURE.md`)
- [ ] All existing tests pass (`uv run pytest tests/ -v`)
- [ ] Linting passes (`uv run ruff check src/ tests/`)
- [ ] New tests cover happy path and at least one edge case
- [ ] Documentation updated (if applicable)
- [ ] Commit GPG signed and DCO signed-off

## Not In Scope
<!-- Explicit boundaries to prevent scope creep. -->
