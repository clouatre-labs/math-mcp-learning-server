# Contributing to Math MCP Server

Thank you for your interest in contributing to the Math MCP Server! This guide will help you get started.

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Development Setup
```bash
# Clone the repository
git clone https://github.com/clouatre-labs/math-mcp-learning-server.git
cd math-mcp-learning-server

# Install dependencies and activate virtual environment
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Verify installation
uv run pytest -v
```

### Run the Server
```bash
# Start the MCP server
uv run python -m math_mcp.server
```

## Development Workflow

### Feature Branch Process

Always use a feature branch for your changes:

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes, test, and commit
# ...

# Push and create Pull Request
git push -u origin feature/your-feature-name
```

### Commit Message Standards

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]
[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

**Examples:**
```
feat: add matrix multiplication operations
fix: resolve division by zero error handling
docs: update installation instructions
```

## Local Testing

Before submitting a PR, run these checks locally:

```bash
# Run all tests
uv run pytest -v

# Type checking
uv run pyright src/

# Linting and formatting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# All checks at once
uv run pytest -v && uv run pyright src/ && uv run ruff check src/ tests/
```

**Required standards:**
- All tests pass (100% pass rate)
- Type checking passes with no errors
- Linting passes with no warnings
- New features include comprehensive tests

## CI/CD Workflow

All pull requests run automated checks in parallel:

- **Linting** (ruff) - Code quality and formatting
- **Type checking** (pyright) - Type safety
- **Tests** (pytest) - Functionality validation across Python 3.11 and 3.13

All checks must pass before merge. Jobs run in parallel for faster feedback.

HTTP integration tests run only on release tags (see [Maintainer Guide](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/MAINTAINER_GUIDE.md)).

See [CI/CD Workflow](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/workflows/ci.yml) for implementation details.

## Code Standards

### Python Style
- Follow PEP 8 (enforced by ruff)
- Use type hints throughout
- Maximum line length: 88 characters
- Meaningful variable and function names

### Documentation
- All functions must have docstrings with examples
- Include parameter descriptions and return types
- Update README.md for user-facing changes

### Security
- Never use `eval()` without proper sandboxing
- Validate all user input
- Log security-relevant events

### MCP Standards
- Use FastMCP framework patterns
- Implement proper error handling
- Include educational annotations where appropriate

## Code Organization

Single-file architecture for core functionality:
```
src/math_mcp/server.py    # Core MCP server
tests/                    # Comprehensive test suite
FUTURE_IMPROVEMENTS.md    # Ideas for later consideration
```

### Adding New Features

**New Mathematical Operations:**
1. Add tool function using `@mcp.tool()` decorator
2. Include comprehensive docstring with examples
3. Add input validation and error handling
4. Include educational annotations
5. Add corresponding tests

**Educational Features:**
1. Ensure it serves mathematical learning
2. Keep implementation minimal
3. Add appropriate difficulty classification
4. Test educational metadata

## Contribution Process

### Before You Start
1. Check existing issues and PRs for similar work
2. Review FUTURE_IMPROVEMENTS.md for planned features
3. Discuss major changes in an issue first

### Making Changes
1. Fork the repository (for external contributors)
2. Create feature branch from main
3. Implement changes following code standards
4. Add/update tests for your changes
5. Update documentation as needed
6. Run quality checks locally
7. Commit with conventional messages

### Submitting Changes
1. Push your branch
2. Create Pull Request with:
   - Clear title and description
   - Reference any related issues
   - Summary of testing performed
   - Note any breaking changes

### PR Review
- Automated checks must pass
- Code review by maintainers
- Discussion of any concerns
- Approval and merge

## What We're Looking For

### High Priority Contributions
- Additional mathematical domains (linear algebra, calculus)
- Educational enhancements (better error explanations)
- Performance improvements
- Security hardening
- Test coverage improvements

### Medium Priority
- Documentation improvements
- Example applications
- Integration guides
- Educational use cases

### Please Avoid
- Feature bloat that doesn't serve education
- Complex architectural changes without discussion
- Breaking changes without clear benefits
- Dependencies that compromise the minimal philosophy

## Getting Help

- **Bug Reports**: Open an issue with detailed reproduction steps
- **Feature Requests**: Check FUTURE_IMPROVEMENTS.md first, then open an issue
- **Questions**: Open a discussion or issue
- **Security Issues**: Report privately to maintainers

## Resources

### MCP Documentation
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)

### Development Tools
- [uv Package Manager](https://docs.astral.sh/uv/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [Pyright Type Checker](https://github.com/microsoft/pyright)

### Mathematical References
- [Python Math Module](https://docs.python.org/3/library/math.html)
- [Python Statistics Module](https://docs.python.org/3/library/statistics.html)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to hugues+mcp-coc@linux.com.

---

For questions about this guide, please open an issue or start a discussion.
