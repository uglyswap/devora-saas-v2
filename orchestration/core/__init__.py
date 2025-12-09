"""
Devora Orchestration Core Module

This module provides the core components for the Devora transformation
orchestration system, including:
- Base Agent classes and configurations
- Orchestrator Ultimate (28 agents, 10 squads)
- Squad Manager (squad coordination)
- Workflow Engine (10 predefined workflows)
- Quality Gate Engine (automated quality checks)
"""

from .base_agent import (
    BaseAgent,
    AgentConfig,
    AgentMetrics,
    AgentStatus
)

from .orchestrator_ultimate import (
    OrchestratorUltimate,
    OrchestratorRequest,
    OrchestratorResult,
    ExecutionMode
)

from .squad_manager import (
    SquadManager,
    Squad,
    SquadType
)

from .workflow_engine import (
    WorkflowEngine,
    Workflow,
    WorkflowStep,
    WorkflowStepType
)

from .quality_gate_engine import (
    QualityGateEngine,
    QualityCheck,
    CheckResult,
    QualityReport,
    CheckStatus,
    CheckSeverity
)

__all__ = [
    # Base Agent
    "BaseAgent",
    "AgentConfig",
    "AgentMetrics",
    "AgentStatus",

    # Orchestrator
    "OrchestratorUltimate",
    "OrchestratorRequest",
    "OrchestratorResult",
    "ExecutionMode",

    # Squad Manager
    "SquadManager",
    "Squad",
    "SquadType",

    # Workflow Engine
    "WorkflowEngine",
    "Workflow",
    "WorkflowStep",
    "WorkflowStepType",

    # Quality Gate
    "QualityGateEngine",
    "QualityCheck",
    "CheckResult",
    "QualityReport",
    "CheckStatus",
    "CheckSeverity"
]

__version__ = "1.0.0"
