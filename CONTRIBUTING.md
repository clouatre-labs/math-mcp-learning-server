# Contributing to Math MCP Server

## Quick Start

### Prerequisites
- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Development Setup
```bash
# Clone the repository
git clone https://github.com/clouatre-labs/math-mcp-learning-server.git
cd math-mcp-learning-server

# Install dependencies and activate virtual environment
uv sync --extra dev --extra plotting
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

- **lint** - Ruff code quality and formatting checks
- **security** - gitleaks secret scanning and pip-audit CVE scanning
- **test** - pytest functionality validation on Python 3.14 with >=90% coverage
- **zizmor** - GitHub Actions workflow security scanning
- **commitlint** - Conventional commit message validation
- **reuse** - SPDX license header compliance

All checks must pass before merge. Jobs run in parallel for faster feedback.

HTTP integration tests run only on release tags (see [Maintainer Guide](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/MAINTAINER_GUIDE.md)).

See [CI/CD Workflow](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/workflows/ci.yml) for implementation details.

## Code Review

All pull requests require at least one approving review before merge. This is enforced by
branch protection on `main`.

Reviewer checklist:

- **Correctness**: logic is sound, edge cases handled, no regressions
- **Test coverage**: new behavior has a test; no untested code paths added
- **Security**: no use of `eval()` outside `src/math_mcp/eval.py`; all inputs validated
  with Pydantic; no secrets or credentials in code
- **Conventions**: conventional commits, GPG + DCO sign-off, `ruff` and `pyright` clean
- **Documentation**: public functions have docstrings; architectural changes have an ADR

## Code Standards

### Python Style
- Follow PEP 8 (enforced by ruff)
- Use type hints throughout
- Maximum line length: 100 characters
- Meaningful variable and function names

**Cyclomatic complexity threshold.** `ruff` enforces McCabe cyclomatic complexity (rule C901) at a threshold of 10 (set in `pyproject.toml`); violations are hard errors in CI. When a function legitimately exceeds the threshold and splitting it would reduce clarity rather than improve it, suppress with a `noqa` comment and a mandatory explanation:

```python
def complex_dispatch(event: Event) -> None:  # noqa: C901 -- <why this function cannot be meaningfully split>
    ...
```

Do not raise the global threshold to accommodate a single outlier. The explanation is required: it documents intent for reviewers and makes the suppression searchable.

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

Modular architecture with composition root and specialized modules:
```
src/math_mcp/
  server.py              # Composition root, middleware, lifespan
  tools/                 # Tool implementations
    calculate.py         # Basic math operations
    matrix.py            # Matrix operations
    persistence.py       # Workspace persistence
    visualization.py     # Chart and plot generation
  persistence/           # State management
    models.py            # Data models
    storage.py           # File-based storage
    workspace.py         # Workspace management
  resources.py           # MCP resources
  settings.py            # Configuration
  eval.py                # Restricted evaluation
  visualization.py       # Visualization helpers
  agent_card.py          # A2A agent card
tests/                   # Comprehensive test suite
ROADMAP.md               # Ideas for later consideration
```

### Adding New Features

**New Mathematical Operations:**
1. Add tool function using `@mcp.tool()` decorator
2. Include comprehensive docstring with examples
3. Add input validation and error handling
4. Include educational annotations
5. Add corresponding tests

**New Files:**
- All new source files require SPDX license headers for REUSE compliance (enforced by reuse.yml in CI)

**Educational Features:**
1. Ensure it serves mathematical learning
2. Keep implementation minimal
3. Add appropriate difficulty classification
4. Test educational metadata

## Commit Message Standards (CI-Enforced)

Commit messages are validated by commitlint in CI to ensure they follow [Conventional Commits](https://www.conventionalcommits.org/). All commits must follow the format outlined in the Commit Message Standards section above.

## Contribution Checklist

1. Check existing issues and PRs for similar work
2. Review ROADMAP.md for planned features
3. Discuss major changes in an issue first
4. Create feature branch from main
5. Implement changes following code standards
6. Add/update tests for your changes
7. Update documentation as needed
8. Run quality checks locally: `uv run pytest -v && uv run pyright src/ && uv run ruff check src/ tests/`
9. Commit with conventional messages (GPG-signed, DCO sign-off)
10. Push your branch and create PR with clear title, description, and testing summary
11. Delete remote branch if PR is closed without merging (merged PRs auto-delete)

## What We're Looking For

**[High Priority]** Additional mathematical domains (linear algebra, calculus); Educational enhancements (better error explanations); Performance improvements; Security hardening

**[Medium Priority]** Documentation improvements; Example applications; Integration guides; Educational use cases

**[Avoid]** Feature bloat that doesn't serve education; Complex architectural changes without discussion; Breaking changes without clear benefits; Dependencies that compromise the minimal philosophy

## Getting Help

- **Bug Reports**: Open an issue with detailed reproduction steps
- **Feature Requests**: Check ROADMAP.md first, then open an issue
- **Questions**: Open a discussion or issue
- **Security Issues**: Report privately to maintainers

## Demo GIF

The README demo is generated with [VHS](https://github.com/charmbracelet/vhs). To regenerate after editing `assets/demo.tape` or `assets/math_demo.py`:

```bash
vhs assets/demo.tape
```

Commit `demo.tape`, `math_demo.py`, and the updated `demo.gif` together.

## Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://gofastmcp.com)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to hugues+mcp-coc@linux.com.
