# Test Coverage Gaps & Roadmap

Known testing gaps and planned improvements for math-mcp-learning-server.

**Last Updated:** 2026-07-27
**Current Version:** v0.12.2
**Test Success Rate:** 201/201 (100%)

---

## Coverage Gate Scope

The 90% coverage gate (`fail_under = 90` in `[tool.coverage.report]`) applies to
the following modules:

- `calculate` tools
- `matrix` tools
- `persistence` (models, storage, workspace)
- `eval.py`
- `visualization.py` and `tools/visualization.py`

`visualization.py` and `tools/visualization.py` were previously excluded from
the `[tool.coverage.run]` omit list; they are now included in measurement.
Measured coverage with visualization included is approximately 91.76%,
above the 90% gate.

`server.py` and `resources.py` remain intentionally omitted from coverage
measurement because:

- `server.py`'s `main()` entrypoint and lifespan startup paths are not
  exercisable in unit tests (the server deploys to FastMCP Cloud/Lambda,
  where these paths run only under the managed runtime).
- `resources.py` contains large MCP runtime handler blocks that are only
  reachable via the MCP protocol runtime and cannot be invoked directly
  in unit tests.

## Overview

While v0.10.0 has excellent core functionality coverage (126 tests), several areas need enhancement to achieve comprehensive production-grade testing.

**Priority Levels:**
- 🔴 **P1 (v0.11.0):** Must-have for next release
- 🟡 **P2 (v0.12.0):** Should-have for production hardening
- 🟢 **P3 (Future):** Nice-to-have for advanced scenarios

---

## Priority 1: MCP Protocol Coverage (v0.11.0)

### Gap 1.1: MCP Resources Not Explicitly Tested

**Status:** ✅ Completed (PR #283)
**Impact:** Medium
**Affected Resources:** 5 out of 5

**Missing Tests:**
```python
# docs/testing/reports/v0.10.0-validation.md identified these gaps


async def test_mcp_resource_math_test():
    """Verify math://test resource"""
    response = await client.get_resource("math://test")
    assert response.content == "MCP Math Server is working!"


async def test_mcp_resource_constants_pi():
    """Verify math://constants/pi resource"""
    response = await client.get_resource("math://constants/pi")
    assert "3.14159" in response.content


async def test_mcp_resource_constants_e():
    """Verify math://constants/e resource"""
    response = await client.get_resource("math://constants/e")
    assert "2.71828" in response.content


async def test_mcp_resource_functions():
    """Verify math://functions resource"""
    response = await client.get_resource("math://functions")
    assert "Available Functions" in response.content


async def test_mcp_resource_workspace():
    """Verify math://workspace resource"""
    response = await client.get_resource("math://workspace")
    assert "Workspace:" in response.content
```

**File to Update:** `tests/test_http_integration.py`
**Estimated Effort:** 2-3 hours

---

### Gap 1.2: MCP Prompts Not Explicitly Tested

**Status:** ✅ Completed (PR #286)
**Impact:** Medium
**Affected Prompts:** 2 out of 2

**Missing Tests:**
```python
async def test_mcp_prompt_math_tutor_all_combinations():
    """Verify math_tutor prompt with various topics/levels"""
    topics = ["algebra", "calculus", "statistics", "geometry"]
    levels = ["beginner", "intermediate", "advanced"]

    for topic in topics:
        for level in levels:
            prompt = await client.get_prompt("math_tutor", topic=topic, level=level)
            assert topic in prompt.messages[0].content.lower()
            assert level in prompt.messages[0].content.lower()


async def test_mcp_prompt_formula_explainer():
    """Verify formula_explainer prompt"""
    formulas = ["quadratic formula", "pythagorean theorem", "compound interest", "law of cosines"]

    for formula in formulas:
        prompt = await client.get_prompt("formula_explainer", formula=formula)
        assert formula in prompt.messages[0].content.lower()
```

**File to Update:** `tests/test_http_integration.py`
**Estimated Effort:** 1-2 hours

---

## Priority 2: Integration & Performance Testing (v0.12.0)

### Gap 2.1: End-to-End Workflow Tests

**Status:** ✅ Resolved
**Impact:** High
**Complexity:** Medium

**Needed Workflows:**
```python
# Create new file: tests/test_integration_workflows.py


async def test_workflow_calculate_save_load_visualize():
    """Test complete workflow: calculate → save → load → visualize"""
    # 1. Calculate
    result = await client.call_tool("calc_expression", expression="[x**2 for x in range(1, 11)]")

    # 2. Save
    await client.call_tool("workspace_save", name="squares", value=result)

    # 3. Load
    loaded = await client.call_tool("workspace_load", name="squares")
    assert loaded == result

    # 4. Visualize
    plot = await client.call_tool("plot_histogram", data=loaded)
    assert plot.startswith("iVBORw0KGgo")


async def test_workflow_matrix_operations_chain():
    """Test matrix workflow: create → multiply → transpose → determinant"""
    # Chain of matrix operations
    pass


async def test_workflow_statistical_analysis():
    """Test stats workflow: calculate → statistics → visualize"""
    pass
```

**File to Create:** `tests/test_integration_workflows.py`
**Estimated Effort:** 4-6 hours

---

### Gap 2.2: Performance Benchmarks

**Status:** ✅ Resolved
**Impact:** Medium
**Complexity:** Low

**Needed Benchmarks:**
```python
# Create new file: tests/test_performance.py

import time


async def test_benchmark_matrix_multiply_scaling():
    """Benchmark matrix multiplication at various sizes"""
    sizes = [10, 50, 100]  # 100x100 is max

    for size in sizes:
        matrix = [[1.0] * size for _ in range(size)]
        start = time.perf_counter()

        result = await client.call_tool("matrix_multiply", matrix_a=matrix, matrix_b=matrix)

        duration = time.perf_counter() - start
        assert duration < 5.0  # Should complete within 5s
        print(f"{size}x{size}: {duration:.3f}s")


async def test_benchmark_visualization_generation():
    """Benchmark plot generation time"""
    # Test various plot types and data sizes
    pass


async def test_rate_limit_behavior():
    """Verify rate limiting under sustained load"""
    results = []
    for _ in range(100):
        result = await client.call_tool("calc_expression", expression="2+2")
        results.append(result)

    assert len(results) > 0  # Should not crash
```

**File to Create:** `tests/test_performance.py`
**Estimated Effort:** 3-4 hours

---

## Priority 3: Advanced Testing (Future)

### Gap 3.1: Documentation Validation

**Status:** 🟢 Nice-to-have
**Impact:** Low
**Complexity:** Medium

**Concept:**
```python
# Create new file: tests/test_documentation.py


async def test_readme_examples_work():
    """Validate all code examples in README.md execute successfully"""
    # Parse README.md
    # Extract code blocks
    # Execute each example
    # Verify expected output
    pass


async def test_examples_file_accuracy():
    """Verify EXAMPLES.md matches actual tool behavior"""
    # Parse EXAMPLES.md
    # Run each example
    # Compare output to documented behavior
    pass
```

**Estimated Effort:** 6-8 hours

---

### Gap 3.2: Load Testing

**Status:** 🟢 Nice-to-have
**Impact:** Low (educational server)
**Complexity:** High

**Concept:**
```python
# Concurrent user simulation
async def test_concurrent_users_100():
    """Simulate 100 concurrent users"""
    # Use asyncio.gather() to run 100 parallel requests
    # Verify no crashes or data corruption
    pass
```

**Estimated Effort:** 8-10 hours

---

### Gap 3.3: Fuzzing Tests

**Status:** 🟢 Nice-to-have
**Impact:** Low
**Complexity:** High

**Concept:**
```python
# Random input generation to find edge cases
async def test_fuzz_calculate_random_expressions():
    """Generate random valid expressions and test"""
    # Use hypothesis library for property-based testing
    pass
```

**Estimated Effort:** 10-12 hours

---

## Summary Roadmap

### v0.11.0 (Completed in v0.11.x)
- [x] Core functionality (126 tests) ✅ **DONE in v0.10.0**
- [x] MCP Resources (5 resources) ✅ **Completed PR #283**
- [x] MCP Prompts (2 prompts) ✅ **Completed PR #286**
- [x] Code coverage >90% ✅ **Enforced in CI (PR #303)**

### v0.12.0 (Resolved)
- [x] Integration workflows (3-5 tests) ✅ **Resolved**
- [x] Performance benchmarks (5-7 tests) ✅ **Resolved**
- **Estimated Total:** 7-10 hours

### v0.13.0+ (Future)
- [ ] Documentation validation 🟢 **P3**
- [ ] Load testing 🟢 **P3**
- [ ] Fuzzing tests 🟢 **P3**
- **Estimated Total:** 24-30 hours

---

## How to Contribute

1. **Pick a gap** from Priority 1 or 2
2. **Create tests** following patterns in existing test files
3. **Run tests** locally: `uv run pytest tests/ -v`
4. **Update this file** when gap is closed
5. **Submit PR** with tests and updated coverage report

---

## Questions?

- **See test patterns:** [test-plan.md](test-plan.md)
- **Check existing tests:** Browse `tests/` directory
- **Ask maintainer:** Open GitHub issue with "Testing" label
