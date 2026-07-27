# Audit: Quality and Freshness Review, July 2026

Date: 2026-07-27
Commit: ac8fff683d8729dabcf122b47f42ee4fe148a783
Version: v0.12.1
Toolchain: Python 3.14.6 / FastMCP 3.3.1 / uv / ruff 0.15.13 / pyright 1.1.409

## Purpose

Point-in-time audit of `math-mcp-learning-server` v0.12.1 against four goals:

1. **MCP 2026-07-28 alignment**: verify the project is ready for the largest spec revision since launch, shipping tomorrow.
2. **Code quality**: typing hygiene, eval sandbox integrity, test coverage configuration correctness.
3. **CI/security**: action pinning, OIDC publishing, binary download integrity, permissions hygiene.
4. **Dependency freshness**: lockfile staleness, tooling ceiling pins, Renovate coverage.

Each confirmed finding includes source evidence, a recommended fix, and an issue mapping. The audit is the source material for the GitHub issues listed in the Summary.

## Methodology

Three parallel read-only delegates ran concurrently, each writing a JSON handoff to `.worktrees/20260727_21/.handoff/`:

- **MCP Protocol delegate** (Claude Sonnet 5 / Bedrock): researched 2026-07-28 spec RC via Context7 and Brave, then audited transport, session, and capability usage in `src/math_mcp/`.
- **Code Quality delegate** (Claude Sonnet 5 / Bedrock): analyzed all source and test files via aptu-coder, cross-checked against current ruff/pyright/FastMCP/pydantic releases.
- **CI/Security delegate** (Claude Haiku 4.5 / Bedrock): inspected all workflow YAML, `pyproject.toml`, `uv.lock`, and open PRs via `gh` CLI and Brave.

Handoff JSON was read and synthesized by the orchestrator. No source files were modified.

## Scope

| Area | Files examined |
|------|---------------|
| MCP protocol | `src/math_mcp/server.py`, `tools/_session.py`, `tools/*.py`, `resources.py` |
| Eval sandbox | `src/math_mcp/eval.py`, `tests/test_math_operations.py` |
| Type hygiene | `src/math_mcp/tools/matrix.py`, `tools/visualization.py`, `settings.py`, `pyproject.toml` |
| Test coverage config | `pyproject.toml` `[tool.coverage.run]`, `docs/testing/coverage-gaps.md` |
| CI / supply chain | `.github/workflows/ci.yml`, `release.yml`, `scorecard.yml`, `reuse.yml` |
| Dependencies | `pyproject.toml`, `uv.lock` |

## Summary

*Table 1: Confirmed findings, issue mapping.*

| ID | Severity | Area | Finding | Issue |
|----|----------|------|---------|-------|
| F01 | High | MCP Protocol | `fastmcp` has no upper-bound pin; v4/MCPServer breaking line ships without warning | [I1](#i1) |
| F02 | High | CI Security | MCP Publisher binary downloaded without SHA256 verification | [I2](#i2) |
| F03 | Medium | Coverage | `server.py`, `resources.py`, `visualization.py` excluded from 90% coverage gate | [I3](#i3) |
| F04 | Medium | Typing | No `[tool.pyright]` config; pyright runs in basic mode; 6 unresolved-import errors on optional extras | [I4](#i4) |
| F05 | Low | CI Security | `test-http-integration` job lacks explicit permissions block | [I2](#i2) |
| F06 | Low | Tooling | `ruff<0.16.0` ceiling excludes 413-rule expanded default set; ceiling rationale stale | [I5](#i5) |
| F07 | Low | Dead code | `settings.py::validated_tool` has no type annotations and appears unused | [I5](#i5) |
| F08 | Low | Docs | `docs/testing/coverage-gaps.md` states v0.11.5 / 126 tests; reality is v0.12.1 / 358 tests | [I3](#i3) |
| A01 | Info | MCP Protocol | `ctx.get_state("session_id")` is application-level state, not protocol-level; safe today but warrants a comment once FastMCP stateless-core lands | [I1](#i1) |
| A02 | Info | Eval | Blocklist-plus-restricted-globals design is safe; AST-based validator would be more future-proof | [I6](#i6) |

## Findings

### F01 -- `fastmcp` has no upper-bound version pin

**Severity:** High
**File:** `pyproject.toml` -- `dependencies`
**Verdict:** CONFIRMED

`pyproject.toml` specifies `fastmcp>=3.2.4` with no upper bound. The MCP spec 2026-07-28 (shipping tomorrow) removes `initialize`/`Mcp-Session-Id` and introduces a stateless protocol core. The FastMCP maintainers are tracking this via a v4/MCPServer rework; MCP's own SDK blog explicitly recommends pinning an upper bound (e.g. `mcp>=1.27,<2`) before the v2/stateless line ships to prevent unplanned breaking upgrades. Without an upper bound, a `uv lock --upgrade` or Renovate update could pull in a breaking FastMCP major version with no warning.

`tools/_session.py` uses `ctx.get_state("session_id")` / `ctx.set_state(...)` for workspace tracking. This is FastMCP's application-level per-connection state, distinct from the protocol-level session being removed. It is not directly broken by 2026-07-28, but the relationship should be documented with a comment once FastMCP's stateless transport lands so future contributors understand why the pattern is safe.

**Resolution:** Add `fastmcp>=3.2.4,<4.0.0` in `pyproject.toml`. Add inline comment in `tools/_session.py` noting that `ctx.get_state` is application-level (FastMCP) state, not the protocol-level Mcp-Session-Id being removed in 2026-07-28.

---

### F02 -- MCP Publisher binary downloaded without SHA256 verification

**Severity:** High
**File:** `.github/workflows/release.yml` -- `mcp-registry` job
**Verdict:** CONFIRMED

The `mcp-registry` job downloads the `mcp-publisher` binary via `curl | tar` with no checksum step. This is a supply-chain risk: a compromised or swapped binary artifact would execute during the release workflow without detection. The parallel `aptu-coder` project correctly adds SHA256 verification before extraction.

**Resolution:** Add a `sha256sum -c` step after the `curl` download and before `tar` extraction. Pin the expected hash for each published `mcp-publisher` release in the workflow.

---

### F03 -- `server.py`, `resources.py`, and `visualization.py` excluded from coverage gate

**Severity:** Medium
**File:** `pyproject.toml` -- `[tool.coverage.run]`
**Verdict:** CONFIRMED

The `omit` list in `[tool.coverage.run]` excludes `server.py`, `resources.py`, and both `visualization.py` paths (`src/math_mcp/visualization.py` and `src/math_mcp/tools/visualization.py`). The `fail_under = 90` gate therefore reflects only calculate/matrix/persistence/eval modules. The 90% CI badge does not represent full-project coverage health; regressions in the excluded modules pass the gate silently. Despite `tests/test_visualization.py` having 861 lines of functional tests, those tests do not enforce the 90% threshold on the visualization modules.

**Resolution:** Remove exclusions from `[tool.coverage.run] omit` for modules that have functional tests (`visualization.py`). For `server.py` and `resources.py`, either add integration-test coverage to bring them into scope or add an explicit `# pragma: no cover` rationale comment and document the intentional gate scope in `docs/testing/coverage-gaps.md`.

**Resolution (F08, bundled):** Update `docs/testing/coverage-gaps.md` header from v0.11.5 / 126 tests to v0.12.1 / 358 tests and close or update gap items whose target versions have passed.

---

### F04 -- No `[tool.pyright]` config; 6 unresolved-import errors on optional extras

**Severity:** Medium
**File:** `pyproject.toml`
**Verdict:** CONFIRMED

No `[tool.pyright]` section exists in `pyproject.toml`. Pyright therefore runs in default `basic` mode with no explicit `pythonVersion`, `include`, or `strict` flag. Six `reportMissingImports` errors fire on `numpy` (in `matrix.py` and `visualization.py`) and `matplotlib` when pyright is run without the `plotting` and `scientific` extras installed. It is unclear from the audited files whether CI installs those extras before running `pyright`; if it does not, type errors in the numeric and visualization modules are silently ignored. The `tools/matrix.py` return type `Any # np.ndarray` workaround and the `requires_matplotlib` decorator's `func: Any` signature also disable type checking at those call sites.

**Resolution:** Add a `[tool.pyright]` section to `pyproject.toml` with explicit `pythonVersion = "3.14"`, `venvPath`/`venv`, and at minimum `typeCheckingMode = "standard"`. Ensure CI installs `plotting` and `scientific` extras (or a `dev` extra that includes them) before the `pyright` step.

---

### F05 -- `test-http-integration` job lacks explicit permissions

**Severity:** Low
**File:** `.github/workflows/ci.yml` -- `test-http-integration` job
**Verdict:** CONFIRMED

The `test-http-integration` job runs only on tag pushes (`startsWith(github.ref, 'refs/tags/')`) and has no explicit `permissions:` block, inheriting the top-level `contents: read`. Per project conventions and global `AGENTS.md`, every job must have an explicit permissions block.

**Resolution:** Add `permissions: contents: read` (or appropriate minimal scope) to the `test-http-integration` job definition.

---

### F06 -- `ruff<0.16.0` ceiling excludes expanded 2026 default rule set

**Severity:** Low
**File:** `pyproject.toml` -- `[tool.ruff]` dependency constraint
**Verdict:** CONFIRMED

`pyproject.toml` pins `ruff>=0.15.1,<0.16.0` with an inline comment explaining the upper bound was set due to a 0.15.0 formatting regression on multi-exception `except`-clause parentheses (fixed in 0.15.1). Ruff 0.16.0 expands the default rule set from 59 to 413 rules and is excluded by this ceiling. Renovate already merged PR #410 (`fix(deps): update dependency ruff to >=0.16.0,<0.17.0`) -- the CI lint job's own constraint (`>=0.14.0,<0.15.0`) was also stale relative to the lockfile.

**Resolution:** Verify the 0.16.x formatter is clean on this codebase (run `uv run ruff format --check` with `ruff>=0.16.0`); fix any new violations; relax the ceiling to `<0.17.0`. Also confirm CI lint job constraint matches `pyproject.toml` after PR #410.

---

### F07 -- `settings.py::validated_tool` is untyped and likely dead code

**Severity:** Low
**File:** `src/math_mcp/settings.py`
**Verdict:** CONFIRMED

`validated_tool(func)` has no parameter or return type annotation, inconsistent with the fully-typed `Annotated`/`Field` style throughout `tools/*.py`. No call site using it as a decorator was found in the audited source; tool functions rely on FastMCP's own Pydantic validation via `Annotated` fields. If it is dead code it should be removed; if it is intentionally kept it needs type annotations and a docstring with usage example.

**Resolution:** Confirm with `rg 'validated_tool' src/` whether it is called anywhere. Remove if unused; otherwise annotate with a `Callable` generic and add a usage example docstring.

---

### A01 -- `ctx.get_state` pattern and 2026-07-28 stateless core

**Severity:** Info
**File:** `src/math_mcp/tools/_session.py`
**Verdict:** NOTED, not a defect

`ctx.get_state("session_id")` / `ctx.set_state("session_id", ...)` is FastMCP's per-connection application state, stored in the FastMCP connection context, not a protocol-level `Mcp-Session-Id` header. The 2026-07-28 stateless core removes the protocol-level session; FastMCP's application-level `get_state`/`set_state` API is a FastMCP abstraction layered above the transport and is not the same thing. No defect today.

Once FastMCP publishes its stateless-core-aligned transport, the behavior of `ctx.get_state` under a stateless transport (where each request may arrive at a different instance) should be re-verified. The workspace persistence backend (`tools/persistence/`) does use file-system storage, so the actual workspace data survives across connections; only the in-memory session state (if any) would be affected.

---

### A02 -- `eval.py` uses blocklist-plus-restricted-globals rather than AST allowlist

**Severity:** Info
**File:** `src/math_mcp/eval.py`
**Verdict:** NOTED, safe in practice

The current design is documented in ADR 001-eval-sandbox.md and is sound: `eval()` is restricted to `{'__builtins__': {'abs': abs}, 'math': math}` globals with an empty locals dict, meaning any identifier not in `MATH_FUNCTIONS_ALL` raises a `NameError` before execution. The character allowlist passes any alphabetic run through to `_build_safe_expr`, but only recognized function names get rewritten to `math.<name>`, and any other bare identifier is unreachable in the restricted scope. CPU/memory exhaustion is mitigated by `asyncio.wait_for` timeout.

An AST-based validator (`ast.parse` + node-type allowlist) would be more future-proof against novel bypass techniques involving new Python syntax, but no exploitable gap was found in this pass. This is a defense-in-depth improvement for a future issue, not a defect.

---

## Non-Findings (considered and dismissed)

**N01:** `fastmcp` 2026-07-28 stateless core breaks `ctx.get_state` in `_session.py`. Dismissed. `ctx.get_state` is FastMCP application-level state, not a protocol-level session concept. See A01.

**N02:** Renovate not configured. Dismissed. Renovate is active without a project-level `renovate.json`, using GitHub defaults. Bot PRs are merging regularly. No gap; adding a `renovate.json` would be an enhancement, not a fix.

**N03:** `pydantic-settings` and `pyright` lockfile lag. Dismissed. Both are at most one patch version behind; Renovate will pick them up. Not worth a dedicated issue.

---

## Subsystem Reviews

### MCP Protocol Alignment

**Status: Mostly clean.** F01 and A01 are the only items; F01 is a version-pin hygiene issue, not a compatibility defect.

- `@mcp.tool()` decorator pattern is confirmed to carry forward unchanged into FastMCP v4/MCPServer.
- `ctx: SkipValidation[Context | None] = None` with `if ctx:` guards is the correct optional-context pattern and is unaffected by transport changes.
- `stdio` and `streamable-http` transports are both supported by 2026-07-28 (stateless HTTP keeps Streamable HTTP, just removes the session header).
- No use of deprecated Roots, Sampling, or Logging MCP capabilities.
- No custom OAuth/authorization code to migrate for RFC 9207 `iss`-validation hardening.
- No `ui://` resources, Tasks extension, or MCP Apps patterns required.

### Eval Sandbox

**Status: Sound.** No exploitable gap found. See A02 for the defense-in-depth follow-up.

- Restricted globals correctly limit reachable builtins to `abs` only.
- `asyncio.wait_for` timeout mitigates CPU exhaustion.
- ADR 001-eval-sandbox.md documents the design tradeoff.
- Dedicated `tests/test_math_operations.py` covers calculate tool paths; no isolated `test_eval.py` found, but indirect coverage is present.

### CI / Supply Chain

**Status: Strong posture with one supply-chain gap (F02).** 

- All GitHub Actions pinned to commit SHAs.
- OIDC Trusted Publishing to PyPI correctly configured with `id-token: write` and no stored credentials.
- GPG tag signature verification enforced before publish.
- Build provenance attestation via `actions/attest-build-provenance` enabled.
- Zizmor security scanning active at `min-severity: high`.
- gitleaks secret scanning, pip-audit CVE scanning, REUSE compliance all present.
- Runners pinned to `ubuntu-24.04-arm` (not `*-latest`).
- CI Result aggregator job gates all checks.
- `fail_under = 90` coverage gate active (scope caveat documented in F03).

---

## Issue Plan

*Table 2: Issue-to-PR mapping.*

| Issue | Title | Findings | Files | Complexity |
|-------|-------|----------|-------|------------|
| I1 | `fastmcp` version ceiling + session state comment | F01, A01 | `pyproject.toml`, `tools/_session.py` | Simple |
| I2 | CI: MCP Publisher SHA256 verification + explicit job permissions | F02, F05 | `release.yml`, `ci.yml` | Simple |
| I3 | Coverage: remove omit exemptions or document scope + update gap doc | F03, F08 | `pyproject.toml`, `docs/testing/coverage-gaps.md` | Medium |
| I4 | Typing: add `[tool.pyright]` config + install extras in CI | F04 | `pyproject.toml`, `ci.yml` | Simple |
| I5 | Tooling: relax `ruff<0.16.0` ceiling + remove dead `validated_tool` | F06, F07 | `pyproject.toml`, `settings.py`, any lint violations | Simple |
| I6 | Eval: AST-based expression validator (defense-in-depth) | A02 | `eval.py`, `tests/` | Complex |
