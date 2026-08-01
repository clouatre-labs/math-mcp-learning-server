# ADR-001: Restricted eval() Sandbox

## Status
Accepted (Amended by ADR-001-A)

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

## Amendment: ADR-001-A

### Status
Amended

### Context
The original two-layer sandbox (character whitelisting + restricted globals) allowed several AST-level attacks that bypass character-level checks. For example, `math.__class__` passes the character whitelist and the regex pattern check but accesses Python internals via attribute access on the math module object.

### Decision
Add a third defense layer: AST-based expression validation. A dedicated `_ASTValidator` (ast.NodeVisitor subclass) walks the parsed AST before evaluation and rejects any node type outside an explicit allowlist. The three-layer model is now:

1. **Layer 1 (AST allowlist):** `_ASTValidator` rejects non-whitelisted AST node types (Attribute, Subscript, Compare, BoolOp, IfExp, Lambda, collection literals, NamedExpr, JoinedStr, MatMult, Invert, Not, non-whitelisted Name identifiers, non-whitelisted Call callees, non-numeric constants). Runs after syntax and security checks to preserve error message contracts.

2. **Layer 2 (Character whitelist + regex):** `_check_expression_security` rejects dangerous patterns (`import`, `exec`, `__`, `eval`, `open`, `file`) and invalid characters via the `allowed_chars` set.

3. **Layer 3 (Restricted globals + timeout):** `_eval_in_restricted_scope` limits `eval()` to `math` module + `abs` only. `evaluate_with_timeout` enforces a 5-second execution timeout via `asyncio.wait_for`.

### Consequences
**Gained:**
- AST-level protection against Attribute-based bypasses, Subscript access, and all AST-level injection techniques
- Defense-in-depth: each layer catches what the previous layer misses
- No new dependencies (ast is stdlib)
- Educational clarity: three independently auditable layers

**Preserved:**
- All existing error message contracts (SyntaxError before AST validation, `forbidden` on character checks, `Mathematical error` on evaluation errors)
- All existing tests pass without modification
- Timeout enforcement remains unchanged
