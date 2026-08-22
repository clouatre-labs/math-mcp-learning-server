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

Scope: `.github/workflows/ci.yml`, `.github/workflows/scheduled-security-audit.yml`, `renovate.json`, and the `zizmorcore/zizmor-action`, `boostsecurityio/poutine-action`, and Renovate feature surfaces those workflows depend on. No application source was touched.

## Methodology

Four independent research delegates (Claude Haiku 4.5) ran in parallel via Workflow, each verifying one claim against primary sources (action READMEs/`action.yml` via WebFetch and `gh api`, Renovate docs via Context7, web search for corroboration), followed by an adversarial pass that read all four reports back and flagged unsourced or speculative claims. Findings below are stated only where corroborated by an action's own `action.yml`/README or by official Renovate documentation; the two areas where sourcing was weaker (pip-audit vs. Dependabot coverage overlap) are flagged as such rather than asserted. The `poutine` finding (S02) was confirmed directly by reading `boostsecurityio/poutine-action`'s `action.yml` and `boostsecurityio/poutine`'s CLI `--help` output, not by the research delegates.

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

**Recommendation: merge #462 as-is.** The actionability gaps (S01, S02) predate #462 in `ci.yml` and were simply copied into the new scheduled workflow; they are not a reason to hold #462, only a reason for this follow-up.

## Summary

*Table 1: Findings and resolution.*

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| S01 | High | `zizmor` findings not persisted to Code Scanning | Fixed in this PR |
| S02 | High | `poutine` produces no signal (dead input, no fail threshold, SARIF discarded) | Fixed in this PR |
| S03 | Medium | Renovate not wired to native GitHub vulnerability alerts | Fixed in this PR |
| S04 | Info | `aptu-github-app` cannot ingest external SARIF or run on a schedule | Backlog candidate, not implemented |
| S05 | Info | `pip-audit` schedule redundancy with Dependabot alerts | No action; confirmed non-redundant |

**Traceability model going forward:** zizmor and poutine findings land in the repository's Security tab (Code Scanning), where GitHub's own watch/notification settings surface new alerts to maintainers, and each alert carries its own dismiss/fix/reopen history -- no bespoke issue-creation automation was added, since it would duplicate what Code Scanning already provides. CVE findings from Dependabot alerts now flow into Renovate PRs, which carry the existing `dependencies` label and automerge rules. No new service, credential, or scheduled job was introduced beyond what #462 already added.

## Recommended Action Order

1. **Merge #462** as originally written.
2. **Merge this follow-up** (S01-S03 fixes) on top of it. Both are CI-configuration-only changes with no effect on application code, verified locally with `zizmor` before push.
3. **S04** -- optional: file a feature-request issue against `aptu-github-app` for scheduled-dispatch + external-SARIF-ingestion if cross-tool AI-summarized triage becomes valuable later. Not blocking.
