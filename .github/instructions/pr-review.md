# PR Review Instructions

## Scope

Review only what the PR changes. Do not flag issues in files the PR does not touch.

## Workflow files

When reviewing `.github/workflows/` changes:

- Evaluate the full job context, not individual steps in isolation. A step that installs a binary
  and a step that executes it are part of the same job; verify both exist before flagging a
  missing publish or execution command.
- Flag `${{ expression }}` interpolation directly inside `run:` scripts as an injection risk;
  inputs should be passed via `env:` blocks.
- Verify action pins use commit SHAs, not mutable tags.
- Check that `permissions:` blocks are present and minimal.

## Python

- Do not comment on code style that ruff catches automatically; it is enforced by CI.
- Do not suggest adding type annotations where pyright can already infer them.

## General

- One comment per distinct issue; do not duplicate findings across multiple inline comments.
- Prefer suggesting a fix (suggestion block) over describing the problem when the fix is
  unambiguous.
