"""Matrix operations tools for FastMCP.

Provides matrix multiplication, transpose, determinant, inverse, and eigenvalue
calculations using NumPy. All tools include input validation, error handling,
and educational annotations.
"""

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field, SkipValidation

from math_mcp.settings import validated_tool

# Try importing numpy for matrix operations
try:
    import numpy as np
    import numpy.linalg as la

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    la = None  # type: ignore

# Fallback if create_matrix_tools() is not called with a custom value
MAX_ARRAY_SIZE = 10000


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


def create_matrix_tools(mcp: FastMCP, max_array_size: int = 10000) -> None:
    """Create and register matrix operation tools with the MCP instance.

    Args:
        mcp: FastMCP instance to register tools with
        max_array_size: Maximum array size for validation
    """
    global MAX_ARRAY_SIZE
    MAX_ARRAY_SIZE = max_array_size

    @mcp.tool(
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
    ) -> dict[str, Any]:
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

        try:
            mat_a = _validate_matrix(matrix_a)
            mat_b = _validate_matrix(matrix_b)

            if mat_a.shape[1] != mat_b.shape[0]:
                raise ValueError(
                    f"Incompatible matrix dimensions for multiplication: "
                    f"({mat_a.shape[0]}x{mat_a.shape[1]}) × ({mat_b.shape[0]}x{mat_b.shape[1]}). "
                    f"Number of columns in first matrix must equal number of rows in second matrix."
                )

            result = np.matmul(mat_a, mat_b)  # type: ignore

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Multiplication Result:**\n{_format_matrix(result)}",
                        "annotations": {
                            "difficulty": "intermediate",
                            "topic": "linear_algebra",
                            "operation": "matrix_multiply",
                            "result_shape": f"{result.shape[0]}x{result.shape[1]}",
                        },
                    }
                ]
            }

        except ValueError as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Multiply Error:** {str(e)}",
                        "annotations": {
                            "error": "matrix_multiply_error",
                            "difficulty": "intermediate",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Unexpected Error:** {str(e)}",
                        "annotations": {
                            "error": "unexpected_error",
                            "difficulty": "intermediate",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }

    @mcp.tool(
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
    ) -> dict[str, Any]:
        """Transpose a matrix (swap rows and columns).

        Args:
            matrix: Input matrix

        Returns:
            Transposed matrix

        Examples:
            matrix_transpose([[1, 2, 3], [4, 5, 6]])  # Returns [[1, 4], [2, 5], [3, 6]]
            matrix_transpose([[1, 2], [3, 4]])
        """
        if ctx:
            await ctx.info("Performing matrix transpose")

        try:
            mat = _validate_matrix(matrix)
            result = np.transpose(mat)  # type: ignore

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Transpose Result:**\n{_format_matrix(result)}",
                        "annotations": {
                            "difficulty": "basic",
                            "topic": "linear_algebra",
                            "operation": "matrix_transpose",
                            "result_shape": f"{result.shape[0]}x{result.shape[1]}",
                        },
                    }
                ]
            }

        except ValueError as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Transpose Error:** {str(e)}",
                        "annotations": {
                            "error": "matrix_transpose_error",
                            "difficulty": "basic",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Unexpected Error:** {str(e)}",
                        "annotations": {
                            "error": "unexpected_error",
                            "difficulty": "basic",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }

    @mcp.tool(
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
    ) -> dict[str, Any]:
        """Calculate the determinant of a square matrix.

        Args:
            matrix: Square matrix (n x n)

        Returns:
            Determinant value

        Examples:
            matrix_determinant([[4, 6], [3, 8]])  # Returns 14
            matrix_determinant([[1, 2], [2, 4]])  # Returns 0 (singular)
        """
        if ctx:
            await ctx.info("Calculating matrix determinant")

        try:
            mat = _validate_matrix(matrix)

            if mat.shape[0] != mat.shape[1]:
                raise ValueError(
                    f"Determinant requires a square matrix. "
                    f"Got {mat.shape[0]}x{mat.shape[1]} matrix instead."
                )

            det = la.det(mat)  # type: ignore

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Determinant:** {det:.6g}",
                        "annotations": {
                            "difficulty": "intermediate",
                            "topic": "linear_algebra",
                            "operation": "matrix_determinant",
                            "matrix_size": f"{mat.shape[0]}x{mat.shape[1]}",
                            "result": f"{det:.6g}",
                        },
                    }
                ]
            }

        except ValueError as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Determinant Error:** {str(e)}",
                        "annotations": {
                            "error": "matrix_determinant_error",
                            "difficulty": "intermediate",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Unexpected Error:** {str(e)}",
                        "annotations": {
                            "error": "unexpected_error",
                            "difficulty": "intermediate",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }

    @mcp.tool(
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
    ) -> dict[str, Any]:
        """Calculate the inverse of a square matrix.

        Args:
            matrix: Square matrix (n x n)

        Returns:
            Inverse matrix

        Examples:
            matrix_inverse([[4, 7], [2, 6]])
            matrix_inverse([[1, 2], [3, 4]])
        """
        if ctx:
            await ctx.info("Calculating matrix inverse")

        try:
            mat = _validate_matrix(matrix)

            if mat.shape[0] != mat.shape[1]:
                raise ValueError(
                    f"Matrix inverse requires a square matrix. "
                    f"Got {mat.shape[0]}x{mat.shape[1]} matrix instead."
                )

            det = la.det(mat)  # type: ignore
            if abs(det) < 1e-10:
                raise ValueError("Matrix is singular (determinant ≈ 0). Cannot compute inverse.")

            result = la.inv(mat)  # type: ignore

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Inverse Result:**\n{_format_matrix(result)}",
                        "annotations": {
                            "difficulty": "advanced",
                            "topic": "linear_algebra",
                            "operation": "matrix_inverse",
                            "matrix_size": f"{mat.shape[0]}x{mat.shape[1]}",
                        },
                    }
                ]
            }

        except ValueError as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Inverse Error:** {str(e)}",
                        "annotations": {
                            "error": "matrix_inverse_error",
                            "difficulty": "advanced",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Unexpected Error:** {str(e)}",
                        "annotations": {
                            "error": "unexpected_error",
                            "difficulty": "advanced",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }

    @mcp.tool(
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
    ) -> dict[str, Any]:
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

        try:
            mat = _validate_matrix(matrix)

            if mat.shape[0] != mat.shape[1]:
                raise ValueError(
                    f"Eigenvalues require a square matrix. "
                    f"Got {mat.shape[0]}x{mat.shape[1]} matrix instead."
                )

            eigenvalues = la.eigvals(mat)  # type: ignore

            # Format eigenvalues (handle complex numbers)
            def _format_complex_eigenvalue(val: Any) -> str:
                """Format complex eigenvalue avoiding +- for negative imaginary parts."""
                if np.isreal(val):  # type: ignore
                    return f"{val.real:.6g}"
                elif val.imag >= 0:
                    return f"{val.real:.6g}+{val.imag:.6g}j"
                else:
                    return f"{val.real:.6g}{val.imag:.6g}j"  # negative sign already in val.imag

            eigenval_str = ", ".join([_format_complex_eigenvalue(val) for val in eigenvalues])

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Eigenvalues:** [{eigenval_str}]",
                        "annotations": {
                            "difficulty": "advanced",
                            "topic": "linear_algebra",
                            "operation": "matrix_eigenvalues",
                            "matrix_size": f"{mat.shape[0]}x{mat.shape[1]}",
                            "count": len(eigenvalues),
                        },
                    }
                ]
            }

        except ValueError as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Matrix Eigenvalues Error:** {str(e)}",
                        "annotations": {
                            "error": "matrix_eigenvalues_error",
                            "difficulty": "advanced",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"**Unexpected Error:** {str(e)}",
                        "annotations": {
                            "error": "unexpected_error",
                            "difficulty": "advanced",
                            "topic": "linear_algebra",
                        },
                    }
                ]
            }
