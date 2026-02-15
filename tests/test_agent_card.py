"""A2A v0.3 agent card endpoint tests.

Tests verify the agent card is correctly generated, served at the
well-known endpoint, and conforms to A2A v0.3 schema.
"""

from importlib.metadata import version as pkg_version

import httpx
import pytest


async def test_agent_card_endpoint_and_json_valid(http_server: str) -> None:
    """Test agent card endpoint is accessible and returns valid JSON."""
    async with httpx.AsyncClient() as client:
        agent_card_url = http_server.replace("/mcp", "") + "/.well-known/agent-card.json"
        response = await client.get(agent_card_url)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        # Verify JSON is valid by parsing
        card = response.json()
        assert isinstance(card, dict)


async def test_agent_card_has_required_fields(http_server: str) -> None:
    """Test agent card contains all required A2A v0.3 fields."""
    async with httpx.AsyncClient() as client:
        agent_card_url = http_server.replace("/mcp", "") + "/.well-known/agent-card.json"
        response = await client.get(agent_card_url)

        card = response.json()

        # Required fields per A2A v0.3 spec
        assert "protocolVersion" in card
        assert card["protocolVersion"] == "1.0"
        assert "name" in card
        assert card["name"] == "Math Learning Server"
        assert "description" in card
        assert len(card["description"]) > 0
        assert "version" in card
        assert "capabilities" in card
        assert "defaultInputModes" in card
        assert "defaultOutputModes" in card
        assert "skills" in card
        assert "documentationUrl" in card


async def test_agent_card_version_matches_package(http_server: str) -> None:
    """Test agent card version matches package metadata."""
    async with httpx.AsyncClient() as client:
        agent_card_url = http_server.replace("/mcp", "") + "/.well-known/agent-card.json"
        response = await client.get(agent_card_url)

        card = response.json()

        # Get version from package metadata
        expected_version = pkg_version("math-mcp-learning-server")
        assert card["version"] == expected_version


async def test_agent_card_camel_case_serialization(http_server: str) -> None:
    """Test agent card uses camelCase JSON serialization per A2A spec."""
    async with httpx.AsyncClient() as client:
        agent_card_url = http_server.replace("/mcp", "") + "/.well-known/agent-card.json"
        response = await client.get(agent_card_url)

        card = response.json()

        # A2A spec requires camelCase in JSON
        assert "protocolVersion" in card
        assert "defaultInputModes" in card
        assert "defaultOutputModes" in card
        assert "documentationUrl" in card

        # Should NOT have snake_case versions
        assert "protocol_version" not in card
        assert "default_input_modes" not in card
        assert "default_output_modes" not in card


async def test_agent_card_capabilities_and_modes(http_server: str) -> None:
    """Test agent card capabilities structure and input/output modes."""
    async with httpx.AsyncClient() as client:
        agent_card_url = http_server.replace("/mcp", "") + "/.well-known/agent-card.json"
        response = await client.get(agent_card_url)

        card = response.json()

        # Verify capabilities structure
        capabilities = card["capabilities"]
        assert isinstance(capabilities, dict)
        assert "streaming" in capabilities
        assert "pushNotifications" in capabilities
        assert "stateTransitionHistory" in capabilities

        # Verify input/output modes
        assert isinstance(card["defaultInputModes"], list)
        assert len(card["defaultInputModes"]) > 0
        assert isinstance(card["defaultOutputModes"], list)
        assert len(card["defaultOutputModes"]) > 0


async def test_agent_card_skills_structure(http_server: str) -> None:
    """Test agent card skills have correct structure and include registered tools."""
    async with httpx.AsyncClient() as client:
        agent_card_url = http_server.replace("/mcp", "") + "/.well-known/agent-card.json"
        response = await client.get(agent_card_url)

        card = response.json()
        skills = card["skills"]

        # Skills should not be empty
        assert isinstance(skills, list)
        assert len(skills) > 0

        # Verify skill structure
        for skill in skills:
            assert "id" in skill
            assert "name" in skill
            assert "description" in skill
            assert "tags" in skill
            assert isinstance(skill["tags"], list)
            assert "mcp" in skill["tags"]
            assert "tool" in skill["tags"]
            assert "inputModes" in skill
            assert "outputModes" in skill

        # Verify key tools are present
        skill_ids = [skill["id"] for skill in skills]
        assert "calculate" in skill_ids
        assert "statistics" in skill_ids


async def test_agent_card_consistency_across_requests(http_server: str) -> None:
    """Test agent card is consistent across multiple requests."""
    async with httpx.AsyncClient() as client:
        agent_card_url = http_server.replace("/mcp", "") + "/.well-known/agent-card.json"

        # Make two requests
        response1 = await client.get(agent_card_url)
        response2 = await client.get(agent_card_url)

        card1 = response1.json()
        card2 = response2.json()

        # Should be identical
        assert card1 == card2
