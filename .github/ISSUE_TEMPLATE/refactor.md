---
name: Refactor
about: Improve code quality, maintainability, or performance without changing behavior
title: "[REFACTOR] "
labels: refactor
assignees: ""
---

## Summary
<!-- 1-2 sentences: what to improve and why. Be specific about the pain point. -->

Example: "Extract duplicate validation logic from `calculate.py` and `matrix.py` into a shared utility. Reduces duplication and ensures consistent error handling."

## Motivation
<!-- Why now? What pain point triggered this? What will improve? -->

- Current pain point:
- Expected benefit:

## Current State
<!-- Show the problem with file paths and line ranges. -->

File: `src/math_mcp/...` (lines N-N)
```python
<code snippet showing current pattern>
```

Problem: <describe what makes this a problem>

## Proposed Changes
<!-- What to change and how. Reference existing patterns. -->

1.

### Integration Notes
- No public API changes; refactoring is internal only
- Behavior must be identical: same results, same error handling

## Constraints

- Public API must remain unchanged
- Behavior identical: same results and error handling
- All existing tests must pass without modification

## Acceptance Criteria

- [ ] All existing tests pass without modification (`uv run pytest tests/ -v`)
- [ ] Linting passes (`uv run ruff check src/ tests/`)
- [ ] No behavior changes: results and error handling identical
- [ ] New code follows project conventions
- [ ] Commit GPG signed and DCO signed-off

## Not In Scope
<!-- Explicit boundaries to prevent scope creep. -->
