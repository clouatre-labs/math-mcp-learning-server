# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported |
| ------- | --------- |
| 0.11.x  | Yes       |
| 0.10.x  | No        |
| < 0.10  | No        |

## Verifying release signatures

### GPG-signed tags

Every release tag is GPG-signed by the maintainer. To verify a tag:

```bash
git fetch --tags
git tag --verify v<version>
```

The signing key is visible on the maintainer's GitHub profile and in the
signed commits in this repository.

### SLSA provenance attestation

Release artifacts on PyPI are attested using GitHub's native attestation
store (SLSA provenance level 3). To verify a downloaded wheel:

```bash
gh attestation verify dist/math_mcp_learning_server-<version>-py3-none-any.whl \
  --repo clouatre-labs/math-mcp-learning-server
```

Replace `<version>` with the release version (e.g. `0.11.5`).

## Reporting a Vulnerability

We take the security of math-mcp-learning-server seriously. If you discover a security vulnerability, please follow these steps:

### 1. **Do Not** Open a Public Issue

Please do not report security vulnerabilities through public GitHub issues.

### 2. Email Us Directly

Send details to: **hugues+mcp-security@linux.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Fix Timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next regular release

### 4. Disclosure Policy

- We will acknowledge receipt of your vulnerability report
- We will provide regular updates on our progress
- We will notify you when the vulnerability is fixed
- We will publicly disclose the vulnerability after a fix is released
- We will credit you for the discovery (unless you prefer to remain anonymous)

## Security Best Practices

This project implements several security measures:

### Safe Expression Evaluation
- Restricted `eval()` with whitelisted functions only
- No access to dangerous built-ins or imports
- Security logging for suspicious attempts
- Controlled execution environment

### Input Validation
- All tool inputs validated with Pydantic models
- Type checking enforced
- Structured error handling without exposing sensitive information

### File Operations
- Workspace operations restricted to designated directory
- Cross-platform path handling
- Atomic file operations with proper locking

### Dependencies
- Regular dependency updates via Dependabot
- Minimal dependency footprint (core uses stdlib only)
- Security scanning in CI/CD pipeline

## Security Review

A security review of this project was conducted in March 2026.

**Scope:**
- `src/math_mcp/eval.py`: restricted `eval()` implementation -- character whitelist,
  dangerous-pattern blocklist, globals locked to `{abs, math}` only
- Input validation: Pydantic `validate_call` on all tool inputs
- Workspace path restriction in `src/math_mcp/persistence/`

**Findings:** No critical issues identified.

**Next review:** Within 12 months or upon any change to `eval.py` or the input
validation layer.

## Scope

### In Scope
- Server code vulnerabilities
- Expression evaluation bypass
- File system access violations
- Dependency vulnerabilities
- Authentication/authorization issues (if applicable)

### Out of Scope
- Issues in third-party MCP clients
- User configuration errors
- Network security (users are responsible for their deployment)
- Denial of Service attacks against public cloud deployment

## Security Updates

Security updates will be released as:
- Patch versions for non-breaking security fixes (0.11.x)
- Minor versions if breaking changes are necessary (0.12.0)

Subscribe to releases on GitHub to receive security notifications.

## Educational Note

This project is designed for educational purposes and demonstrates security best practices:
- Safe expression evaluation patterns
- Input validation with Pydantic
- Secure file operations
- Security logging and monitoring

Students and learners should study the security implementations as examples of defensive programming.

## Contact

For security concerns: hugues+mcp-security@linux.com
For general questions: Open a GitHub issue or discussion
