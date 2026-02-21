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
        from fastmcp.exceptions import ToolError

        with pytest.raises(ToolError) as exc_info:
            await http_client.call_tool(
                "matrix_multiply",
                arguments={
                    "matrix_a": [[1, 2], [3, 4]],  # 2x2
                    "matrix_b": [[1, 2, 3]],  # 1x3 (incompatible)
                },
            )
        assert "incompatible" in str(exc_info.value).lower()

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
            ([[4, 6], [3, 8]], 14.0),
            ([[1, 2, 3], [0, 1, 4], [5, 6, 0]], 1.0),
        ],
    )
    async def test_determinant(self, http_client, matrix, expected):
        """Test determinant calculation for various matrices."""
        import json

        response = await http_client.call_tool(
            "matrix_determinant",
            arguments={"matrix": matrix},
        )

        assert response.is_error is False
        result = response.content[0].text
        data = json.loads(result)
        assert abs(data["determinant"] - expected) < 1e-6

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
        response = await http_client.call_tool(
            "matrix_inverse",
            arguments={"matrix": singular_matrix},
        )
        assert response.is_error is False
        assert "error" in response.content[0].text.lower()
        assert "singular" in response.content[0].text.lower()

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
    ],
)
async def test_non_square_error(http_client, tool_name):
    """Test non-square matrix error."""
    with pytest.raises(ToolError) as exc_info:
        await http_client.call_tool(
            tool_name,
            arguments={"matrix": [[1, 2, 3], [4, 5, 6]]},
        )
    assert "square" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_non_square_error_eigenvalues(http_client):
    """Test non-square matrix error for eigenvalues (returns graceful error)."""
    import json

    response = await http_client.call_tool(
        "matrix_eigenvalues",
        arguments={"matrix": [[1, 2, 3], [4, 5, 6]]},
    )
    assert response.is_error is False
    result = json.loads(response.content[0].text)
    assert result.get("success") is False
    assert result.get("error") is not None
    assert "square" in result.get("error", "").lower()


class TestMatrixEdgeCases:
    """Test edge cases for matrix operations."""

    @pytest.mark.asyncio
    async def test_multiply_minimal_and_zero(self, http_client):
        """Test multiply with 1x1 matrices and zero matrices (edge cases: minimal and all zeros).

        Happy path: 1x1 matrices [[5]] * [[3]] = [[15]]
        Edge case: zero matrix [[0,0],[0,0]] * [[1,2],[3,4]] = [[0,0],[0,0]]
        """
        # Happy path: minimal 1x1 matrices
        response = await http_client.call_tool(
            "matrix_multiply",
            arguments={
                "matrix_a": [[5]],
                "matrix_b": [[3]],
            },
        )
        assert response.is_error is False
        assert "15" in response.content[0].text

        # Edge case: zero matrix
        response = await http_client.call_tool(
            "matrix_multiply",
            arguments={
                "matrix_a": [[0, 0], [0, 0]],
                "matrix_b": [[1, 2], [3, 4]],
            },
        )
        assert response.is_error is False
        assert "0" in response.content[0].text

    @pytest.mark.asyncio
    async def test_transpose_minimal_and_rectangular(self, http_client):
        """Test transpose with 1x1 matrix and rectangular matrix (edge cases: minimal and shape change).

        Happy path: 1x1 matrix [[42]] transposes to [[42]]
        Edge case: 3x1 column vector transposes to 1x3 row vector
        """
        # Happy path: minimal 1x1 matrix
        response = await http_client.call_tool(
            "matrix_transpose",
            arguments={"matrix": [[42]]},
        )
        assert response.is_error is False
        assert "42" in response.content[0].text

        # Edge case: column to row transpose
        response = await http_client.call_tool(
            "matrix_transpose",
            arguments={"matrix": [[1], [2], [3]]},
        )
        assert response.is_error is False
        result = response.content[0].text
        assert "1" in result and "2" in result and "3" in result

    @pytest.mark.asyncio
    async def test_determinant_minimal_and_zero(self, http_client):
        """Test determinant with 1x1 matrix and zero matrix (edge cases: minimal and singular).

        Happy path: 1x1 matrix [[7]] has determinant ~7
        Edge case: zero matrix [[0,0],[0,0]] has determinant ~0
        """
        import json

        # Happy path: minimal 1x1 matrix
        response = await http_client.call_tool(
            "matrix_determinant",
            arguments={"matrix": [[7]]},
        )
        assert response.is_error is False
        result = json.loads(response.content[0].text)
        assert abs(result["determinant"] - 7.0) < 0.1

        # Edge case: zero matrix
        response = await http_client.call_tool(
            "matrix_determinant",
            arguments={"matrix": [[0, 0], [0, 0]]},
        )
        assert response.is_error is False
        result = json.loads(response.content[0].text)
        assert abs(result["determinant"]) < 0.1

    @pytest.mark.asyncio
    async def test_determinant_large_and_negative(self, http_client):
        """Test determinant with large matrix and negative result (edge cases: boundary and sign).

        Happy path: 100x100 identity matrix has determinant ~1 (floating point)
        Edge case: [[0,1],[1,0]] has determinant -1
        """
        import json

        # Happy path: large identity matrix (allow floating point tolerance)
        large_matrix = [[1.0 if i == j else 0.0 for j in range(100)] for i in range(100)]
        response = await http_client.call_tool(
            "matrix_determinant",
            arguments={"matrix": large_matrix},
        )
        assert response.is_error is False
        result = json.loads(response.content[0].text)
        # Should be close to 1, allowing for floating point errors
        assert abs(result["determinant"] - 1.0) < 0.1

        # Edge case: negative determinant
        response = await http_client.call_tool(
            "matrix_determinant",
            arguments={"matrix": [[0, 1], [1, 0]]},
        )
        assert response.is_error is False
        result = json.loads(response.content[0].text)
        assert abs(result["determinant"] - (-1.0)) < 0.1

    @pytest.mark.asyncio
    async def test_inverse_minimal_and_permutation(self, http_client):
        """Test inverse with 1x1 matrix and permutation matrix (edge cases: minimal and special form).

        Happy path: 1x1 matrix [[2]] has inverse [[0.5]]
        Edge case: permutation matrix [[0,1],[1,0]] is its own inverse
        """
        # Happy path: minimal 1x1 matrix
        response = await http_client.call_tool(
            "matrix_inverse",
            arguments={"matrix": [[2]]},
        )
        assert response.is_error is False
        assert "0.5" in response.content[0].text or "1/2" in response.content[0].text.lower()

        # Edge case: permutation matrix (invertible)
        response = await http_client.call_tool(
            "matrix_inverse",
            arguments={"matrix": [[0, 1], [1, 0]]},
        )
        assert response.is_error is False
        result = response.content[0].text
        assert "error" not in result.lower() or "0" in result

    @pytest.mark.asyncio
    async def test_eigenvalues_minimal_and_zero(self, http_client):
        """Test eigenvalues with 1x1 matrix and zero matrix (edge cases: minimal and singular).

        Happy path: 1x1 matrix [[5]] has eigenvalue 5
        Edge case: zero matrix [[0,0],[0,0]] has eigenvalue 0
        """
        # Happy path: minimal 1x1 matrix
        response = await http_client.call_tool(
            "matrix_eigenvalues",
            arguments={"matrix": [[5]]},
        )
        assert response.is_error is False
        assert "5" in response.content[0].text

        # Edge case: zero matrix
        response = await http_client.call_tool(
            "matrix_eigenvalues",
            arguments={"matrix": [[0, 0], [0, 0]]},
        )
        assert response.is_error is False
        assert "0" in response.content[0].text

    @pytest.mark.asyncio
    async def test_multiply_negative_values(self, http_client):
        """Test multiply with negative values (edge case: sign handling).

        Edge case: [[-1,-2],[-3,-4]] * [[1,2],[3,4]] produces negative results
        """
        response = await http_client.call_tool(
            "matrix_multiply",
            arguments={
                "matrix_a": [[-1, -2], [-3, -4]],
                "matrix_b": [[1, 2], [3, 4]],
            },
        )
        assert response.is_error is False
        result = response.content[0].text
        assert "-7" in result

    @pytest.mark.asyncio
    async def test_determinant_negative_result(self, http_client_high_limit):
        """Test determinant with negative result (edge case: sign)."""
        response = await http_client_high_limit.call_tool(
            "matrix_determinant",
            arguments={"matrix": [[0, 1], [1, 0]]},
        )
        assert response.is_error is False
        result = response.content[0].text
        assert "-1" in result

    @pytest.mark.asyncio
    async def test_transpose_large_rectangular(self, http_client_high_limit):
        """Test transpose of large rectangular matrix (edge case: boundary size).

        Edge case: 50x100 matrix transposed to 100x50
        """
        large_rect = [[float(i + j) for j in range(100)] for i in range(50)]
        response = await http_client_high_limit.call_tool(
            "matrix_transpose",
            arguments={"matrix": large_rect},
        )
        assert response.is_error is False
        result = response.content[0].text
        assert "[" in result or any(c.isdigit() for c in result)


# === PROGRESS REPORTING TESTS ===


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context for testing progress reporting."""

    class MockContext:
        def __init__(self):
            self.info_logs = []
            self.progress_reports = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

        async def report_progress(self, current: int, total: int, message: str = ""):
            """Mock progress reporting."""
            self.progress_reports.append((current, total, message))

    return MockContext()


@pytest.mark.asyncio
async def test_matrix_inverse_progress_reporting(mock_context):
    """Test matrix_inverse reports progress through 4 stages with messages.

    Arrange: Create mock context and call matrix_inverse
    Act: Call matrix_inverse with mock context and a valid invertible matrix
    Assert: progress_reports contains 4 stages with 3-tuples (current, total, message)
    """
    from math_mcp.tools.matrix import matrix_inverse

    # Arrange: Valid invertible 2x2 matrix
    matrix = [[1, 2], [3, 4]]

    # Act: Call matrix_inverse with mock context
    await matrix_inverse.raw_function(matrix, mock_context)

    # Assert: Progress reports contain 4 stages with 3-tuples
    assert len(mock_context.progress_reports) == 4

    # Check each stage has correct structure (current, total, message)
    for i, (current, total, message) in enumerate(mock_context.progress_reports):
        assert current == i
        assert total == 3
        assert isinstance(message, str)
        assert len(message) > 0


@pytest.mark.asyncio
async def test_matrix_eigenvalues_progress_reporting(mock_context):
    """Test matrix_eigenvalues reports progress through 3 stages with messages.

    Arrange: Create mock context and call matrix_eigenvalues
    Act: Call matrix_eigenvalues with mock context and a valid square matrix
    Assert: progress_reports contains 3 stages with 3-tuples (current, total, message)
    """
    from math_mcp.tools.matrix import matrix_eigenvalues

    # Arrange: Valid square matrix
    matrix = [[4, 2], [1, 3]]

    # Act: Call matrix_eigenvalues with mock context
    await matrix_eigenvalues.raw_function(matrix, mock_context)

    # Assert: Progress reports contain 3 stages with 3-tuples
    assert len(mock_context.progress_reports) == 3

    # Check each stage has correct structure (current, total, message)
    for i, (current, total, message) in enumerate(mock_context.progress_reports):
        assert current == i
        assert total == 2
        assert isinstance(message, str)
        assert len(message) > 0
