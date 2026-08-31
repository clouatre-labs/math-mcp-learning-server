"""A2A v0.3 Agent Card schema models for MCP server discovery.

This module implements the Agent-to-Agent (A2A) v0.3 specification for
agent discovery and capability advertisement. The agent card is served
at /.well-known/agent-card.json and enables other agents to discover
and understand this server's capabilities.

Reference: https://modelcontextprotocol.io/
"""

from pydantic import BaseModel, ConfigDict, Field


class AgentCapabilities(BaseModel):
    """Agent capabilities advertisement.

    Describes optional capabilities the agent supports beyond basic
    tool invocation. All fields are optional.
    """

    model_config = ConfigDict(populate_by_name=True)

    streaming: bool | None = Field(
        default=None,
        description="Whether the agent supports streaming responses",
    )
    push_notifications: bool | None = Field(
        default=None,
        alias="pushNotifications",
        description="Whether the agent supports push notifications",
    )
    state_transition_history: bool | None = Field(
        default=None,
        alias="stateTransitionHistory",
        description="Whether the agent maintains state transition history",
    )
    extensions: list[str] | None = Field(
        default=None,
        description="List of supported protocol extensions",
    )


class AgentSkill(BaseModel):
    """A skill or capability the agent can perform.

    Skills represent discrete, invocable capabilities. Each skill maps
    to an MCP tool with metadata for discovery and understanding.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(
        ...,
        description="Unique identifier for the skill",
    )
    name: str = Field(
        ...,
        description="Human-readable skill name",
    )
    description: str = Field(
        ...,
        description="Detailed description of what the skill does",
    )
    tags: list[str] = Field(
        ...,
        description="Tags for categorization and discovery",
    )
    examples: list[str] | None = Field(
        default=None,
        description="Example use cases or invocations",
    )
    input_modes: list[str] | None = Field(
        default=None,
        alias="inputModes",
        description="Supported input media types",
    )
    output_modes: list[str] | None = Field(
        default=None,
        alias="outputModes",
        description="Supported output media types",
    )


class AgentInterface(BaseModel):
    """Interface for communicating with the agent.

    Specifies how to connect to and communicate with this agent,
    including the protocol binding used.
    """

    model_config = ConfigDict(populate_by_name=True)

    url: str = Field(
        ...,
        description="URL where the agent can be reached",
    )
    protocol_binding: str = Field(
        ...,
        alias="protocolBinding",
        description="Protocol binding (e.g., 'HTTP+JSON')",
    )


class AgentProvider(BaseModel):
    """Information about the agent's provider/organization.

    Identifies who created and maintains this agent.
    """

    organization: str = Field(
        ...,
        description="Organization name",
    )
    url: str | None = Field(
        default=None,
        description="Organization website URL",
    )


class AgentCard(BaseModel):
    """A2A v0.3 Agent Card for MCP server discovery.

    The agent card is the primary discovery mechanism for agents.
    It describes the agent's capabilities, skills, and how to interact
    with it. Served at /.well-known/agent-card.json per A2A spec.

    Reference: https://modelcontextprotocol.io/
    """

    model_config = ConfigDict(populate_by_name=True)

    protocol_version: str = Field(
        default="0.3.0",
        alias="protocolVersion",
        description="A2A protocol version",
    )
    name: str = Field(
        ...,
        description="Agent name",
    )
    description: str = Field(
        ...,
        description="Agent description",
    )
    version: str = Field(
        ...,
        description="Agent version",
    )
    capabilities: AgentCapabilities = Field(
        ...,
        description="Agent capabilities",
    )
    default_input_modes: list[str] = Field(
        ...,
        alias="defaultInputModes",
        description="Default input media types",
    )
    default_output_modes: list[str] = Field(
        ...,
        alias="defaultOutputModes",
        description="Default output media types",
    )
    skills: list[AgentSkill] = Field(
        ...,
        description="List of skills the agent can perform",
    )
    supported_interfaces: list[AgentInterface] | None = Field(
        default=None,
        alias="supportedInterfaces",
        description="Interfaces for communicating with the agent",
    )
    provider: AgentProvider | None = Field(
        default=None,
        description="Agent provider information",
    )
    documentation_url: str | None = Field(
        default=None,
        alias="documentationUrl",
        description="URL to agent documentation",
    )
    icon_url: str | None = Field(
        default=None,
        alias="iconUrl",
        description="URL to agent icon",
    )
    supports_extended_agent_card: bool | None = Field(
        default=None,
        alias="supportsExtendedAgentCard",
        description="Whether extended agent card is supported",
    )
