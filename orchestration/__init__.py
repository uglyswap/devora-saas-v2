"""
Devora Orchestration System - Ultimate Edition
==============================================

A powerful multi-agent orchestration system with 28 specialized agents
organized into 10 squads, supporting 10 predefined workflows.

Architecture:
    - 10 Squads (Frontend, Backend, Data, Business, DevOps, QA, Performance,
                 Documentation, Accessibility, AI/ML)
    - 28 Specialized Agents
    - 10 Workflows (Feature Dev, Bug Fix, SaaS MVP, Quality Gate, Migration,
                    Refactoring, Performance Audit, Scaling, Incident Response,
                    Release Management)
    - Automatic Quality Gate with auto-fix capability

Usage:
    from orchestration import OrchestratorUltimate

    orchestrator = OrchestratorUltimate(
        api_key="your-openrouter-key",
        model="anthropic/claude-3.5-sonnet"
    )

    result = await orchestrator.execute(
        request="Build a landing page with contact form",
        workflow="feature_development"
    )

Author: Devora Team
Version: 2.0.0 (Ultimate Edition)
"""

__version__ = "2.0.0"
__author__ = "Devora Team"
__license__ = "MIT"

# Core components
from .core.base_agent import BaseAgent, AgentConfig, AgentMetrics, AgentStatus

# Squads will be imported after they are created
SQUADS = [
    "frontend_squad",
    "backend_squad",
    "data_squad",
    "business_squad",
    "devops_squad",
    "qa_squad",
    "performance_squad",
    "documentation_squad",
    "accessibility_squad",
    "ai_ml_squad"
]

WORKFLOWS = [
    "feature_development",
    "bug_resolution",
    "saas_mvp",
    "quality_gate",
    "migration",
    "refactoring",
    "performance_audit",
    "scaling",
    "incident_response",
    "release_management"
]

TOTAL_AGENTS = 28

__all__ = [
    # Version info
    "__version__",
    "__author__",

    # Core
    "BaseAgent",
    "AgentConfig",
    "AgentMetrics",
    "AgentStatus",

    # Constants
    "SQUADS",
    "WORKFLOWS",
    "TOTAL_AGENTS",
]
