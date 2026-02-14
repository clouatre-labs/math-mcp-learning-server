"""Configuration management for Math MCP Server."""

from pydantic import ConfigDict, Field, field_validator, validate_call
from pydantic_settings import BaseSettings


class MathMCPSettings(BaseSettings):
    """Environment-based configuration with automatic validation."""

    math_timeout: float = 5.0
    mcp_rate_limit_per_minute: int = Field(default=100, ge=0)
    max_expression_length: int = Field(default=500, ge=0)
    max_string_param_length: int = Field(default=100, ge=0)
    max_array_size: int = Field(default=10000, ge=0)
    max_groups_count: int = Field(default=100, ge=0)
    max_group_size: int = Field(default=1000, ge=0)
    max_variable_name_length: int = Field(default=50, ge=0)
    max_days_financial: int = Field(default=1000, ge=0)

    model_config = ConfigDict(env_prefix="", case_sensitive=False)

    @field_validator("math_timeout", mode="after")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Ensure timeout is positive."""
        if v <= 0:
            raise ValueError("math_timeout must be positive")
        return v


# === CUSTOM DECORATOR FOR TOOL VALIDATION ===


def validated_tool(func):
    """Apply Pydantic validation to tool functions with Context support."""
    return validate_call(config={"arbitrary_types_allowed": True})(func)


# === CONSTANTS ===

MATH_FUNCTIONS_SINGLE = ["sin", "cos", "tan", "log", "sqrt", "abs"]
MATH_FUNCTIONS_ALL = {"sin", "cos", "tan", "log", "sqrt", "abs", "pow", "exp"}
DANGEROUS_PATTERNS = ["import", "exec", "__", "eval", "open", "file"]

ALLOWED_OPERATIONS = {"mean", "median", "mode", "std_dev", "variance"}
ALLOWED_TRENDS = {"bullish", "bearish", "volatile"}

TOPIC_KEYWORDS = {
    "finance": ["interest", "rate", "investment", "portfolio"],
    "geometry": ["pi", "radius", "area", "volume"],
    "trigonometry": ["sin", "cos", "tan"],
    "logarithms": ["log", "ln", "exp"],
}

TEMP_CONVERSIONS = {
    "c": {"f": lambda c: c * 9 / 5 + 32, "k": lambda c: c + 273.15},
    "f": {"c": lambda f: (f - 32) * 5 / 9, "k": lambda f: (f - 32) * 5 / 9 + 273.15},
    "k": {"c": lambda k: k - 273.15, "f": lambda k: (k - 273.15) * 9 / 5 + 32},
}
