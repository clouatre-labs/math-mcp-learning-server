# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.8.x   | :white_check_mark: |
| < 0.8   | :x:                |

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
- Patch versions for non-breaking security fixes (0.8.x)
- Minor versions if breaking changes are necessary (0.9.0)

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
