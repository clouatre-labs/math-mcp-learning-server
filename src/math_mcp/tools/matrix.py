"""Matrix operations tools for FastMCP.

Provides matrix multiplication, transpose, determinant, inverse, and eigenvalue
calculations using NumPy. All tools include input validation, error handling,
and educational annotations.
"""

import logging
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, SkipValidation

from math_mcp.settings import MAX_ARRAY_SIZE, validated_tool

logger = logging.getLogger(__name__)

# Try importing numpy for matrix operations
try:
    import numpy as np
    import numpy.linalg as la

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    la = None  # type: ignore


class MatrixMultiplyResult(BaseModel):
    """Result of matrix multiplication operation."""

    rows_a: int
    cols_a: int
    rows_b: int
    cols_b: int
    result_matrix: list[list[float]]
    difficulty: str
    topic: str


class MatrixTransposeResult(BaseModel):
    """Result of matrix transpose operation."""

    original_rows: int
    original_cols: int
    result_matrix: list[list[float]]
    difficulty: str
    topic: str


class MatrixDeterminantResult(BaseModel):
    """Result of matrix determinant calculation."""

    size: int
    determinant: float
    difficulty: str
    topic: str


class MatrixInverseResult(BaseModel):
    """Result of matrix inverse calculation."""

    size: int
    success: bool
    result_matrix: list[list[float]] | None = None
    error: str | None = None
    difficulty: str
    topic: str


class MatrixEigenvaluesResult(BaseModel):
    """Result of matrix eigenvalues calculation."""

    size: int
    success: bool
    eigenvalues: list[float] | None = None
    eigenvectors: list[list[float]] | None = None
    error: str | None = None
    complex_eigenvalues_warning: str | None = None
    complex_values: list[str] | None = None
    difficulty: str
    topic: str


def _check_numpy_available() -> None:
    """Check if numpy is available and raise error if not."""
    if not NUMPY_AVAILABLE:
        raise ValueError(
            "NumPy is required for matrix operations. "
            "Install with: pip install math-mcp-learning-server[scientific]"
        )


def _validate_matrix(matrix: list[list[float]], max_size: int = 100) -> Any:  # np.ndarray
    """Validate matrix input and convert to numpy array.

    Returns:
        numpy.ndarray: Validated matrix

    Raises:
        ValueError: If matrix is invalid
    """
    _check_numpy_available()

    if not matrix:
        raise ValueError("Matrix cannot be empty")

    if not all(isinstance(row, list) for row in matrix):
        raise ValueError("Matrix must be a list of lists")

    row_lengths = [len(row) for row in matrix]
    if len(set(row_lengths)) > 1:
        raise ValueError("All matrix rows must have the same length")

    if not all(isinstance(val, (int, float)) for row in matrix for val in row):
        raise ValueError("All matrix elements must be numeric (int or float)")

    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0

    if rows > max_size or cols > max_size:
        raise ValueError(
            f"Matrix dimensions ({rows}x{cols}) exceed maximum size ({max_size}x{max_size})"
        )

    return np.array(matrix, dtype=float)  # type: ignore


# Module-level FastMCP instance for matrix operations
matrix_mcp = FastMCP("matrix-operations")


@matrix_mcp.tool(
    name="matrix_multiply",
    annotations=ToolAnnotations(
        title="Matrix Multiplication",
        read_only_hint=True,
        idempotent_hint=True,
    ),
)
@validated_tool
async def matrix_multiply(
    matrix_a: Annotated[
        list[list[float]],
        Field(
            max_length=MAX_ARRAY_SIZE,
            description="2D list of numbers representing the first matrix. Each inner list is a row. Example: [[1, 2], [3, 4]]",
        ),
    ],
    matrix_b: Annotated[
        list[list[float]],
        Field(
            max_length=MAX_ARRAY_SIZE,
            description="2D list of numbers representing the second matrix. Each inner list is a row. Example: [[5, 6], [7, 8]]",
        ),
    ],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixMultiplyResult:
    """Multiply two matrices (A × B).

    Note:
        Requires NumPy. Raises ValueError if NumPy is unavailable.

    Examples:
        matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
        matrix_multiply([[1, 2, 3]], [[1], [2], [3]])
    """
    logger.info("Performing matrix multiplication")

    mat_a = _validate_matrix(matrix_a)
    mat_b = _validate_matrix(matrix_b)

    if mat_a.shape[1] != mat_b.shape[0]:
        raise ValueError(
            f"Incompatible matrix dimensions for multiplication: "
            f"({mat_a.shape[0]}x{mat_a.shape[1]}) × ({mat_b.shape[0]}x{mat_b.shape[1]}). "
            f"Number of columns in first matrix must equal number of rows in second matrix."
        )

    result = np.matmul(mat_a, mat_b)  # type: ignore
    result_list = result.tolist()  # type: ignore

    return MatrixMultiplyResult(
        rows_a=int(mat_a.shape[0]),
        cols_a=int(mat_a.shape[1]),
        rows_b=int(mat_b.shape[0]),
        cols_b=int(mat_b.shape[1]),
        result_matrix=result_list,
        difficulty="intermediate",
        topic="linear_algebra",
    )


@matrix_mcp.tool(
    name="matrix_transpose",
    annotations=ToolAnnotations(
        title="Matrix Transpose",
        read_only_hint=True,
        idempotent_hint=True,
    ),
)
@validated_tool
async def matrix_transpose(
    matrix: Annotated[
        list[list[float]],
        Field(
            max_length=MAX_ARRAY_SIZE,
            description="2D list of numbers representing the matrix. Each inner list is a row. Example: [[1, 2, 3], [4, 5, 6]]",
        ),
    ],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixTransposeResult:
    """Transpose a matrix (swap rows and columns).

    Note:
        Requires NumPy. Raises ValueError if NumPy is unavailable.

    Examples:
        matrix_transpose([[1, 2, 3], [4, 5, 6]])
        matrix_transpose([[1], [2], [3]])
    """
    logger.info("Transposing matrix")

    mat = _validate_matrix(matrix)
    result = mat.T  # type: ignore
    result_list = result.tolist()  # type: ignore

    return MatrixTransposeResult(
        original_rows=int(mat.shape[0]),
        original_cols=int(mat.shape[1]),
        result_matrix=result_list,
        difficulty="beginner",
        topic="linear_algebra",
    )


@matrix_mcp.tool(
    name="matrix_determinant",
    annotations=ToolAnnotations(
        title="Matrix Determinant",
        read_only_hint=True,
        idempotent_hint=True,
    ),
)
@validated_tool
async def matrix_determinant(
    matrix: Annotated[
        list[list[float]],
        Field(
            max_length=MAX_ARRAY_SIZE,
            description="2D list of numbers representing a square matrix. Each inner list is a row. Example: [[1, 2], [3, 4]]",
        ),
    ],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixDeterminantResult:
    """Calculate the determinant of a square matrix.

    Note:
        Requires NumPy. Raises ValueError if NumPy is unavailable.

    Examples:
        matrix_determinant([[1, 2], [3, 4]])
        matrix_determinant([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # Identity matrix
    """
    logger.info("Calculating matrix determinant")

    mat = _validate_matrix(matrix)

    if mat.shape[0] != mat.shape[1]:
        raise ValueError(
            f"Determinant requires a square matrix. "
            f"Got {mat.shape[0]}x{mat.shape[1]} matrix instead."
        )

    det = la.det(mat)  # type: ignore

    return MatrixDeterminantResult(
        size=int(mat.shape[0]),
        determinant=float(det),
        difficulty="intermediate",
        topic="linear_algebra",
    )


@matrix_mcp.tool(
    name="matrix_inverse",
    annotations=ToolAnnotations(
        title="Matrix Inverse",
        read_only_hint=True,
        idempotent_hint=True,
    ),
)
@validated_tool
async def matrix_inverse(
    matrix: Annotated[
        list[list[float]],
        Field(
            max_length=MAX_ARRAY_SIZE,
            description="2D list of numbers representing a square matrix. Each inner list is a row. Example: [[1, 2], [3, 4]]",
        ),
    ],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixInverseResult:
    """Calculate the inverse of a square matrix.

    Note:
        Requires NumPy. Raises ValueError if NumPy is unavailable.

    Examples:
        matrix_inverse([[1, 2], [3, 4]])
        matrix_inverse([[2, 0], [0, 2]])  # Diagonal matrix
    """
    logger.info("Calculating matrix inverse")

    if ctx:
        await ctx.report_progress(0, 3, "Validating matrix")

    mat = _validate_matrix(matrix)

    if mat.shape[0] != mat.shape[1]:
        raise ValueError(
            f"Matrix inverse requires a square matrix. "
            f"Got {mat.shape[0]}x{mat.shape[1]} matrix instead."
        )

    if ctx:
        await ctx.report_progress(1, 3, "Checking singularity")

    det = la.det(mat)  # type: ignore
    if abs(det) < 1e-10:
        logger.warning("Matrix is singular (determinant near 0); inverse does not exist")
        return MatrixInverseResult(
            size=int(mat.shape[0]),
            success=False,
            error="Matrix is singular (determinant ≈ 0). Cannot compute inverse for singular matrices.",
            difficulty="advanced",
            topic="linear_algebra",
        )

    if ctx:
        await ctx.report_progress(2, 3, "Computing inverse")

    result = la.inv(mat)  # type: ignore
    result_list = result.tolist()  # type: ignore

    if ctx:
        await ctx.report_progress(3, 3, "Complete")

    return MatrixInverseResult(
        size=int(mat.shape[0]),
        success=True,
        result_matrix=result_list,
        difficulty="advanced",
        topic="linear_algebra",
    )


@matrix_mcp.tool(
    name="matrix_eigenvalues",
    annotations=ToolAnnotations(
        title="Matrix Eigenvalues",
        read_only_hint=True,
        idempotent_hint=True,
    ),
)
@validated_tool
async def matrix_eigenvalues(
    matrix: Annotated[
        list[list[float]],
        Field(
            max_length=MAX_ARRAY_SIZE,
            description="2D list of numbers representing a square matrix. Each inner list is a row. Example: [[4, 2], [1, 3]]",
        ),
    ],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixEigenvaluesResult:
    """Calculate the eigenvalues of a square matrix.

    Note:
        Requires NumPy. Raises ValueError if NumPy is unavailable.

    Examples:
        matrix_eigenvalues([[4, 2], [1, 3]])
        matrix_eigenvalues([[3, 0, 0], [0, 5, 0], [0, 0, 7]])  # Diagonal matrix
    """
    logger.info("Calculating matrix eigenvalues")

    if ctx:
        await ctx.report_progress(0, 2, "Validating matrix")

    mat = _validate_matrix(matrix)

    if mat.shape[0] != mat.shape[1]:
        logger.warning(f"Eigenvalues require square matrix; got {mat.shape[0]}x{mat.shape[1]}")
        return MatrixEigenvaluesResult(
            size=int(mat.shape[0]),
            success=False,
            error=f"Eigenvalues require a square matrix. Got {mat.shape[0]}x{mat.shape[1]} matrix instead.",
            difficulty="advanced",
            topic="linear_algebra",
        )

    if ctx:
        await ctx.report_progress(1, 2, "Calculating eigenvalues")

    eigenvalues = la.eigvals(mat)  # type: ignore

    # Detect complex eigenvalues (imaginary part exceeds floating-point noise threshold)
    has_complex = any(abs(val.imag) > 1e-10 for val in eigenvalues)
    if has_complex:
        logger.warning(
            "Matrix has complex eigenvalues; imaginary parts truncated to real in eigenvalues field"
        )

    # Convert eigenvalues to list of floats (real parts only, for backward compat)
    eigenval_list = [float(val.real) for val in eigenvalues]  # type: ignore

    # Build complex_values strings when imaginary parts are significant
    complex_values = (
        [f"{val.real:.6g}+{val.imag:.6g}i" for val in eigenvalues]  # type: ignore
        if has_complex
        else None
    )
    complex_warning = (
        "Imaginary parts truncated; see complex_values for full representation"
        if has_complex
        else None
    )

    if ctx:
        await ctx.report_progress(2, 2, "Complete")

    return MatrixEigenvaluesResult(
        size=int(mat.shape[0]),
        success=True,
        eigenvalues=eigenval_list,
        complex_eigenvalues_warning=complex_warning,
        complex_values=complex_values,
        difficulty="advanced",
        topic="linear_algebra",
    )


__all__ = [
    "matrix_mcp",
    "matrix_multiply",
    "matrix_transpose",
    "matrix_determinant",
    "matrix_inverse",
    "matrix_eigenvalues",
]
