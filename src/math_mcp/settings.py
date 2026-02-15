"""Configuration management for Math MCP Server."""

from typing import Final

from pydantic import ConfigDict, Field, field_validator, validate_call
from pydantic_settings import BaseSettings

__all__ = [
    "MathMCPSettings",
    "validated_tool",
    "MATH_FUNCTIONS_SINGLE",
    "MATH_FUNCTIONS_ALL",
    "DANGEROUS_PATTERNS",
    "ALLOWED_OPERATIONS",
    "ALLOWED_TRENDS",
    "TOPIC_KEYWORDS",
    "TEMP_CONVERSIONS",
    "EXPRESSION_TIMEOUT_SECONDS",
    "RATE_LIMIT_PER_MINUTE",
    "MAX_EXPRESSION_LENGTH",
    "MAX_STRING_PARAM_LENGTH",
    "MAX_ARRAY_SIZE",
    "MAX_GROUPS_COUNT",
    "MAX_GROUP_SIZE",
    "MAX_VARIABLE_NAME_LENGTH",
    "MAX_DAYS_FINANCIAL",
]


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

# === SHARED SETTINGS INSTANCE ===

_settings = MathMCPSettings()

# === DERIVED CONSTANTS (from shared _settings instance) ===

EXPRESSION_TIMEOUT_SECONDS: Final[float] = _settings.math_timeout
RATE_LIMIT_PER_MINUTE: Final[int] = _settings.mcp_rate_limit_per_minute
MAX_EXPRESSION_LENGTH: Final[int] = _settings.max_expression_length
MAX_STRING_PARAM_LENGTH: Final[int] = _settings.max_string_param_length
MAX_ARRAY_SIZE: Final[int] = _settings.max_array_size
MAX_GROUPS_COUNT: Final[int] = _settings.max_groups_count
MAX_GROUP_SIZE: Final[int] = _settings.max_group_size
MAX_VARIABLE_NAME_LENGTH: Final[int] = _settings.max_variable_name_length
MAX_DAYS_FINANCIAL: Final[int] = _settings.max_days_financial
