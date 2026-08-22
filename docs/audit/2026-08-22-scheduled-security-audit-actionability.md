# Audit: Scheduled Security Audit Actionability

Date: 2026-08-22
Commit: e617352
Version: v0.12.3
Toolchain: zizmor 1.29.0 / poutine-action v1.1.4 / zizmor-action v0.6.2 / Renovate (config:best-practices)

## Purpose

PR [#462](https://github.com/clouatre-labs/math-mcp-learning-server/pull/462) adds `scheduled-security-audit.yml`, re-running `pip-audit`, `zizmor`, and `poutine` on a weekly cron so CVE and Actions-security drift is caught even when nobody touches `src/**` or `.github/workflows/**` for a while. That schedule is the right instinct, but a scan that runs and drops its output has not, by itself, closed the loop from detection to remediation.

This audit answers three questions raised before merging #462:

1. **What is the actual result of the scheduled run, and how is it actionable today?**
2. **Given Renovate is already running in this repo, is #462 redundant?**
3. **Can remediation be automated safely through Renovate or the org's own `aptu` / `aptu-github-app`, without adding a maintenance burden or risking breakage?**

## Methodology

Four independent research delegates (Claude Haiku 4.5) ran in parallel via Workflow, each verifying one claim against primary sources (action READMEs/`action.yml` via WebFetch and `gh api`, Renovate docs via Context7, web search for corroboration), followed by an adversarial pass that read all four reports back and flagged unsourced or speculative claims. Findings below are stated only where corroborated by an action's own `action.yml`/README or by official Renovate documentation; the two areas where sourcing was weaker (pip-audit vs. Dependabot coverage overlap) are flagged as such rather than asserted. The `poutine` finding (S02) was confirmed directly by reading `boostsecurityio/poutine-action`'s `action.yml` and `boostsecurityio/poutine`'s CLI `--help` output, not by the research delegates. The addendum (below) was confirmed by reading `aptu-github-app`'s worker source (`worker/src/config.ts`, `worker/src/index.ts`) and `aptu`'s CLI source (`crates/aptu-cli/src/cli.rs`, `src/commands/scan_security.rs`) directly, not from README prose alone.

## Scope

| Area | Files / surfaces examined |
|------|---------------------------|
| CI workflows | `.github/workflows/ci.yml`, `.github/workflows/scheduled-security-audit.yml` |
| Dependency automation | `renovate.json`, GitHub Dependabot alerts (`vulnerability-alerts` API) |
| aptu integration | `.github/aptu.yml`, `aptu-github-app` worker source, `aptu` CLI source |
| External action internals | `zizmorcore/zizmor-action`, `boostsecurityio/poutine-action`, `github/codeql-action/upload-sarif` |

No application source (`src/math_mcp/**`) was touched or in scope.

## Summary

*Table 1: Findings and resolution.*

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| S01 | High | `zizmor` findings not persisted to Code Scanning | Fixed -- [#463](https://github.com/clouatre-labs/math-mcp-learning-server/pull/463) |
| S02 | High | `poutine` produces no signal (dead input, no fail threshold, SARIF discarded) | Fixed -- [#463](https://github.com/clouatre-labs/math-mcp-learning-server/pull/463) |
| S03 | Medium | Renovate not wired to native GitHub vulnerability alerts | Fixed -- [#463](https://github.com/clouatre-labs/math-mcp-learning-server/pull/463) |
| S04 | Info | `aptu-github-app` cannot ingest external SARIF or run on a schedule | Backlog candidate, not implemented |
| S05 | Info | `pip-audit` schedule redundancy with Dependabot alerts | No action; confirmed non-redundant |
| A01 | Info | Fix wired entirely through free, public-repo GitHub features -- no GHAS | Confirmed, no action needed |
| A02 | Info | `.github/aptu.yml`'s `scan.enabled` layer is complementary, not conflicting | Confirmed, no action needed |
| A03 | Low | `aptu`'s own `src/**` scan has the same schedule gap S01/S02 had | Backlog candidate, not implemented |

## Findings

### S01 -- HIGH -- `zizmor` findings are printed, never persisted or triaged

**Files:** `.github/workflows/ci.yml`, `.github/workflows/scheduled-security-audit.yml`

Both workflows ran `zizmor-action` with `advanced-security: false`. Per the action's own documentation, that mode prints findings to the console and emits workflow annotations, and explicitly **does not** upload SARIF to GitHub Code Scanning. `advanced-security: true` does upload SARIF, requires nothing but the already-free GitHub Code Scanning feature for public repositories (this repo is public), and -- notably -- does not fail the job on findings; it relies on Code Scanning's own triage state (open/dismissed/fixed) instead of a pass/fail gate. `advanced-security: true` requires `security-events: write` on the job, which `false` mode does not.

Net effect before this audit: a zizmor finding on the weekly schedule produced a console log entry inside a GitHub Actions run nobody was looking at, with no persistent record, no dismiss/triage state, and no diff against the previous week's findings.

**Fix:** Set `advanced-security: true` and add `security-events: write` in both workflows. Verified locally with `zizmor --min-severity medium` against the full `.github/workflows/` tree: no new findings introduced, `No findings to report`.

---

### S02 -- HIGH -- `poutine` currently produces no signal at all

**Files:** `.github/workflows/ci.yml`, `.github/workflows/scheduled-security-audit.yml`

Two independent, compounding defects:

1. Both workflows pass `with: action: analyze_local` to `poutine-action`. Reading the action's `action.yml` directly shows it accepts exactly two inputs, `format` and `output` -- there is no `action` input. The wrapper script always runs `poutine analyze_local "$GITHUB_WORKSPACE" --format "$INPUT_FORMAT" > "$INPUT_OUTPUT"` regardless. GitHub Actions silently ignores unrecognized `with:` keys, so `action: analyze_local` has never had any effect; it happens to describe what the action always does anyway.
2. `poutine`'s own CLI only exits non-zero on findings if invoked with `--fail-on-violation` (confirmed via `poutine`'s `--help` text: "Exit with a non-zero code (10) when violations are found"). `poutine-action` does not expose that flag through its two inputs, and the workflows don't set it via a config file. `format` defaults to `sarif` and `output` defaults to `results.sarif`, so a SARIF file **is** generated on every run -- and then discarded when the runner is torn down, since neither workflow uploads or archives it.

Net effect before this audit: the `poutine` job has run in `ci.yml` on every code-path PR since it was added, always exits 0, and its findings have never been visible anywhere -- not in logs (stdout is redirected into the SARIF file), not as annotations, not in Code Scanning, not as a failed check.

**Fix:** Drop the meaningless `action: analyze_local` input, add `security-events: write`, and add a `github/codeql-action/upload-sarif` step reading the `results.sarif` the action already produces by default. This mirrors S01's philosophy: report via Code Scanning's triage state rather than hard-failing CI on a tool that has no built-in severity threshold exposed through its GitHub Action wrapper.

---

### S03 -- MEDIUM -- Renovate is already installed but not wired to CVE alerts

**File:** `renovate.json`

Renovate's `config:best-practices` preset (confirmed via Context7 against `docs.renovatebot.com`) extends `config:recommended` with digest-pinning and similar hardening defaults, but does **not** enable vulnerability-alert-driven PRs. That requires an explicit `vulnerabilityAlerts.enabled: true` (wired to GitHub's native Dependabot alerts) or `osvVulnerabilityAlerts: true` (Renovate's own OSV.dev-backed, currently-experimental path). Neither was present.

Separately confirmed: this repository already has GitHub's native Dependabot alerts (vulnerability alerts) turned on -- `gh api repos/clouatre-labs/math-mcp-learning-server/vulnerability-alerts` returns `204 No Content`, GitHub's documented "enabled" response. That data source was sitting unused: Renovate wasn't configured to act on it, and nothing else in CI files a remediation PR from a CVE hit.

This is the direct answer to "can we use Renovate for remediation": yes, and it required no new service, no new credentials, and no new code to maintain -- only a config flag on infrastructure already running in this repo.

**Fix:** Add `"vulnerabilityAlerts": { "enabled": true }` to `renovate.json`. Renovate's existing `packageRules` (automerge on patch/minor/digest/pin) already apply to whatever PRs this produces, so no further wiring is needed for low-risk updates; anything crossing a major version still lands as a normal PR for review, unchanged from today's behavior.

---

### S04 -- INFO -- `aptu-github-app` is not a fit for this loop today, and that's fine

`aptu-github-app`'s `scan.enabled` feature (per its README) dispatches `aptu scan-security` on `pull_request` push events only, runs aptu's own local pattern-based scanner, and uploads its own SARIF. It has no `schedule` trigger and no path to ingest SARIF or findings produced by an external tool (`pip-audit`, `zizmor`, `poutine`). Building that ingestion path now would mean writing and maintaining new Worker/Action code to reproduce what GitHub Code Scanning (S01, S02) and Renovate's vulnerability alerts (S03) already do for free, natively, with no additional surface for this team to operate.

This is not a gap worth closing under "low-maintenance, safe, nothing breaks": `aptu` and `aptu-github-app` are well-suited to AI-assisted PR review and issue triage, which is a different job than CVE/workflow-security remediation. If a future need emerges for cross-tool SARIF aggregation with AI-generated remediation summaries, a scheduled-dispatch + external-SARIF-ingestion capability would be a reasonable `aptu-github-app` feature request -- filed there, not built as a one-off here.

**No action taken.** Noted for the backlog, not implemented.

---

### S05 -- INFO -- `pip-audit` on the schedule is not redundant with Renovate/Dependabot, but the overlap claim needed a caveat

GitHub's dependency graph and Dependabot alerts do cover Python projects using `uv.lock` (per Astral's own Dependabot integration docs), and with S03 fixed, a Dependabot-sourced CVE hit now produces a Renovate PR automatically. `pip-audit` draws from the PyPI Advisory Database / OSV.dev rather than the GitHub Advisory Database, so the two have overlapping but non-identical coverage; the research pass corroborated the data-source distinction from primary sources but could not corroborate the stronger claim ("pip-audit catches vulnerabilities Dependabot definitively misses") beyond secondary blog sources, so that stronger claim is not asserted here.

Practically: `pip-audit` costs one `uv tool run pip-audit` invocation on a weekly schedule and provides a second, differently-sourced check on the exact resolved lockfile. That is a reasonable defense-in-depth trade for the cost. **Keep it as-is.**

---

## Is PR #462 pertinent given Renovate is already in use?

**Yes.** Renovate's GitHub Actions support (confirmed via Context7 against `docs.renovatebot.com/modules/manager/github-actions`) is limited to version and digest pin bumping. It performs no static analysis of workflow YAML for injection risk, excessive permissions, or supply-chain issues -- that is exactly what `zizmor` and `poutine` do, and nothing else in this repo's toolchain covers it. The `pip-audit` leg has partial conceptual overlap with Dependabot alerts (S05) but is not made redundant by them. The unrelated `typecheck` gating fix in #462 is an orthogonal, correct bug fix.

**Recommendation: merge #462 as-is.** The actionability gaps (S01, S02) predate #462 in `ci.yml` and were simply copied into the new scheduled workflow; they are not a reason to hold #462, only a reason for the follow-up in [#463](https://github.com/clouatre-labs/math-mcp-learning-server/pull/463).

**Update (2026-08-22):** #462 has merged. #463 has auto-merge enabled, pending its CI run against `main`.

---

## Addendum: `aptu.yml` interaction, cost, and format alignment

Three questions came up after the initial findings above: does this fix interact with the repo's existing `.github/aptu.yml`, does it stay entirely within GitHub's free tier, and does this document's own format line up with `aptu-coder`'s `docs/audit/` convention. Answered by reading source directly rather than README prose, per the Methodology note above.

### A01 -- INFO -- Everything here runs on GitHub's free tier

`math-mcp-learning-server` is a public repository. Every mechanism S01-S03 rely on is free for public repos with no GitHub Advanced Security (GHAS) license: GitHub Code Scanning (SARIF upload/storage, used by `advanced-security: true` in S01 and the `upload-sarif` step in S02) is GHAS-gated only on private repositories; GitHub Actions minutes are unmetered on public repos; and Dependabot alerts (the vulnerability-alerts API checked in S03) have been a free, native feature on all repositories, public or private, since 2022 -- no GHAS involved at all. Renovate's own hosted GitHub App is free for public/open-source repositories; `vulnerabilityAlerts.enabled: true` is a config flag, not a paid feature toggle. Nothing in #462 or #463 introduces a paid GitHub feature.

### A02 -- INFO -- `.github/aptu.yml`'s scan layer is complementary, not conflicting

This repo's `.github/aptu.yml` already has `scan.enabled: true` with `path: src/`, dispatching `aptu scan-security` (local pattern matching, no AI required) on every PR push and uploading its own SARIF to Code Scanning. That is a third, independent SARIF producer alongside zizmor (workflow injection/permission risk) and poutine (workflow supply-chain risk) -- three tools, three non-overlapping scopes (`src/**` app-code patterns vs. `.github/workflows/**` vs. dependency CVEs), all landing in the same Security tab under distinct tool names with no collision. Nothing in S01-S03 changes what aptu scans or how; the two systems were never coupled and stay that way.

One correction to the initial finding write-up: the publicly documented `scan.fail-on` values (`none`/`warning`/`error`) do not match either the actual worker code or the actual CLI. `aptu-github-app`'s `worker/src/config.ts` passes `scan['fail-on']` through as an opaque string with no enum validation, and `aptu`'s own CLI (`crates/aptu-cli/src/cli.rs`, `src/commands/scan_security.rs`) takes `--fail-on` as a comma-separated list of severities (e.g. `critical,high`) matched against `aptu-core`'s severity types. This repo's `fail-on: critical,high` matches the real implementation exactly -- it is not a misconfiguration, the README is just stale relative to the shipped code.

### A03 -- LOW -- `aptu`'s own scan has the same schedule gap S01/S02 had

`scan.enabled` only dispatches on `pull_request` push events (confirmed in `worker/src/index.ts`), same as the S04 finding already noted. That means `aptu scan-security`'s coverage of `src/**` goes stale between touches to that path, for the same reason `pip-audit`/`zizmor`/`poutine` did before #462 -- nobody has to touch `src/**` for the pattern scan to go unexercised for weeks. Unlike S04's ingestion gap, this one has a direct, no-new-code fix available: `aptu scan-security` ships as a standalone CLI/Action (`aptu scan-security . --sarif-output findings.sarif`, local pattern matching only, no `ai` block or API key required per its own docs), so it could be added as a fourth job in `scheduled-security-audit.yml` alongside `pip-audit`/`zizmor`/`poutine` with an `upload-sarif` step, matching the pattern S01/S02 established.

**Not implemented here** -- this audit was scoped to #462's own three checks, and adding a fourth scanner is a new capability rather than a fix to what #462 shipped. Flagged for a decision on whether to extend the schedule.

---

## Recommended Action Order

1. ~~Merge #462 as originally written.~~ **Done, 2026-08-22.**
2. Merge #463 (S01-S03 fixes) on top of it. **Auto-merge enabled, 2026-08-22; pending CI.**
3. **S04/A03** -- optional, same shape: extend `scheduled-security-audit.yml` with a fourth `aptu scan-security` job (A03), and/or file a feature-request issue against `aptu-github-app` for native scheduled-dispatch + external-SARIF-ingestion (S04) if cross-tool AI-summarized triage becomes valuable later. Neither is blocking; both are additive.
