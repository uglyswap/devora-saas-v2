"""
Devora Orchestration - Agents Registry
=======================================

Central registry for all 28 specialized agents organized into 10 squads.

Squads:
    1. Frontend Squad (3 agents)
    2. Backend Squad (3 agents)
    3. Data Squad (3 agents)
    4. Business Squad (5 agents)
    5. DevOps Squad (3 agents)
    6. QA Squad (2 agents)
    7. Performance Squad (3 agents)
    8. Documentation Squad (2 agents)
    9. Accessibility Squad (2 agents)
    10. AI/ML Squad (2 agents)

Total: 28 agents
"""

from typing import Dict, Type, List
from ..core.base_agent import BaseAgent

# Agent registry - will be populated as agents are imported
_AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {}

# Squad to agents mapping
SQUAD_AGENTS: Dict[str, List[str]] = {
    "frontend_squad": [
        "ui_ux_designer",
        "frontend_developer",
        "component_architect"
    ],
    "backend_squad": [
        "api_architect",
        "backend_developer",
        "integration_specialist"
    ],
    "data_squad": [
        "database_architect",
        "analytics_engineer",
        "search_rag_specialist"
    ],
    "business_squad": [
        "product_manager",
        "copywriter",
        "pricing_strategist",
        "compliance_officer",
        "growth_engineer"
    ],
    "devops_squad": [
        "infrastructure_engineer",
        "security_engineer",
        "monitoring_engineer"
    ],
    "qa_squad": [
        "test_engineer",
        "code_reviewer"
    ],
    "performance_squad": [
        "performance_engineer",
        "bundle_optimizer",
        "database_optimizer"
    ],
    "documentation_squad": [
        "technical_writer",
        "api_documenter"
    ],
    "accessibility_squad": [
        "accessibility_expert",
        "i18n_specialist"
    ],
    "ai_ml_squad": [
        "ai_engineer",
        "ml_ops_engineer"
    ]
}


def register_agent(name: str, agent_class: Type[BaseAgent]) -> None:
    """Register an agent in the global registry."""
    _AGENT_REGISTRY[name] = agent_class


def get_agent(name: str) -> Type[BaseAgent]:
    """Get an agent class by name."""
    if name not in _AGENT_REGISTRY:
        raise KeyError(f"Agent '{name}' not found in registry")
    return _AGENT_REGISTRY[name]


def get_squad_agents(squad_name: str) -> List[str]:
    """Get list of agent names for a squad."""
    if squad_name not in SQUAD_AGENTS:
        raise KeyError(f"Squad '{squad_name}' not found")
    return SQUAD_AGENTS[squad_name]


def get_all_agents() -> Dict[str, Type[BaseAgent]]:
    """Get all registered agents."""
    return _AGENT_REGISTRY.copy()


def list_squads() -> List[str]:
    """List all available squads."""
    return list(SQUAD_AGENTS.keys())


def list_agents() -> List[str]:
    """List all registered agent names."""
    return list(_AGENT_REGISTRY.keys())


def get_agent_count() -> int:
    """Get total number of registered agents."""
    return len(_AGENT_REGISTRY)


# Import all squad agents (will fail gracefully if not yet created)
try:
    from .frontend_squad import *
except ImportError:
    pass

try:
    from .backend_squad import *
except ImportError:
    pass

try:
    from .data_squad import *
except ImportError:
    pass

try:
    from .business_squad import *
except ImportError:
    pass

try:
    from .devops_squad import *
except ImportError:
    pass

try:
    from .qa_squad import *
except ImportError:
    pass

try:
    from .performance_squad import *
except ImportError:
    pass

try:
    from .documentation_squad import *
except ImportError:
    pass

try:
    from .accessibility_squad import *
except ImportError:
    pass

try:
    from .ai_ml_squad import *
except ImportError:
    pass


__all__ = [
    # Registry functions
    "register_agent",
    "get_agent",
    "get_squad_agents",
    "get_all_agents",
    "list_squads",
    "list_agents",
    "get_agent_count",

    # Constants
    "SQUAD_AGENTS",
]
