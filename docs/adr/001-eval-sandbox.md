# ADR-001: Restricted eval() Sandbox

## Status
Accepted

## Context
Mathematical expression evaluation requires executing user-provided code. Without proper sandboxing, this creates a critical security vulnerability. The project needed a lightweight, educational approach to safely evaluate arithmetic and trigonometric expressions without introducing heavy dependencies or complex parsing infrastructure.

## Decision
Implement a restricted `eval()` sandbox using character whitelisting, function whitelisting, and restricted globals. The approach is documented in `src/math_mcp/settings.py` (lines 64-66) and `src/math_mcp/eval.py` (lines 40-87).

**Whitelist constants** (settings.py):
```python
MATH_FUNCTIONS_ALL = {"sin", "cos", "tan", "log", "sqrt", "abs", "pow", "exp"}
DANGEROUS_PATTERNS = ["import", "exec", "__", "eval", "open", "file"]
```

**Restricted globals** (eval.py, line 73):
```python
allowed_globals = {"__builtins__": {"abs": abs}, "math": math}
```

**Allowed characters** (eval.py, line 49):
```python
allowed_chars = set("0123456789+-*/.(),e")
```

Timeout enforcement via `asyncio.wait_for()` with `EXPRESSION_TIMEOUT_SECONDS` (default 5.0s) prevents denial-of-service attacks.

## Consequences

**Gained:**
- No arbitrary code execution; only math module + abs available
- Character-level validation catches most injection attempts
- Timeout prevents infinite loops or expensive computations
- Educational clarity: whitelist approach is easy to audit and understand

**Limited:**
- No symbolic math (SymPy integration would require separate design)
- No user-defined functions or variables in expressions
- No complex numbers or advanced mathematical operations
- Scope limited to arithmetic, trigonometry, logarithms, and exponents

This is intentional: the project targets educational use cases where simplicity and security outweigh advanced features.
