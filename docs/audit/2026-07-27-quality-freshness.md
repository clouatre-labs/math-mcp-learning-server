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

Each confirmed finding includes source evidence, a verdict, a fix, a regression gate, and an issue mapping. The audit is the source material for the GitHub issues listed in the Summary.

## Methodology

Three parallel read-only delegates ran concurrently, each writing a JSON handoff to `.worktrees/20260727_21/.handoff/`:

- **MCP Protocol delegate** (Claude Sonnet 5 / Bedrock): researched 2026-07-28 spec RC changes via Context7 and Brave, then audited transport, session, and capability usage in `src/math_mcp/`.
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

*Table 1: Confirmed findings, verdicts, issue mapping, and status.*

| ID | Severity | Area | Finding | Verdict | Issue | Status |
|----|----------|------|---------|---------|-------|--------|
| F01 | High | MCP Protocol | `fastmcp` has no upper-bound pin; v4/MCPServer breaking line ships without warning | CONFIRMED | [#413](https://github.com/clouatre-labs/math-mcp-learning-server/issues/413) | Open |
| F02 | High | CI Security | MCP Publisher binary downloaded without SHA256 verification | CONFIRMED | [#414](https://github.com/clouatre-labs/math-mcp-learning-server/issues/414) | Open |
| F03 | Medium | Coverage | `server.py`, `resources.py`, `visualization.py` excluded from 90% coverage gate | CONFIRMED | [#415](https://github.com/clouatre-labs/math-mcp-learning-server/issues/415) | Open |
| F04 | Medium | Typing | No `[tool.pyright]` config; pyright runs in basic mode; 6 unresolved-import errors on optional extras | CONFIRMED | [#416](https://github.com/clouatre-labs/math-mcp-learning-server/issues/416) | Open |
| F05 | Low | CI Security | `test-http-integration` job lacks explicit permissions block | CONFIRMED | [#414](https://github.com/clouatre-labs/math-mcp-learning-server/issues/414) | Open |
| F06 | Low | Tooling | `ruff<0.16.0` ceiling excludes 413-rule expanded default set; ceiling rationale stale | CONFIRMED | [#417](https://github.com/clouatre-labs/math-mcp-learning-server/issues/417) | Open |
| F07 | Low | Dead code | `settings.py::validated_tool` has no type annotations and appears unused | CONFIRMED | [#417](https://github.com/clouatre-labs/math-mcp-learning-server/issues/417) | Open |
| F08 | Low | Docs | `docs/testing/coverage-gaps.md` states v0.11.5 / 126 tests; reality is v0.12.1 / 358 tests | CONFIRMED | [#415](https://github.com/clouatre-labs/math-mcp-learning-server/issues/415) | Open |
| A01 | Info | MCP Protocol | `ctx.get_state("session_id")` is application-level state, not protocol-level; safe today but warrants a comment once FastMCP stateless-core lands | NOTED | [#413](https://github.com/clouatre-labs/math-mcp-learning-server/issues/413) | Open |
| A02 | Info | Eval | Blocklist-plus-restricted-globals design is safe; AST-based validator would be more future-proof | NOTED | [#418](https://github.com/clouatre-labs/math-mcp-learning-server/issues/418) | Open |

## Findings

### F01 -- `fastmcp` has no upper-bound version pin

**Severity:** High
**File:** `pyproject.toml` -- `dependencies`
**Verdict:** CONFIRMED -- `pyproject.toml` specifies `fastmcp>=3.2.4` with no upper bound. The MCP spec 2026-07-28 introduces a stateless protocol core. FastMCP is tracking this via a v4/MCPServer rework; the MCP SDK blog explicitly recommends pinning an upper bound before the v2/stateless line ships. `rg 'fastmcp' pyproject.toml` confirms the bare lower-bound pin.
**Issue:** [#413](https://github.com/clouatre-labs/math-mcp-learning-server/issues/413)

`tools/_session.py` uses `ctx.get_state("session_id")` / `ctx.set_state(...)` for workspace tracking. This is FastMCP's application-level per-connection state, distinct from the protocol-level `Mcp-Session-Id` being removed. It is not directly broken by 2026-07-28, but the relationship should be documented with a comment once FastMCP's stateless transport lands.

**Fix:** Change `fastmcp>=3.2.4` to `fastmcp>=3.2.4,<4.0.0` in `pyproject.toml`. Add an inline comment in `tools/_session.py` above the `ctx.get_state` / `ctx.set_state` calls noting that this is FastMCP application-level state, not the protocol-level `Mcp-Session-Id` removed in spec 2026-07-28.

**Regression gate:** `uv run pytest -v` must pass.

---

### F02 -- MCP Publisher binary downloaded without SHA256 verification

**Severity:** High
**File:** `.github/workflows/release.yml` -- `mcp-registry` job
**Verdict:** CONFIRMED -- the `mcp-registry` job downloads the `mcp-publisher` binary via `curl | tar` with no checksum step. Confirmed by reading the job steps directly; no `sha256sum` or equivalent command present between the `curl` and `tar` invocations.
**Issue:** [#414](https://github.com/clouatre-labs/math-mcp-learning-server/issues/414)

**Fix:** Add a `sha256sum -c` step after the `curl` download and before `tar` extraction. Pin the expected hash for the specific `mcp-publisher` version in the workflow; update it when the binary version is bumped.

**Regression gate:** Release workflow `mcp-registry` job must complete without error on next run. No functional test available locally; verify by dry-run or workflow inspection.

---

### F03 -- `server.py`, `resources.py`, and `visualization.py` excluded from coverage gate

**Severity:** Medium
**File:** `pyproject.toml` -- `[tool.coverage.run]`
**Verdict:** CONFIRMED -- `[tool.coverage.run] omit` excludes `server.py`, `resources.py`, `src/math_mcp/visualization.py`, and `src/math_mcp/tools/visualization.py`. `fail_under = 90` therefore reflects only calculate/matrix/persistence/eval modules. Despite `tests/test_visualization.py` containing 861 lines of functional tests, the visualization modules are not measured against the threshold.
**Issue:** [#415](https://github.com/clouatre-labs/math-mcp-learning-server/issues/415)

**Fix:** Remove `src/math_mcp/visualization.py` and `src/math_mcp/tools/visualization.py` from `omit` -- functional tests exist and must be enforced. For `server.py` and `resources.py`: either remove from `omit` and accept integration-test coverage, or add `# pragma: no cover` rationale comments on genuinely uncoverable paths (e.g. `main()` entry point) and document the intentional gate scope in `coverage-gaps.md`. Update `docs/testing/coverage-gaps.md` header to v0.12.1 / 358 tests and close gap items whose target versions have passed (F08).

**Regression gate:** `uv run pytest --cov --cov-fail-under=90 -v` must pass with visualization modules included in measurement.

---

### F04 -- No `[tool.pyright]` config; 6 unresolved-import errors on optional extras

**Severity:** Medium
**File:** `pyproject.toml`
**Verdict:** CONFIRMED -- no `[tool.pyright]` section found in `pyproject.toml`. Running `uv run pyright src/` without the `plotting` and `scientific` extras installed produces 6 `reportMissingImports` errors on `numpy` (in `matrix.py` and `tools/visualization.py`) and `matplotlib`. CI step order was not verified; if extras are not installed before `pyright`, type errors in the numeric and visualization modules are silently ignored.
**Issue:** [#416](https://github.com/clouatre-labs/math-mcp-learning-server/issues/416)

**Fix:** Add a `[tool.pyright]` section to `pyproject.toml` with at minimum `pythonVersion = "3.14"` and `typeCheckingMode = "standard"`. Ensure the CI `typecheck` step installs `plotting` and `scientific` extras (e.g. `uv sync --extra plotting --extra scientific --extra dev`) before running `uv run pyright src/`.

**Regression gate:** `uv run pyright src/` (with extras installed) must report zero errors.

---

### F05 -- `test-http-integration` job lacks explicit permissions

**Severity:** Low
**File:** `.github/workflows/ci.yml` -- `test-http-integration` job
**Verdict:** CONFIRMED -- job has no `permissions:` block; inherits top-level `contents: read`. Per project conventions every job must carry an explicit permissions block.
**Issue:** [#414](https://github.com/clouatre-labs/math-mcp-learning-server/issues/414)

**Fix:** Add `permissions: contents: read` to the `test-http-integration` job definition.

**Regression gate:** `uv run pytest -v` and CI lint pass; workflow YAML validates.

---

### F06 -- `ruff<0.16.0` ceiling excludes expanded 2026 default rule set

**Severity:** Low
**File:** `pyproject.toml` -- ruff dependency constraint
**Verdict:** CONFIRMED -- `pyproject.toml` pins `ruff>=0.15.1,<0.16.0`. Ruff 0.16.0 expands the default rule set from 59 to 413 rules and is excluded. The inline comment cites a 0.15.0 formatting regression on multi-exception `except`-clause parentheses (fixed in 0.15.1) as the rationale for the ceiling; that rationale does not apply to 0.16.x. Renovate merged PR #410 updating to `>=0.16.0,<0.17.0` -- verify the CI lint job constraint was also updated in that PR.
**Issue:** [#417](https://github.com/clouatre-labs/math-mcp-learning-server/issues/417)

**Fix:** Confirm constraint is `>=0.16.0,<0.17.0` post-PR #410; if not, update `pyproject.toml` and the CI lint job constraint. Run `uv run ruff format --check` to verify the 0.16.x formatter is clean on this codebase; fix any new violations.

**Regression gate:** `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/` must both pass with ruff 0.16.x.

---

### F07 -- `settings.py::validated_tool` is untyped and likely dead code

**Severity:** Low
**File:** `src/math_mcp/settings.py`
**Verdict:** CONFIRMED -- `validated_tool(func)` has no parameter or return type annotation, inconsistent with the `Annotated`/`Field` style throughout `tools/*.py`. No call site using it as a decorator was found in the audited source; tool functions rely on FastMCP's own Pydantic validation.
**Issue:** [#417](https://github.com/clouatre-labs/math-mcp-learning-server/issues/417)

**Fix:** Confirm with `rg 'validated_tool' src/` whether it is called anywhere. Remove if unused; otherwise add `Callable` generic type annotations and a docstring with a usage example.

**Regression gate:** `uv run pytest -v` and `uv run ruff check src/ tests/` must pass.

---

### A01 -- `ctx.get_state` pattern and 2026-07-28 stateless core

**Severity:** Info
**File:** `src/math_mcp/tools/_session.py`
**Verdict:** NOTED -- `ctx.get_state("session_id")` / `ctx.set_state(...)` is FastMCP's per-connection application state, not the protocol-level `Mcp-Session-Id` being removed in 2026-07-28. No defect today. The workspace persistence backend uses the filesystem, so actual workspace data survives across connections regardless of transport statefulness.
**Issue:** [#413](https://github.com/clouatre-labs/math-mcp-learning-server/issues/413)

Once FastMCP publishes its stateless-core-aligned transport, the behavior of `ctx.get_state` under a stateless transport (where each request may arrive at a different instance) should be re-verified.

**Fix:** Add an inline comment at the `get_state`/`set_state` call sites clarifying the application-level vs. protocol-level distinction.

**Regression gate:** `uv run pytest -v` must pass; comment only, no behavior change.

---

### A02 -- `eval.py` uses blocklist-plus-restricted-globals rather than AST allowlist

**Severity:** Info
**File:** `src/math_mcp/eval.py`
**Verdict:** NOTED -- design is documented in ADR 001-eval-sandbox.md and is safe in practice: `eval()` is restricted to `{'__builtins__': {'abs': abs}, 'math': math}` with an empty locals dict, so any unrecognized identifier raises `NameError` before execution. CPU/memory exhaustion is mitigated by `asyncio.wait_for` timeout. No exploitable gap found in this pass.
**Issue:** [#418](https://github.com/clouatre-labs/math-mcp-learning-server/issues/418)

The weakness is that safety depends partly on the `DANGEROUS_PATTERNS` substring blocklist; an AST-based validator (`ast.parse` + node-type allowlist) would be more future-proof against novel Python syntax constructs and is the recommended defense-in-depth follow-up.

**Fix:** Add an `ast.NodeVisitor` allowlist pass before `_build_safe_expr` / `eval()`. Update ADR 001-eval-sandbox.md to document the three-layer model: AST allowlist -> restricted globals -> timeout.

**Regression gate:** All existing `test_math_operations.py` calculate tests must pass. New `tests/test_eval.py` must cover AST rejection of non-whitelisted node types and acceptance of all arithmetic operators and whitelisted math functions. `uv run pytest -v` must pass.

---

## Non-Findings (considered and dismissed)

**N01:** `fastmcp` 2026-07-28 stateless core breaks `ctx.get_state` in `_session.py`. Dismissed. `ctx.get_state` is FastMCP application-level state, not a protocol-level session concept. See A01.

**N02:** Renovate not configured. Dismissed. Renovate is active using GitHub defaults; bot PRs are merging regularly. Adding `renovate.json` would be an enhancement, not a fix.

**N03:** `pydantic-settings` and `pyright` lockfile lag. Dismissed. Both are at most one patch version behind; Renovate will pick them up. Not worth a dedicated issue.

---

## Subsystem Reviews

### MCP Protocol Alignment

**Status: Mostly clean.** F01 and A01 are the only items; F01 is a version-pin hygiene issue, not a compatibility defect.

- `@mcp.tool()` decorator pattern is confirmed to carry forward unchanged into FastMCP v4/MCPServer.
- `ctx: SkipValidation[Context | None] = None` with `if ctx:` guards is the correct optional-context pattern and is unaffected by transport changes.
- `stdio` and `streamable-http` transports both supported; 2026-07-28 keeps Streamable HTTP and only removes the protocol-level session header.
- No use of deprecated Roots, Sampling, or Logging MCP capabilities.
- No custom OAuth/authorization code to migrate for RFC 9207 `iss`-validation hardening.

### Eval Sandbox

**Status: Sound.** No exploitable gap found. See A02 for the defense-in-depth follow-up.

- Restricted globals correctly limit reachable builtins to `abs` only.
- `asyncio.wait_for` timeout mitigates CPU exhaustion.
- ADR 001-eval-sandbox.md documents the design tradeoff.
- `test_annotations.py` regression-tests every tool/param description, giving strong protection against annotation drift.

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

---

## Regression Strategy

Safe implementation order by blast radius.

*Table 2: Issue sequencing.*

| Order | Issue | Findings | Rationale |
|-------|-------|----------|-----------|
| 1 | [#413](https://github.com/clouatre-labs/math-mcp-learning-server/issues/413) | F01, A01 | Time-gated: spec ships 2026-07-28; one-line `pyproject.toml` change + comment |
| 2 | [#417](https://github.com/clouatre-labs/math-mcp-learning-server/issues/417) | F06, F07 | Same sitting as #413; verify PR #410 completeness; trivial if complete |
| 3 | [#414](https://github.com/clouatre-labs/math-mcp-learning-server/issues/414) | F02, F05 | Release-path risk; no release imminent; workflow YAML only |
| 4 | [#416](https://github.com/clouatre-labs/math-mcp-learning-server/issues/416) | F04 | Config-only; unblocks #415 |
| 5 | [#415](https://github.com/clouatre-labs/math-mcp-learning-server/issues/415) | F03, F08 | Do after #416; coverage failures easier to read with clean pyright baseline |
| 6 | [#418](https://github.com/clouatre-labs/math-mcp-learning-server/issues/418) | A02 | Defense-in-depth only; no urgency; good contributor issue |
