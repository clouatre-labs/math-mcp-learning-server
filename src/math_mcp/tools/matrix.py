"""Matrix operations tools for FastMCP.

Provides matrix multiplication, transpose, determinant, inverse, and eigenvalue
calculations using NumPy. All tools include input validation, error handling,
and educational annotations.
"""

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field, SkipValidation

from math_mcp.settings import MAX_ARRAY_SIZE, validated_tool

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

    Args:
        matrix: Input matrix as list of lists
        max_size: Maximum dimension size (prevents DoS)

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


def _format_matrix(matrix_array: Any) -> str:
    """Format numpy array as readable string.

    Args:
        matrix_array: numpy array to format

    Returns:
        Formatted string representation
    """
    if matrix_array.size == 0:
        return "[]"

    # For small matrices, show full precision
    if matrix_array.size <= 9:
        return str(matrix_array)

    # For larger matrices, use compact format
    return np.array2string(matrix_array, separator=", ", suppress_small=True, precision=6)  # type: ignore


# Module-level FastMCP instance for matrix operations
matrix_mcp = FastMCP("matrix-operations")


@matrix_mcp.tool(
    annotations={
        "title": "Matrix Multiplication",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
async def matrix_multiply(
    matrix_a: Annotated[list[list[float]], Field(max_length=MAX_ARRAY_SIZE)],
    matrix_b: Annotated[list[list[float]], Field(max_length=MAX_ARRAY_SIZE)],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixMultiplyResult:
    """Multiply two matrices (A × B).

    Args:
        matrix_a: First matrix (m x n)
        matrix_b: Second matrix (n x p)

    Returns:
        Result matrix (m x p)

    Examples:
        matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
        matrix_multiply([[1, 2, 3]], [[1], [2], [3]])
    """
    if ctx:
        await ctx.info("Performing matrix multiplication")

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
    annotations={
        "title": "Matrix Transpose",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
async def matrix_transpose(
    matrix: Annotated[list[list[float]], Field(max_length=MAX_ARRAY_SIZE)],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixTransposeResult:
    """Transpose a matrix (swap rows and columns).

    Args:
        matrix: Input matrix (m x n)

    Returns:
        Transposed matrix (n x m)

    Examples:
        matrix_transpose([[1, 2, 3], [4, 5, 6]])
        matrix_transpose([[1], [2], [3]])
    """
    if ctx:
        await ctx.info("Transposing matrix")

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
    annotations={
        "title": "Matrix Determinant",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
async def matrix_determinant(
    matrix: Annotated[list[list[float]], Field(max_length=MAX_ARRAY_SIZE)],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixDeterminantResult:
    """Calculate the determinant of a square matrix.

    Args:
        matrix: Square matrix (n x n)

    Returns:
        Determinant value (scalar)

    Examples:
        matrix_determinant([[1, 2], [3, 4]])
        matrix_determinant([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # Identity matrix
    """
    if ctx:
        await ctx.info("Calculating matrix determinant")

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
    annotations={
        "title": "Matrix Inverse",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
async def matrix_inverse(
    matrix: Annotated[list[list[float]], Field(max_length=MAX_ARRAY_SIZE)],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixInverseResult:
    """Calculate the inverse of a square matrix.

    Args:
        matrix: Square matrix (n x n)

    Returns:
        Inverse matrix (n x n)

    Examples:
        matrix_inverse([[1, 2], [3, 4]])
        matrix_inverse([[2, 0], [0, 2]])  # Diagonal matrix
    """
    if ctx:
        await ctx.info("Calculating matrix inverse")

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
    annotations={
        "title": "Matrix Eigenvalues",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
async def matrix_eigenvalues(
    matrix: Annotated[list[list[float]], Field(max_length=MAX_ARRAY_SIZE)],
    ctx: SkipValidation[Context | None] = None,
) -> MatrixEigenvaluesResult:
    """Calculate the eigenvalues of a square matrix.

    Args:
        matrix: Square matrix (n x n)

    Returns:
        List of eigenvalues (may be complex numbers)

    Examples:
        matrix_eigenvalues([[4, 2], [1, 3]])
        matrix_eigenvalues([[3, 0, 0], [0, 5, 0], [0, 0, 7]])  # Diagonal matrix
    """
    if ctx:
        await ctx.info("Calculating matrix eigenvalues")

    if ctx:
        await ctx.report_progress(0, 2, "Validating matrix")

    mat = _validate_matrix(matrix)

    if mat.shape[0] != mat.shape[1]:
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

    # Convert eigenvalues to list of floats (real part only for display)
    eigenval_list = [float(val.real) if np.isreal(val) else float(val.real) for val in eigenvalues]  # type: ignore

    if ctx:
        await ctx.report_progress(2, 2, "Complete")

    return MatrixEigenvaluesResult(
        size=int(mat.shape[0]),
        success=True,
        eigenvalues=eigenval_list,
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
