# Security Assurance Case

This document provides the security assurance case for math-mcp-learning-server.

## What the project does

math-mcp-learning-server is a Python FastMCP server that exposes 17 MCP tools for math operations, matrix operations, visualization, and persistent workspaces. It uses a restricted `eval()` with a character and function allowlist (math module + `abs` only). All tool inputs are validated with Pydantic before processing. The server runs on FastMCP Cloud (Lambda) and is distributed as a Python package on PyPI.

## Trust boundaries

| Boundary | Direction | Description |
|----------|-----------|-------------|
| PyPI (HTTPS) | Inbound | Package downloaded from `pypi.org` via HTTPS; SLSA provenance attestation generated for every release |
| FastMCP Cloud (Lambda, HTTPS) | Outbound | Server deployed to FastMCP Cloud over HTTPS; no plain-HTTP fallback |
| uv (package manager) | Inbound | Dependencies resolved from `uv.lock`; all pinned and monitored by Renovate + pip-audit |
| Caller (MCP client) | Inbound | MCP client sends tool inputs; all inputs validated with Pydantic before processing |

The server makes no outbound calls beyond FastMCP Cloud infrastructure. It holds no credentials and writes no persistent state outside the designated workspace directory.

## Attack surface

The primary attack surfaces are:

1. **eval() injection**: The `calculate` tool accepts math expressions evaluated with `eval()`. This is mitigated by a three-layer defense-in-depth model (see [ADR-001](docs/adr/001-eval-sandbox.md)): character/pattern blocklist, restricted globals (`math` + `abs` only), and an AST NodeVisitor allowlist (`_ASTValidator`) that rejects non-whitelisted AST node types before evaluation.

2. **Workspace path traversal**: The `persistence` tools write and read files in a workspace directory. This is mitigated by path restriction in `storage.py`, which rejects any path that escapes the workspace root.

3. **Dependency confusion**: Third-party Python packages could introduce malicious code. This is mitigated by `pip-audit` CVE scanning on every CI run and Renovate weekly dependency update PRs.

4. **Prompt injection from user-provided math expressions**: An MCP client could pass adversarial expressions via tool inputs. This is a documented residual risk; the `eval()` allowlist is the primary mitigation -- no arbitrary code execution is possible within the sandbox.

## Common weaknesses countered

| Weakness | Status |
|----------|--------|
| Injection (eval) | Mitigated -- three-layer defense (character blocklist, restricted globals, AST NodeVisitor allowlist); no arbitrary code execution |
| Path traversal | Mitigated -- workspace path restriction in storage.py rejects escaping paths |
| Supply chain | Mitigated -- SLSA provenance attestation, pip-audit CVE scanning, SHA-pinned Actions, Renovate |
| Secret leakage | Mitigated -- gitleaks secret scanning runs on every PR as a required CI check |
| Dependency confusion | Mitigated -- pip-audit scans all transitive dependencies on every CI run |

## Supply chain hardening

- All GitHub Actions used by CI and release workflows are pinned to SHA digests (enforced by zizmor)
- Renovate bot creates weekly PRs for Python dependency updates and GitHub Actions digest updates
- Release artifacts are published to PyPI via HTTPS using Trusted Publishing (OIDC)
- SLSA provenance attestation is generated for every release (`attest-build-provenance`)
- pip-audit scans dependencies for known CVEs on every CI run

## CI enforcement

| Tool | Purpose | Enforcement |
|------|---------|-------------|
| gitleaks | Secret scanning | Required CI check |
| zizmor | Workflow security (template injection, dangerous permissions, unpinned actions) | Required CI check |
| pip-audit | CVE scanning of Python dependencies | Required CI check |
| ruff | Python code quality and linting | Required CI check |
| pyright | Static type checking | Required CI check |

## Security review

- **Review date:** March 2026
- **Scope:** Full codebase including eval.py, storage.py, all tool inputs, CI workflow, trust boundaries, and attack surface (as documented in this file and SECURITY.md)
- **Conclusion:** No critical findings; residual prompt-injection risk is documented above with eval allowlist as the primary mitigation
- **Reviewer:** Project maintainer (self-review; acceptable for solo projects under OpenSSF criteria)
