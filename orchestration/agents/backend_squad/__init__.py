"""
Backend Squad - Specialized agents for backend development.

This module exports all backend-focused agents:
- APIArchitect: API design and OpenAPI specification
- BackendDeveloper: Backend code implementation
- IntegrationSpecialist: Third-party integrations and webhooks

Usage:
    from orchestration.agents.backend_squad import (
        APIArchitect,
        BackendDeveloper,
        IntegrationSpecialist
    )

    # Initialize agents
    api_architect = APIArchitect(api_key="your-key")
    backend_dev = BackendDeveloper(api_key="your-key")
    integration_specialist = IntegrationSpecialist(api_key="your-key")

    # Execute tasks
    api_spec = await api_architect.execute({
        "requirements": [...],
        "data_models": [...],
        "api_type": "rest"
    })

    backend_code = await backend_dev.execute({
        "api_spec": api_spec,
        "framework": "fastapi",
        "database": "postgresql"
    })

    integrations = await integration_specialist.execute({
        "integrations": ["stripe", "sendgrid"],
        "framework": "fastapi"
    })
"""

from .api_architect import APIArchitect
from .backend_developer import BackendDeveloper
from .integration_specialist import IntegrationSpecialist

__all__ = [
    "APIArchitect",
    "BackendDeveloper",
    "IntegrationSpecialist",
]

__version__ = "1.0.0"

# Agent metadata
BACKEND_SQUAD_AGENTS = {
    "api_architect": {
        "class": APIArchitect,
        "description": "Designs REST/GraphQL APIs with OpenAPI documentation",
        "capabilities": [
            "API architecture design",
            "OpenAPI/Swagger specification generation",
            "Pydantic/Zod schema validation",
            "API versioning strategies",
            "GraphQL schema design",
        ],
    },
    "backend_developer": {
        "class": BackendDeveloper,
        "description": "Implements backend code with FastAPI or Next.js",
        "capabilities": [
            "FastAPI/Next.js API Routes implementation",
            "JWT and OAuth authentication",
            "Middleware development",
            "Background job processing",
            "Database query optimization",
        ],
    },
    "integration_specialist": {
        "class": IntegrationSpecialist,
        "description": "Manages third-party integrations and webhooks",
        "capabilities": [
            "Stripe payment integration",
            "OAuth provider configuration",
            "Webhook implementation (incoming/outgoing)",
            "Email service integration",
            "Cloud storage integration",
        ],
    },
}


def get_agent(agent_name: str, api_key: str, model: str = "openai/gpt-4o"):
    """Factory function to get an agent instance by name.

    Args:
        agent_name: Name of the agent ("api_architect", "backend_developer", "integration_specialist")
        api_key: OpenRouter API key
        model: LLM model to use (default: GPT-4o)

    Returns:
        Instance of the requested agent

    Raises:
        ValueError: If agent_name is not recognized

    Example:
        >>> agent = get_agent("api_architect", api_key="sk-...")
        >>> result = await agent.execute(task)
    """
    if agent_name not in BACKEND_SQUAD_AGENTS:
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Available agents: {', '.join(BACKEND_SQUAD_AGENTS.keys())}"
        )

    agent_class = BACKEND_SQUAD_AGENTS[agent_name]["class"]
    return agent_class(api_key=api_key, model=model)


def list_agents():
    """List all available Backend Squad agents with their capabilities.

    Returns:
        Dictionary of agent metadata

    Example:
        >>> agents = list_agents()
        >>> for name, info in agents.items():
        ...     print(f"{name}: {info['description']}")
    """
    return BACKEND_SQUAD_AGENTS.copy()
