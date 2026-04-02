---
name: Refactor
about: Improve code quality without changing behavior
title: "[REFACTOR] "
labels: refactor
assignees: ""
---

## Summary
<!-- 1-2 sentences: what to refactor and why. -->

## Current State
<!-- What is wrong or suboptimal today. Include file paths and line ranges. -->

## Proposed Changes
<!-- What to change and what pattern to follow. -->

## Acceptance Criteria

- [ ] Behavior unchanged (no functional diff)
- [ ] All existing tests pass (`uv run pytest tests/ -v`)
- [ ] Linting passes (`uv run ruff check src/ tests/`)
- [ ] No new test gaps introduced
- [ ] Commit GPG signed and DCO signed-off
