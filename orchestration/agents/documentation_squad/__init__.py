"""
Documentation Squad - Professional Technical and API Documentation

This squad provides comprehensive documentation generation capabilities
for the Devora transformation orchestration system.

Available Agents:
    - TechnicalWriterAgent: Generates README, ADRs, installation guides, architecture docs
    - APIDocumenterAgent: Creates OpenAPI specs, Postman collections, SDK docs

Squad Capabilities:
    - Technical documentation (README, ADR, architecture, installation, changelog)
    - API documentation (OpenAPI/Swagger, Postman, integration guides)
    - Multi-language SDK documentation
    - Code examples and use cases
    - Mermaid diagrams and visual documentation
    - Authentication flow documentation
    - Error handling and troubleshooting guides
"""

from .technical_writer import TechnicalWriterAgent
from .api_documenter import APIDocumenterAgent

__all__ = [
    "TechnicalWriterAgent",
    "APIDocumenterAgent"
]

# Squad metadata
SQUAD_NAME = "Documentation Squad"
SQUAD_DESCRIPTION = """
The Documentation Squad provides world-class documentation generation
for technical projects, APIs, and developer tools.

Core Responsibilities:
- Technical documentation: README files, ADRs, architecture docs, installation guides
- API documentation: OpenAPI/Swagger specs, Postman collections, integration guides
- SDK documentation: Multi-language examples and usage guides
- Developer experience: Code examples, troubleshooting, best practices

Standards Followed:
- Keep a Changelog for changelog formatting
- Semantic Versioning for version numbers
- OpenAPI 3.0+ specification for API docs
- Postman Collection v2.1 format
- MADR (Markdown Any Decision Records) for ADRs
- README best practices with shields/badges
"""

SQUAD_AGENTS = {
    "technical_writer": {
        "class": TechnicalWriterAgent,
        "name": "Technical Writer",
        "description": "Generates comprehensive technical documentation",
        "capabilities": [
            "Professional README generation with badges and examples",
            "Architecture Decision Records (ADRs) following MADR format",
            "Multi-platform installation guides (macOS, Linux, Windows)",
            "System architecture documentation with Mermaid diagrams",
            "Changelog generation following Keep a Changelog",
            "Troubleshooting guides and FAQ sections",
            "Contributing guidelines and code of conduct"
        ],
        "output_formats": [
            "README.md with Table of Contents",
            "ADR documents in docs/adr/",
            "INSTALLATION.md with platform-specific instructions",
            "ARCHITECTURE.md with Mermaid diagrams",
            "CHANGELOG.md following standard format"
        ]
    },
    "api_documenter": {
        "class": APIDocumenterAgent,
        "name": "API Documenter",
        "description": "Creates comprehensive API documentation and specifications",
        "capabilities": [
            "OpenAPI 3.0+ specification generation",
            "Postman Collection v2.1 creation with examples",
            "GraphQL schema documentation",
            "Multi-language integration guides (JavaScript, Python, Go, cURL)",
            "SDK documentation with code examples",
            "Authentication flow documentation (OAuth2, JWT, API Keys)",
            "Rate limiting and error handling documentation",
            "Webhook and event-driven API documentation"
        ],
        "output_formats": [
            "OpenAPI YAML/JSON specification files",
            "Postman Collection JSON (importable)",
            "Integration guide markdown",
            "SDK documentation for specific languages",
            "GraphQL schema documentation"
        ]
    }
}


def get_squad_info() -> dict:
    """
    Get comprehensive information about the Documentation Squad.

    Returns:
        Dictionary containing squad metadata, agents, and capabilities
    """
    return {
        "name": SQUAD_NAME,
        "description": SQUAD_DESCRIPTION,
        "agent_count": len(SQUAD_AGENTS),
        "agents": list(SQUAD_AGENTS.keys()),
        "agent_details": SQUAD_AGENTS,
        "use_cases": [
            "Generate README for new projects",
            "Document architectural decisions with ADRs",
            "Create installation guides for complex setups",
            "Generate OpenAPI specs from API definitions",
            "Create Postman collections for API testing",
            "Write integration guides for API consumers",
            "Generate SDK documentation for multiple languages",
            "Document changelog following standard format"
        ]
    }


def list_agents() -> list:
    """
    List all available agents in the Documentation Squad.

    Returns:
        List of agent names
    """
    return list(SQUAD_AGENTS.keys())


def get_agent_class(agent_name: str):
    """
    Get agent class by name.

    Args:
        agent_name: Name of the agent ('technical_writer' or 'api_documenter')

    Returns:
        Agent class

    Raises:
        ValueError: If agent name is invalid
    """
    if agent_name not in SQUAD_AGENTS:
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Available agents: {', '.join(SQUAD_AGENTS.keys())}"
        )

    return SQUAD_AGENTS[agent_name]["class"]


def get_agent_capabilities(agent_name: str) -> list:
    """
    Get capabilities of a specific agent.

    Args:
        agent_name: Name of the agent

    Returns:
        List of agent capabilities

    Raises:
        ValueError: If agent name is invalid
    """
    if agent_name not in SQUAD_AGENTS:
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Available agents: {', '.join(SQUAD_AGENTS.keys())}"
        )

    return SQUAD_AGENTS[agent_name]["capabilities"]


# Quick access functions for common documentation tasks

async def generate_readme(api_key: str, project_name: str, project_description: str, tech_stack: list, **kwargs):
    """
    Quick helper to generate a README file.

    Args:
        api_key: OpenRouter API key
        project_name: Name of the project
        project_description: Brief description
        tech_stack: List of technologies
        **kwargs: Additional parameters (features, audience, etc.)

    Returns:
        Result dictionary with README content
    """
    writer = TechnicalWriterAgent(api_key=api_key)
    return await writer.generate_readme(
        project_name=project_name,
        project_description=project_description,
        tech_stack=tech_stack,
        features=kwargs.get("features")
    )


async def generate_api_docs(api_key: str, api_name: str, base_url: str, endpoints: list, **kwargs):
    """
    Quick helper to generate OpenAPI specification.

    Args:
        api_key: OpenRouter API key
        api_name: Name of the API
        base_url: Base URL
        endpoints: List of endpoint definitions
        **kwargs: Additional parameters (auth_type, version, etc.)

    Returns:
        Result dictionary with OpenAPI spec
    """
    documenter = APIDocumenterAgent(api_key=api_key)
    return await documenter.generate_openapi_spec(
        api_name=api_name,
        base_url=base_url,
        endpoints=endpoints,
        auth_type=kwargs.get("auth_type", "bearer"),
        version=kwargs.get("version", "1.0.0")
    )


async def generate_integration_guide(api_key: str, api_name: str, base_url: str, endpoints: list, **kwargs):
    """
    Quick helper to generate API integration guide.

    Args:
        api_key: OpenRouter API key
        api_name: Name of the API
        base_url: Base URL
        endpoints: List of endpoint definitions
        **kwargs: Additional parameters (auth_type, etc.)

    Returns:
        Result dictionary with integration guide
    """
    documenter = APIDocumenterAgent(api_key=api_key)
    return await documenter.generate_integration_guide(
        api_name=api_name,
        base_url=base_url,
        endpoints=endpoints,
        auth_type=kwargs.get("auth_type", "bearer")
    )
