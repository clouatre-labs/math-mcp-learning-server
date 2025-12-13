# Test Plan & Strategy

Comprehensive testing strategy for math-mcp-learning-server.

## Testing Philosophy

**Goals:**
1. Educational MCP server with production-quality testing
2. Comprehensive coverage across all tool categories
3. Strong security posture (DoS prevention, input validation)
4. Maintainable test suite that scales with features

**Principles:**
- Every tool has explicit tests for success and failure cases
- Security-critical features have dedicated test coverage
- Tests serve as executable documentation
- Fast feedback loop (<1 minute for full suite)

---

## Test Architecture

### Test Organization

Tests are organized by **feature category**, not by file structure:

```
tests/
├── conftest.py                    # Shared fixtures (client, temp dirs)
├── test_http_integration.py       # MCP protocol compliance
├── test_math_operations.py        # Basic math tools
├── test_matrix_operations.py      # Linear algebra tools
├── test_persistence.py            # Workspace & storage
└── test_visualization.py          # Plotting & charts
```

### Test Naming Convention

```python
# Format: test_<feature>_<scenario>_<expected_result>
async def test_calculate_complex_expression_success()
async def test_statistics_empty_array_raises_error()
async def test_matrix_multiply_incompatible_dimensions_fails()
```

---

## Testing Levels

### 1. Unit Tests (Implicit)
Individual tool functionality tested in isolation.

**Example:** `test_calculate_basic_arithmetic()`

### 2. Integration Tests
MCP server protocol compliance and tool interaction.

**Example:** `test_http_integration.py` validates MCP server startup, tool discovery, resource enumeration.

### 3. Security Tests
DoS prevention, input validation, injection protection.

**Examples:**
- Expression length limits (500 chars)
- Array size limits (10,000 elements)
- Matrix size limits (100x100)
- No eval/exec/import in calculate tool

### 4. End-to-End Workflows (Future - v0.11.0)
Complete user workflows spanning multiple tools.

**Planned:** calculate → save → load → visualize

---

## Test Coverage Strategy

### Current Coverage (v0.10.0)

| Feature Category | Test Count | Coverage Areas |
|------------------|-----------|----------------|
| **HTTP Integration** | 18 | Server startup, tool discovery, resource enumeration, prompts |
| **Math Operations** | 34 | calculate, statistics, compound_interest, convert_units |
| **Matrix Operations** | 21 | multiply, transpose, determinant, inverse, eigenvalues |
| **Persistence** | 22 | save_calculation, load_variable, workspace management |
| **Visualization** | 31 | plot_function, histograms, line/scatter charts, box plots |

### Coverage Targets

- **Code coverage:** >90% (run `pytest --cov=src --cov-report=html`)
- **Tool coverage:** 100% (all 17 tools tested)
- **MCP protocol:** Resources and prompts (gap in v0.10.0)
- **Security:** All input validation paths tested

---

## Security Testing

### DoS Prevention Tests

```python
# Expression length limits
async def test_calculate_expression_too_long():
    expression = "1+" * 300  # >500 chars
    # Expect: ValidationError

# Array size limits
async def test_statistics_array_too_large():
    data = list(range(20000))  # >10,000 elements
    # Expect: ValidationError

# Matrix size limits
async def test_matrix_multiply_too_large():
    matrix = [[1.0] * 150 for _ in range(150)]  # >100x100
    # Expect: ValidationError
```

### Input Validation Tests

```python
# Type checking
async def test_compound_interest_negative_principal():
    # Expect: ValidationError

# Security filtering
async def test_calculate_blocked_keywords():
    expressions = ["import os", "__import__", "exec()", "eval()"]
    # Expect: ValidationError for all
```

---

## Test Data Management

### Fixtures (conftest.py)

```python
@pytest.fixture
async def client():
    """MCP client for HTTP integration tests"""

@pytest.fixture
def temp_workspace(tmp_path):
    """Temporary workspace directory"""
```

### Test Data Patterns

- **Small datasets:** Inline in test functions
- **Complex datasets:** Generate programmatically
- **Visual outputs:** Validate Base64 PNG signature only
- **Error cases:** Test boundary conditions

---

## Performance Testing

### Current Benchmarks (v0.10.0)

- Full test suite: ~35 seconds
- Average test: ~0.28 seconds
- Slowest category: Visualization (plot generation)

### Future Performance Tests (v0.11.0)

```python
# Benchmark matrix operations at scale
async def test_benchmark_matrix_multiply_100x100():
    start = time.perf_counter()
    # ... operation
    duration = time.perf_counter() - start
    assert duration < 5.0  # Should complete within 5s
```

---

## MCP Protocol Testing

### Current Coverage

✅ **Server Initialization:** Startup, health check
✅ **Tool Discovery:** List all 17 tools
✅ **Tool Execution:** All tools tested individually

### Gaps (To address in v0.11.0)

⚠️ **MCP Resources:** 5 resources not explicitly tested
- `math://test`
- `math://constants/pi`
- `math://constants/e`
- `math://functions`
- `math://workspace`

⚠️ **MCP Prompts:** 2 prompts not explicitly tested
- `math_tutor` (with various topics/levels)
- `formula_explainer` (with different formulas)

---

## Test Maintenance

### When to Update Tests

1. **New tool added:** Add test file or expand existing category
2. **Tool behavior changed:** Update corresponding tests
3. **Security issue found:** Add regression test
4. **Bug fixed:** Add test to prevent regression

### Test Review Checklist

- [ ] Test names are descriptive
- [ ] Success and failure cases both covered
- [ ] Edge cases identified and tested
- [ ] No hardcoded paths or credentials
- [ ] Tests are independent (no shared state)
- [ ] Fast execution (<5s per test)

---

## Continuous Integration

### GitHub Actions Workflow

Tests run on:
- Push to main branch
- Pull request creation/updates
- Scheduled nightly builds

**Test matrix:**
- Python versions: 3.11, 3.14
- Operating systems: Ubuntu 24.04

---

## Future Enhancements

See [coverage-gaps.md](coverage-gaps.md) for detailed roadmap.

### v0.11.0 Focus
- Complete MCP protocol test coverage
- Integration workflow tests
- Performance benchmarks

### v0.12.0 Focus
- Load testing (concurrent users)
- Memory profiling (large datasets)
- Fuzzing tests (random inputs)

---

## References

- **pytest Documentation:** https://docs.pytest.org/
- **MCP Protocol Spec:** https://modelcontextprotocol.io/
- **Test Reports:** [reports/](reports/)
