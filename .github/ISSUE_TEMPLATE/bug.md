---
name: Bug
about: Report a defect or unexpected behavior
title: "[BUG] "
labels: bug
assignees: ""
---

## Summary
<!-- 1-2 sentences: what is broken? Be specific about the symptom, not the suspected cause. -->

Example: "Tool `calculate` crashes when dividing by zero. Expected a descriptive error result, got an unhandled exception."

## Steps to Reproduce
<!-- Numbered list of exact steps to trigger the bug. Include tool name, inputs, and MCP client. -->

1.
2.
3.

Example:
1. Connect to the server with Claude Desktop
2. Call tool `calculate` with expression `"1/0"`
3. Observe: unhandled exception instead of error message

## Expected Behavior
<!-- What should happen? -->

## Actual Behavior
<!-- What actually happens? Include error messages or stack traces. -->

```
<paste full error output or stack trace here>
```

## Environment

- OS: macOS / Linux / Windows (specify version)
- Python version: `python --version`
- Package version: check `pyproject.toml`
- MCP client: Claude Desktop / goose / other
- Tool or resource called: exact name and inputs

## Logs / Error Output

```
<paste full error output here>
```

## Root Cause Analysis
<!-- Optional: hypothesis with file path and line range. -->

Example: "Suspected cause: `src/math_mcp/eval.py` line 42 does not guard against division by zero before calling `eval()`."

## Fix Direction
<!-- Optional: suggested approach or pattern to follow. -->

## Acceptance Criteria

- [ ] Bug is reproducible with provided steps
- [ ] Root cause identified and documented
- [ ] Fix implemented and verified
- [ ] Regression test added covering the bug scenario
- [ ] All existing tests pass (`uv run pytest tests/ -v`)
- [ ] Linting passes (`uv run ruff check src/ tests/`)
- [ ] Commit GPG signed and DCO signed-off
