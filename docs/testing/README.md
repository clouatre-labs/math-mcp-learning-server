# Testing Guide

Quick reference for running tests and understanding the test suite for math-mcp-learning-server.

## Quick Start

### Run All Tests
```bash
# Basic test run
uv run pytest tests/ -v

# With coverage report
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific test file
uv run pytest tests/test_math_operations.py -v

# Run specific test category
uv run pytest tests/ -k "matrix" -v
```

### Run Code Quality Checks
```bash
# Linting
uv run ruff check

# Formatting check
uv run ruff format --check

# Security checks
uv run ruff check --select S
```

## Test Suite Overview

**Total Tests:** 126
**Success Rate:** 100% (v0.10.0)
**Execution Time:** ~35 seconds

### Test Categories

| Category | Tests | Coverage |
|----------|-------|----------|
| HTTP Integration | 18 | MCP server protocol, tool/resource discovery |
| Math Operations | 34 | calculate, statistics, units, financial |
| Matrix Operations | 21 | multiply, transpose, determinant, inverse, eigenvalues |
| Persistence | 22 | save_calculation, load_variable, workspace |
| Visualization | 31 | plotting functions, charts, histograms |

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── test_http_integration.py       # MCP protocol tests
├── test_math_operations.py        # Basic math tools
├── test_matrix_operations.py      # Matrix operations (v0.10.0)
├── test_persistence.py            # Workspace & storage
└── test_visualization.py          # Plotting tools
```

## Common Test Commands

### Run Specific Category
```bash
# HTTP/MCP protocol tests
uv run pytest tests/test_http_integration.py -v

# Matrix operations only
uv run pytest tests/test_matrix_operations.py -v

# Visualization tests
uv run pytest tests/test_visualization.py -v
```

### Debug Failed Tests
```bash
# Stop on first failure
uv run pytest tests/ -x

# Show print statements
uv run pytest tests/ -v -s

# Run last failed tests
uv run pytest tests/ --lf
```

### Performance Testing
```bash
# Show slowest tests
uv run pytest tests/ --durations=10

# Benchmark mode (if pytest-benchmark installed)
uv run pytest tests/ --benchmark-only
```

## CI/CD Integration

Tests run automatically on:
- Every push to main branch
- Pull request creation/updates
- Pre-release validation

GitHub Actions workflow: `.github/workflows/test.yml`

## More Information

- **[Test Plan](test-plan.md)** - Testing strategy & architecture
- **[Coverage Gaps](coverage-gaps.md)** - Known gaps & improvement roadmap
- **[Validation Reports](reports/)** - Comprehensive QA reports per version

## Security Testing

The test suite validates:
- ✅ DoS prevention (expression length limits, array size limits, matrix size limits)
- ✅ Input validation (type checking, range validation)
- ✅ Injection protection (no eval/exec/import in calculate tool)
- ✅ Rate limiting implementation

## Getting Help

- **Issue with tests?** Check [coverage-gaps.md](coverage-gaps.md) for known issues
- **Adding new tests?** See [test-plan.md](test-plan.md) for architecture guidance
- **Contributing?** See main [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines
