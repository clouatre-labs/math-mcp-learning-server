"""Expression evaluation and validation utilities."""

import asyncio
import atexit
import logging
import math
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool

from math_mcp.settings import (
    DANGEROUS_PATTERNS,
    EXPRESSION_TIMEOUT_SECONDS,
    MATH_FUNCTIONS_ALL,
    MATH_FUNCTIONS_SINGLE,
    TEMP_CONVERSIONS,
    TOPIC_KEYWORDS,
)

_executor: ProcessPoolExecutor = ProcessPoolExecutor(max_workers=1)
# Register graceful shutdown on interpreter exit; wait=False prevents blocking
# the interpreter if in-flight evaluations are still running
atexit.register(_executor.shutdown, wait=False)


def _validate_expression_syntax(expression: str) -> None:
    """Provide specific error messages for common syntax errors."""
    clean_expr = expression.replace(" ", "").lower()

    # Check for common function syntax issues
    if "pow(" in clean_expr and "," not in clean_expr:
        raise ValueError(
            "Function 'pow()' requires two parameters: pow(base, exponent). Example: pow(2, 3)"
        )

    # Check for empty function calls (functions with no parameters)
    for func in MATH_FUNCTIONS_SINGLE:
        empty_call = f"{func}()"
        if empty_call in clean_expr:
            raise ValueError(f"Function '{func}()' requires one parameter. Example: {func}(3.14)")


def safe_eval_expression(expression: str) -> float:
    """Safely evaluate mathematical expressions with restricted scope."""
    # Validate syntax and provide helpful error messages
    _validate_expression_syntax(expression)

    # Remove whitespace
    clean_expr = expression.replace(" ", "")

    # Only allow safe characters (including comma for function parameters)
    allowed_chars = set("0123456789+-*/.(),e")

    # Security check - log and block dangerous patterns
    if any(pattern in clean_expr.lower() for pattern in DANGEROUS_PATTERNS):
        logging.warning(f"Security: Blocked unsafe expression attempt: {expression[:50]}...")
        raise ValueError(
            "Expression contains forbidden operations. Only mathematical expressions are allowed."
        )

    # Check for unsafe characters
    if not all(c in allowed_chars or c.isalpha() for c in clean_expr):
        raise ValueError(
            "Expression contains invalid characters. Use only numbers, +, -, *, /, (), and math functions."
        )

    # Replace math functions with safe alternatives
    safe_expr = clean_expr
    for func in MATH_FUNCTIONS_ALL:
        if func in clean_expr:
            if func != "abs":  # abs is built-in, others need math module
                safe_expr = safe_expr.replace(func, f"math.{func}")

    # Evaluate with restricted globals
    try:
        allowed_globals = {"__builtins__": {"abs": abs}, "math": math}
        result = eval(safe_expr, allowed_globals, {})
        return float(result)
    except ZeroDivisionError:
        raise ValueError("Mathematical error: Division by zero is undefined.")
    except OverflowError:
        raise ValueError("Mathematical error: Result is too large to compute.")
    except ValueError as e:
        if "math domain error" in str(e):
            raise ValueError(
                "Mathematical error: Invalid input for function (e.g., sqrt of negative number)."
            )
        raise ValueError(f"Mathematical expression error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Expression evaluation failed: {str(e)}")


def validate_variable_name(name: str) -> str:
    """Validate variable name for filesystem safety (alphanumeric + underscore/hyphen only)."""
    if not name.strip():
        raise ValueError("Variable name cannot be empty")
    if not name.replace("_", "").replace("-", "").isalnum():
        raise ValueError(
            "Variable name must contain only letters, numbers, underscores, and hyphens"
        )
    return name


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin."""
    from_lower = from_unit.lower()
    to_lower = to_unit.lower()

    # Direct conversion if same unit
    if from_lower == to_lower:
        return value

    # Convert to Celsius first if not already
    if from_lower == "c":
        celsius = value
    elif from_lower in TEMP_CONVERSIONS:
        celsius = TEMP_CONVERSIONS[from_lower]["c"](value)
    else:
        raise ValueError(f"Unknown temperature unit '{from_unit}'")

    # Convert from Celsius to target
    if to_lower == "c":
        return celsius
    elif to_lower in TEMP_CONVERSIONS["c"]:
        return TEMP_CONVERSIONS["c"][to_lower](celsius)
    else:
        raise ValueError(f"Unknown temperature unit '{to_unit}'")


def _classify_expression_difficulty(expression: str) -> str:
    """Classify mathematical expression difficulty for educational annotations."""
    clean_expr = expression.replace(" ", "").lower()

    # Count complexity indicators
    has_functions = any(func in clean_expr for func in MATH_FUNCTIONS_ALL)
    has_parentheses = "(" in clean_expr
    has_exponents = "**" in clean_expr or "^" in clean_expr
    operator_count = sum(clean_expr.count(op) for op in "+-*/")

    if has_functions or has_exponents:
        return "advanced"
    elif has_parentheses or operator_count > 2:
        return "intermediate"
    else:
        return "basic"


def _classify_expression_topic(expression: str) -> str:
    """Enhanced topic classification for educational metadata."""
    clean_expr = expression.lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(word in clean_expr for word in keywords):
            return topic

    return "arithmetic"


async def evaluate_with_timeout(expression: str) -> float:
    """
    Safely evaluate mathematical expression with execution timeout.

    Prevents denial-of-service by ensuring expression evaluation completes
    within EXPRESSION_TIMEOUT_SECONDS. Wraps synchronous safe_eval_expression()
    in a ProcessPoolExecutor to allow timeout enforcement and eliminate GIL
    contention for CPU-bound evaluation.

    This is an educational example of wrapping CPU-bound synchronous operations
    in async context using asyncio.wait_for() and loop.run_in_executor().

    Args:
        expression: Mathematical expression string to evaluate.

    Returns:
        float: Result of the expression evaluation.

    Raises:
        ValueError: If expression evaluation exceeds timeout or is invalid.
    """
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(_executor, safe_eval_expression, expression),
            timeout=EXPRESSION_TIMEOUT_SECONDS,
        )
    except TimeoutError as e:
        raise ValueError(
            f"Expression evaluation exceeded {EXPRESSION_TIMEOUT_SECONDS}s timeout. "
            f"Try simplifying the expression or breaking it into smaller parts."
        ) from e
    except BrokenProcessPool as e:
        raise ValueError("Expression evaluation failed: subprocess error") from e
