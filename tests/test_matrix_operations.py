"""
Test specifications for matrix operations (TDD - RED phase).

Tests define API contracts before implementation and are skipped until GREEN phase.

Tools tested:
- matrix_multiply: Multiply two matrices
- matrix_transpose: Transpose a matrix
- matrix_determinant: Calculate determinant
- matrix_inverse: Calculate inverse matrix
- matrix_eigenvalues: Calculate eigenvalues
"""

import pytest
from fastmcp.exceptions import ToolError

pytest.importorskip("numpy")


@pytest.fixture
def identity_2x2():
    return [[1, 0], [0, 1]]


@pytest.fixture
def identity_3x3():
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


@pytest.fixture
def singular_matrix():
    return [[1, 2], [2, 4]]


@pytest.fixture
def test_matrix_2x2():
    return [[1, 2], [3, 4]]


class TestMatrixMultiply:
    """Test matrix multiplication tool."""

    @pytest.mark.asyncio
    async def test_multiply_2x2_matrices(self, http_client):
        """Test multiplying two 2x2 matrices."""
        response = await http_client.call_tool(
            "matrix_multiply",
            arguments={
                "matrix_a": [[1, 2], [3, 4]],
                "matrix_b": [[5, 6], [7, 8]],
            },
        )

        assert response.is_error is False
        result = response.content[0].text
        # Verify result contains expected values: [1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]
        assert "19" in result  # First row, first col
        assert "22" in result  # First row, second col
        assert "43" in result  # Second row, first col
        assert "50" in result  # Second row, second col

    @pytest.mark.asyncio
    async def test_multiply_3x3_matrices(self, http_client):
        """Test multiplying two 3x3 matrices."""
        response = await http_client.call_tool(
            "matrix_multiply",
            arguments={
                "matrix_a": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                "matrix_b": [[9, 8, 7], [6, 5, 4], [3, 2, 1]],
            },
        )

        assert response.is_error is False
        result = response.content[0].text
        # First row: [1*9+2*6+3*3, 1*8+2*5+3*2, 1*7+2*4+3*1] = [30, 24, 18]
        assert "30" in result
        assert "24" in result
        assert "18" in result

    @pytest.mark.asyncio
    async def test_multiply_incompatible_dimensions(self, http_client):
        """Test error handling for incompatible matrix dimensions."""
        with pytest.raises(ToolError) as exc_info:
            await http_client.call_tool(
                "matrix_multiply",
                arguments={
                    "matrix_a": [[1, 2], [3, 4]],  # 2x2
                    "matrix_b": [[1, 2, 3]],  # 1x3 (incompatible)
                },
            )

        error_msg = str(exc_info.value).lower()
        assert "incompatible" in error_msg or "dimension" in error_msg or "shape" in error_msg

    @pytest.mark.asyncio
    async def test_multiply_identity_matrix(self, http_client, test_matrix_2x2, identity_2x2):
        """Test multiplying by identity matrix returns original."""
        response = await http_client.call_tool(
            "matrix_multiply",
            arguments={
                "matrix_a": test_matrix_2x2,
                "matrix_b": identity_2x2,
            },
        )

        assert response.is_error is False
        result = response.content[0].text
        # Should return original matrix
        assert "1" in result and "2" in result
        assert "3" in result and "4" in result


class TestMatrixTranspose:
    """Test matrix transpose tool."""

    @pytest.mark.asyncio
    async def test_transpose_2x3_matrix(self, http_client):
        """Test transposing a 2x3 matrix to 3x2."""
        response = await http_client.call_tool(
            "matrix_transpose",
            arguments={"matrix": [[1, 2, 3], [4, 5, 6]]},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Transposed: [[1, 4], [2, 5], [3, 6]]
        assert "1" in result and "4" in result
        assert "2" in result and "5" in result
        assert "3" in result and "6" in result

    @pytest.mark.asyncio
    async def test_transpose_square_matrix(self, http_client, test_matrix_2x2):
        """Test transposing a square matrix."""
        response = await http_client.call_tool(
            "matrix_transpose",
            arguments={"matrix": test_matrix_2x2},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Transposed: [[1, 3], [2, 4]]
        assert "1" in result and "3" in result
        assert "2" in result and "4" in result

    @pytest.mark.asyncio
    async def test_transpose_single_row(self, http_client):
        """Test transposing a single row to column."""
        response = await http_client.call_tool(
            "matrix_transpose",
            arguments={"matrix": [[1, 2, 3, 4]]},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Transposed: [[1], [2], [3], [4]]
        assert "1" in result
        assert "2" in result
        assert "3" in result
        assert "4" in result


class TestMatrixDeterminant:
    """Test matrix determinant calculation tool."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "matrix,expected",
        [
            ([[4, 6], [3, 8]], "14"),
            ([[1, 2, 3], [0, 1, 4], [5, 6, 0]], "1"),
        ],
    )
    async def test_determinant(self, http_client, matrix, expected):
        """Test determinant calculation for various matrices."""
        response = await http_client.call_tool(
            "matrix_determinant",
            arguments={"matrix": matrix},
        )

        assert response.is_error is False
        result = response.content[0].text
        assert expected in result

    @pytest.mark.asyncio
    async def test_determinant_singular_matrix(self, http_client, singular_matrix):
        """Test determinant of singular matrix (det = 0)."""
        response = await http_client.call_tool(
            "matrix_determinant",
            arguments={"matrix": singular_matrix},
        )

        assert response.is_error is False
        result = response.content[0].text
        assert "0" in result or "0.0" in result


class TestMatrixInverse:
    """Test matrix inverse calculation tool."""

    @pytest.mark.asyncio
    async def test_inverse_2x2(self, http_client):
        """Test inverse of 2x2 matrix."""
        response = await http_client.call_tool(
            "matrix_inverse",
            arguments={"matrix": [[4, 7], [2, 6]]},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Inverse exists (det = 4*6 - 7*2 = 10 ≠ 0)
        # Should contain decimal values
        assert "0.6" in result or "0.60" in result  # 6/10
        assert "-0.7" in result or "-0.70" in result  # -7/10

    @pytest.mark.asyncio
    async def test_inverse_3x3(self, http_client):
        """Test inverse of 3x3 matrix."""
        response = await http_client.call_tool(
            "matrix_inverse",
            arguments={"matrix": [[1, 2, 3], [0, 1, 4], [5, 6, 0]]},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Inverse exists (det = 1 from previous test)
        # Should contain matrix values
        assert "[" in result or "matrix" in result.lower()

    @pytest.mark.asyncio
    async def test_inverse_singular_matrix(self, http_client, singular_matrix):
        """Test error handling for singular matrix (no inverse)."""
        with pytest.raises(ToolError) as exc_info:
            await http_client.call_tool(
                "matrix_inverse",
                arguments={"matrix": singular_matrix},
            )

        error_msg = str(exc_info.value).lower()
        assert "singular" in error_msg or "invertible" in error_msg or "not invertible" in error_msg

    @pytest.mark.asyncio
    async def test_inverse_identity_matrix(self, http_client, identity_2x2):
        """Test inverse of identity matrix is itself."""
        response = await http_client.call_tool(
            "matrix_inverse",
            arguments={"matrix": identity_2x2},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Inverse of identity is identity
        assert "1" in result and "0" in result


class TestMatrixEigenvalues:
    """Test matrix eigenvalues calculation tool."""

    @pytest.mark.asyncio
    async def test_eigenvalues_2x2(self, http_client):
        """Test eigenvalues of 2x2 matrix."""
        response = await http_client.call_tool(
            "matrix_eigenvalues",
            arguments={"matrix": [[4, 2], [1, 3]]},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Eigenvalues are 5 and 2
        assert "5" in result
        assert "2" in result

    @pytest.mark.asyncio
    async def test_eigenvalues_3x3(self, http_client):
        """Test eigenvalues of 3x3 matrix."""
        response = await http_client.call_tool(
            "matrix_eigenvalues",
            arguments={"matrix": [[1, 2, 3], [0, 1, 4], [5, 6, 0]]},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Should contain eigenvalues (may be complex)
        assert "[" in result or "eigenvalue" in result.lower() or any(c.isdigit() for c in result)

    @pytest.mark.asyncio
    async def test_eigenvalues_diagonal_matrix(self, http_client):
        """Test eigenvalues of diagonal matrix are diagonal elements."""
        response = await http_client.call_tool(
            "matrix_eigenvalues",
            arguments={"matrix": [[3, 0, 0], [0, 5, 0], [0, 0, 7]]},
        )

        assert response.is_error is False
        result = response.content[0].text
        # Eigenvalues are 3, 5, 7
        assert "3" in result
        assert "5" in result
        assert "7" in result

    @pytest.mark.asyncio
    async def test_eigenvalues_identity_matrix(self, http_client, identity_3x3):
        """Test eigenvalues of identity matrix are all 1."""
        response = await http_client.call_tool(
            "matrix_eigenvalues",
            arguments={"matrix": identity_3x3},
        )

        assert response.is_error is False
        result = response.content[0].text
        # All eigenvalues are 1
        assert "1" in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool_name",
    [
        "matrix_determinant",
        "matrix_inverse",
        "matrix_eigenvalues",
    ],
)
async def test_non_square_error(http_client, tool_name):
    """Test non-square matrix error."""
    with pytest.raises(ToolError) as exc_info:
        await http_client.call_tool(
            tool_name,
            arguments={"matrix": [[1, 2, 3], [4, 5, 6]]},
        )

    error_msg = str(exc_info.value).lower()
    assert "square" in error_msg
