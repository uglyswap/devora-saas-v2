"""
Templates pour l'orchestration Devora.

Fournit les prompts et schémas de réponses pour tous les agents.
"""

from .prompts import (
    SystemPrompts,
    RouterPrompts,
    PlannerPrompts,
    ResearcherPrompts,
    AnalystPrompts,
    ImplementerPrompts,
    ValidatorPrompts,
    OrchestratorPrompts,
    format_prompt,
    create_messages,
)

from .responses import (
    # Enums
    ResponseStatus,
    TaskType,
    Severity,
    # Base classes
    Metadata,
    Issue,
    Task,
    BaseResponse,
    ErrorResponse,
    # Specific responses
    RouterResponse,
    PlannerResponse,
    ResearcherResponse,
    AnalystResponse,
    ImplementerResponse,
    ValidatorResponse,
    OrchestratorResponse,
    # Data classes
    Finding,
    Metric,
    Pattern,
    Recommendation,
    FileOutput,
    Implementation,
    ValidationCheck,
    QualityMetrics,
    AgentAction,
    # Utility functions
    create_success_response,
    create_error_response,
    validate_response_schema,
)

__all__ = [
    # Prompts
    "SystemPrompts",
    "RouterPrompts",
    "PlannerPrompts",
    "ResearcherPrompts",
    "AnalystPrompts",
    "ImplementerPrompts",
    "ValidatorPrompts",
    "OrchestratorPrompts",
    "format_prompt",
    "create_messages",
    # Response Enums
    "ResponseStatus",
    "TaskType",
    "Severity",
    # Base Response Classes
    "Metadata",
    "Issue",
    "Task",
    "BaseResponse",
    "ErrorResponse",
    # Specific Responses
    "RouterResponse",
    "PlannerResponse",
    "ResearcherResponse",
    "AnalystResponse",
    "ImplementerResponse",
    "ValidatorResponse",
    "OrchestratorResponse",
    # Data Classes
    "Finding",
    "Metric",
    "Pattern",
    "Recommendation",
    "FileOutput",
    "Implementation",
    "ValidationCheck",
    "QualityMetrics",
    "AgentAction",
    # Utilities
    "create_success_response",
    "create_error_response",
    "validate_response_schema",
]

__version__ = "0.1.0"
