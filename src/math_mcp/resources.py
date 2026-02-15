"""
Resources and Prompts Sub-Server
FastMCP sub-server for mathematical resources, constants, and prompt templates.
"""

import math

from fastmcp import Context, FastMCP

# Create sub-server for resources and prompts
resources_mcp = FastMCP(name="Resources and Prompts")


@resources_mcp.resource("math://test")
async def simple_test(ctx: Context) -> str:
    """Simple test resource like FastMCP examples"""
    await ctx.info("Accessing test resource")
    return "Test resource working successfully!"


@resources_mcp.resource(
    "math://constants/{constant}", annotations={"readOnlyHint": True, "idempotentHint": True}
)
def get_math_constant(constant: str) -> str:
    """Get mathematical constants like pi, e, golden ratio, etc."""
    constants = {
        "pi": {"value": math.pi, "description": "Ratio of circle's circumference to diameter"},
        "e": {"value": math.e, "description": "Euler's number, base of natural logarithm"},
        "golden_ratio": {"value": (1 + math.sqrt(5)) / 2, "description": "Golden ratio φ"},
        "euler_gamma": {"value": 0.5772156649015329, "description": "Euler-Mascheroni constant γ"},
        "sqrt2": {"value": math.sqrt(2), "description": "Square root of 2"},
        "sqrt3": {"value": math.sqrt(3), "description": "Square root of 3"},
    }

    if constant not in constants:
        available = ", ".join(constants.keys())
        return f"Unknown constant '{constant}'. Available constants: {available}"

    const_info = constants[constant]
    return f"{constant}: {const_info['value']}\nDescription: {const_info['description']}"


@resources_mcp.resource("math://functions")
async def list_available_functions(ctx: Context) -> str:
    """List all available mathematical functions with examples and syntax help."""
    await ctx.info("Accessing function reference documentation")
    return """# Available Mathematical Functions

## Basic Functions
- **abs(x)**: Absolute value
  - Example: abs(-5) = 5.0

## Trigonometric Functions
- **sin(x)**: Sine (input in radians)
  - Example: sin(3.14159/2) ≈ 1.0
- **cos(x)**: Cosine (input in radians)
  - Example: cos(0) = 1.0
- **tan(x)**: Tangent (input in radians)
  - Example: tan(3.14159/4) ≈ 1.0

## Mathematical Functions
- **sqrt(x)**: Square root
  - Example: sqrt(16) = 4.0
- **log(x)**: Natural logarithm
  - Example: log(2.71828) ≈ 1.0
- **pow(x, y)**: x raised to the power of y
  - Example: pow(2, 3) = 8.0

## Usage Notes
- All functions use parentheses: function(parameter)
- Multi-parameter functions use commas: pow(base, exponent)
- Use operators for basic math: +, -, *, /, **
- Parentheses for grouping: (2 + 3) * 4

## Examples
- Simple: 2 + 3 * 4 = 14.0
- Functions: sqrt(16) + pow(2, 3) = 12.0
- Complex: sin(3.14159/2) + cos(0) = 2.0
"""


@resources_mcp.resource("math://history")
async def get_calculation_history(ctx: Context) -> str:
    """Get the history of calculations performed across sessions."""
    await ctx.info("Accessing calculation history")
    from math_mcp.persistence.workspace import _workspace_manager

    workspace_data = _workspace_manager._load_workspace()

    if not workspace_data.variables:
        return "No calculations in workspace yet. Use save_calculation() to persist calculations."

    history_text = "Calculation History (from workspace):\n\n"

    variables = list(workspace_data.variables.items())
    variables.sort(key=lambda x: x[1].timestamp, reverse=True)

    for i, (name, var) in enumerate(variables[:10], 1):
        history_text += f"{i}. {name}: {var.expression} = {var.result} (saved {var.timestamp})\n"

    if len(variables) > 10:
        history_text += f"\n... and {len(variables) - 10} more calculations"

    return history_text


@resources_mcp.resource(
    "math://workspace", annotations={"readOnlyHint": True, "idempotentHint": False}
)
async def get_workspace(ctx: Context) -> str:
    """Get persistent calculation workspace showing all saved variables.

    This resource displays the complete state of the persistent workspace,
    including all saved calculations, metadata, and statistics. The workspace
    survives server restarts and is accessible across different transport modes.
    """
    await ctx.info("Accessing persistent workspace")
    from math_mcp.persistence.workspace import _workspace_manager

    return _workspace_manager.get_workspace_summary()


@resources_mcp.prompt()
def math_tutor(topic: str, level: str = "intermediate", include_examples: bool = True) -> str:
    """Generate a math tutoring prompt for explaining concepts.

    Args:
        topic: Mathematical topic to explain (e.g., "derivatives", "statistics")
        level: Difficulty level (beginner, intermediate, advanced)
        include_examples: Whether to include worked examples
    """
    prompt = f"""You are an expert mathematics tutor. Please explain the concept of {topic} at a {level} level.

Please structure your explanation as follows:
1. **Definition**: Provide a clear, concise definition
2. **Key Concepts**: Break down the main ideas
3. **Applications**: Where this is used in real life
"""

    if include_examples:
        prompt += "4. **Worked Examples**: Provide 2-3 step-by-step examples\n"

    prompt += f"""
Make your explanation engaging and accessible for a {level} learner. Use analogies when helpful, and encourage questions.
"""

    return prompt


@resources_mcp.prompt()
def formula_explainer(formula: str, context: str = "general mathematics") -> str:
    """Generate a prompt for explaining mathematical formulas in detail.

    Args:
        formula: The mathematical formula to explain (e.g., "A = πr²")
        context: The mathematical context (e.g., "geometry", "calculus", "statistics")
    """
    return f"""Please provide a comprehensive explanation of the formula: {formula}

Include the following in your explanation:

1. **What it represents**: What does this formula calculate or describe?
2. **Variable definitions**: Define each variable/symbol in the formula
3. **Context**: How this formula fits within {context}
4. **Step-by-step breakdown**: If the formula has multiple parts, explain each step
5. **Example calculation**: Show how to use the formula with specific numbers
6. **Real-world applications**: Where might someone use this formula?
7. **Common mistakes**: What errors do people often make when using this formula?

Make your explanation clear and educational, suitable for someone learning about {context}.
"""
