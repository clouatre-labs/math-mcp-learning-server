# Audit: GitHub Actions Minutes Optimization -- October 2026

Date: 2026-10-05  
Base: afa5cad (origin/main)  
Visibility: public repo (standard and arm64 runner minutes free; optimization target is wall-clock and pointless runs, not cost)  
Required checks: DCO and CI Result (rulesets `Main Branch Protection` #13365825, `Protect main branch` #10860043)  
Evidence: `gh run list` per workflow (30-day window), job-level durations from `/actions/runs/{id}/jobs` over the last 20 CI runs (completed_at minus started_at), ruleset reads via `gh api`

## See Also

- [2026-08-22-scheduled-security-audit-actionability.md](2026-08-22-scheduled-security-audit-actionability.md) -- prior CI-adjacent audit in this directory

## Question

Can GitHub Actions minutes consumption in this repository be reduced while keeping functionality, security posture, and merge-gate guarantees identical?

## Answer (short)

No change is justified by measured data. Baseline CI consumption is approximately 32 billed-minutes per week on free standard runners, with a roughly 2-minute wall clock per run. The pipeline already implements every validated optimization pattern: arm64 runners, `dorny/paths-filter` in-workflow gating with an aggregate `CI Result` job (`if: always()`) as the sole required check, per-ref `concurrency` with `cancel-in-progress`, dependency caches, SHA-pinned actions, and fail-fast job ordering. No idle polling, stub jobs, path-filter starvation, or duplicate expensive steps were found.

## Summary Table

| # | Waste pattern | Finding | Verdict | Estimated saving | Priority |
|---|---------------|---------|---------|------------------|----------|
| W1 | Duplicate push runs on main after merge | ~2.5 push runs/week re-test a tree identical to the just-tested squash-merge PR head; however, the push run is the only verification of the merge commit itself against the branch ruleset | REJECTED | ~5 billed-min/week (already free) | none |
| W2 | Trigger-level `paths:` starvation | REUSE workflow uses trigger-level path filters, but REUSE is not a required check (only DCO and CI Result are), and the filters cover every content path REUSE could flag | NO ACTION | ~1 billed-min/week | none |
| W3 | Draft/bot PRs running full CI | Only bot activity is one Renovate lock-file PR, where running CI is the desired behavior | NO ACTION | ~0 | none |
| W4 | Idle/polling, stub jobs, missing concurrency, uncached installs | None present; audit confirmed concurrency groups, uv/npm caches, and parallel jobs | NONE FOUND | n/a | none |
| W5 | Required-check starvation after removing filters | `ci.yml` has no trigger-level path filter and `ci-result` runs with `if: always()`, so CI Result reports on every PR | NONE FOUND | n/a | none |

## Evidence Detail

### CI job means (last 20 runs, n=20 each)

| Job | Mean (min) | Total (20 runs) |
|-----|------------|-----------------|
| test | 0.78 | 15.6 |
| zizmor | 0.27 | 5.4 |
| Type Check | 0.18 | 3.7 |
| security | 0.17 | 3.5 |
| commitlint | 0.14 | 2.9 |
| Detect Changes | 0.09 | 1.8 |
| lint | 0.09 | 1.7 |
| Check Branch Base | 0.07 | 1.5 |
| CI Result | 0.05 | 1.0 |
| test-http-integration | skipped (tag-only) | n/a |

### Frequency and totals

- 60 pull_request runs plus ~15 push runs in the last 30 days: ~17 CI runs/week.
- Per-run billed time is the job-mean sum (~1.84 min; jobs run in parallel).
- Weekly CI total: ~32 billed-minutes on free standard runners; wall clock ~2 minutes per run.
- Other workflows: release ~monthly, scorecard and scheduled-security-audit weekly and short, REUSE ~16 runs/week at ~10 seconds, markdown-lint only on `.md` paths.

### W1 detail (the only candidate above threshold)

Squash merges make the main-branch tree identical to the tested PR head, so the push-triggered CI run on main re-tests the same content. Skipping it would save ~5 billed-minutes/week but would remove the only run that verifies CI green on the actual merge commit referenced by the branch ruleset. A merge-gate guarantee may not be traded for free minutes; rejected.

## No-action list

- REUSE, markdown-lint, aptu (org-managed), scorecard, and scheduled-security-audit workflows: each is already path-filtered, scheduled, or externally dispatched; all consume negligible minutes.
- Release workflow: tag-triggered only, ~monthly, already gated on GPG signature verification.
