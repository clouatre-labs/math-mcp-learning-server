---
name: Bug
about: Report a defect or unexpected behavior
title: "[BUG] "
labels: bug
assignees: ""
---

## Summary
<!-- 1-2 sentences: what is broken? Symptom, not suspected cause. -->

## Steps to Reproduce
<!-- Exact steps to trigger the bug. Include tool name, inputs, and MCP client. -->

1.
2.
3.

## Expected Behavior
<!-- What should happen? -->

## Actual Behavior
<!-- What actually happens? -->

```
<paste error output or stack trace here>
```

## Environment

- OS:
- Python version: `python --version`
- Package version: check `pyproject.toml`
- MCP client: Claude Desktop / goose / other
- Tool or resource called:

## Root Cause Analysis
<!-- Optional: hypothesis with file path and line range. -->

## Acceptance Criteria

- [ ] Bug is reproducible with provided steps
- [ ] Root cause identified
- [ ] Fix implemented and verified
- [ ] Regression test added
- [ ] All tests pass (`uv run pytest tests/ -v`)
- [ ] Linting passes (`uv run ruff check src/ tests/`)
- [ ] Commit GPG signed and DCO signed-off
