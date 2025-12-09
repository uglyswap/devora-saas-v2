"""
Templates de réponses structurées pour l'orchestration Devora.

Fournit des schémas et validateurs pour les réponses des agents.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime


class ResponseStatus(Enum):
    """Statuts possibles des réponses."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"
    PENDING = "pending"


class TaskType(Enum):
    """Types de tâches."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    PLANNING = "planning"
    COORDINATION = "coordination"


class Severity(Enum):
    """Niveaux de sévérité."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Metadata:
    """Métadonnées communes à toutes les réponses."""
    agent_id: str
    agent_type: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time: float = 0.0
    tokens_used: int = 0
    model_used: Optional[str] = None
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class Issue:
    """Représente un problème ou une erreur."""
    issue: str
    severity: Severity
    location: Optional[str] = None
    suggestion: Optional[str] = None
    error_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "issue": self.issue,
            "severity": self.severity.value,
            "location": self.location,
            "suggestion": self.suggestion,
            "error_code": self.error_code,
        }


@dataclass
class Task:
    """Représente une tâche planifiée."""
    id: str
    description: str
    type: TaskType
    priority: int
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: Optional[str] = None
    resources_needed: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            **asdict(self),
            "type": self.type.value,
        }


@dataclass
class BaseResponse:
    """Classe de base pour toutes les réponses."""
    status: ResponseStatus
    metadata: Metadata
    data: Dict[str, Any] = field(default_factory=dict)
    issues: List[Issue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la réponse en dictionnaire."""
        return {
            "status": self.status.value,
            "metadata": self.metadata.to_dict(),
            "data": self.data,
            "issues": [issue.to_dict() for issue in self.issues],
            "warnings": self.warnings,
        }

    def is_success(self) -> bool:
        """Vérifie si la réponse est un succès."""
        return self.status == ResponseStatus.SUCCESS

    def has_errors(self) -> bool:
        """Vérifie si la réponse contient des erreurs."""
        return any(issue.severity in [Severity.CRITICAL, Severity.HIGH] for issue in self.issues)


@dataclass
class RouterResponse(BaseResponse):
    """Réponse de l'agent Router."""
    intent: str = ""
    complexity: str = "medium"
    workflow: str = ""
    required_agents: List[str] = field(default_factory=list)
    estimated_steps: int = 0
    reasoning: str = ""
    execution_plan: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        base = super().to_dict()
        base["data"].update({
            "intent": self.intent,
            "complexity": self.complexity,
            "workflow": self.workflow,
            "required_agents": self.required_agents,
            "estimated_steps": self.estimated_steps,
            "reasoning": self.reasoning,
            "execution_plan": self.execution_plan,
        })
        return base


@dataclass
class PlannerResponse(BaseResponse):
    """Réponse de l'agent Planner."""
    tasks: List[Task] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    parallel_tasks: List[List[str]] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    total_estimated_duration: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        base = super().to_dict()
        base["data"].update({
            "tasks": [task.to_dict() for task in self.tasks],
            "execution_order": self.execution_order,
            "parallel_tasks": self.parallel_tasks,
            "milestones": self.milestones,
            "total_estimated_duration": self.total_estimated_duration,
        })
        return base


@dataclass
class Finding:
    """Représente une découverte de recherche."""
    key_point: str
    details: str
    source: str
    confidence: float
    supporting_evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class ResearcherResponse(BaseResponse):
    """Réponse de l'agent Researcher."""
    summary: str = ""
    findings: List[Finding] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    sources_consulted: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        base = super().to_dict()
        base["data"].update({
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "insights": self.insights,
            "gaps": self.gaps,
            "recommendations": self.recommendations,
            "sources_consulted": self.sources_consulted,
        })
        return base


@dataclass
class Metric:
    """Représente une métrique d'analyse."""
    value: float
    unit: str
    trend: str = "stable"
    significance: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class Pattern:
    """Représente un pattern détecté."""
    pattern: str
    frequency: float
    significance: str
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class Recommendation:
    """Représente une recommandation."""
    recommendation: str
    priority: int
    expected_impact: str
    confidence: float
    implementation_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class AnalystResponse(BaseResponse):
    """Réponse de l'agent Analyst."""
    analysis_summary: str = ""
    metrics: Dict[str, Metric] = field(default_factory=dict)
    patterns: List[Pattern] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        base = super().to_dict()
        base["data"].update({
            "analysis_summary": self.analysis_summary,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "patterns": [pattern.to_dict() for pattern in self.patterns],
            "anomalies": self.anomalies,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
        })
        return base


@dataclass
class FileOutput:
    """Représente un fichier généré."""
    path: str
    content: str
    language: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class Implementation:
    """Représente une implémentation."""
    type: str
    content: str
    language: Optional[str] = None
    files: List[FileOutput] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "type": self.type,
            "content": self.content,
            "language": self.language,
            "files": [f.to_dict() for f in self.files],
        }


@dataclass
class ImplementerResponse(BaseResponse):
    """Réponse de l'agent Implementer."""
    implementation: Optional[Implementation] = None
    testing: Dict[str, Any] = field(default_factory=dict)
    documentation: Dict[str, Any] = field(default_factory=dict)
    quality_checks: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        base = super().to_dict()
        base["data"].update({
            "implementation": self.implementation.to_dict() if self.implementation else None,
            "testing": self.testing,
            "documentation": self.documentation,
            "quality_checks": self.quality_checks,
        })
        return base


@dataclass
class ValidationCheck:
    """Représente une vérification de validation."""
    check: str
    status: str
    details: str
    severity: Severity

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            **asdict(self),
            "severity": self.severity.value,
        }


@dataclass
class QualityMetrics:
    """Métriques de qualité."""
    completeness: float = 0.0
    correctness: float = 0.0
    clarity: float = 0.0
    efficiency: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)

    def overall_score(self) -> float:
        """Calcule le score global."""
        return (self.completeness + self.correctness + self.clarity + self.efficiency) / 4


@dataclass
class ValidatorResponse(BaseResponse):
    """Réponse de l'agent Validator."""
    validation_result: str = "pending"
    overall_score: float = 0.0
    checks: List[ValidationCheck] = field(default_factory=list)
    quality_metrics: Optional[QualityMetrics] = None
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        base = super().to_dict()
        base["data"].update({
            "validation_result": self.validation_result,
            "overall_score": self.overall_score,
            "checks": [check.to_dict() for check in self.checks],
            "quality_metrics": self.quality_metrics.to_dict() if self.quality_metrics else None,
            "recommendations": self.recommendations,
        })
        return base


@dataclass
class AgentAction:
    """Représente une action d'agent à effectuer."""
    agent: str
    action: str
    priority: int
    input: Dict[str, Any]
    timeout: Optional[str] = None
    status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class OrchestratorResponse(BaseResponse):
    """Réponse de l'agent Orchestrator."""
    next_actions: List[AgentAction] = field(default_factory=list)
    resource_allocation: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)
    workflow_progress: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        base = super().to_dict()
        base["data"].update({
            "next_actions": [action.to_dict() for action in self.next_actions],
            "resource_allocation": self.resource_allocation,
            "monitoring": self.monitoring,
            "workflow_progress": self.workflow_progress,
        })
        return base


@dataclass
class ErrorResponse(BaseResponse):
    """Réponse d'erreur standardisée."""
    error_message: str = ""
    error_type: str = ""
    error_code: str = ""
    traceback: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Force le status à ERROR."""
        self.status = ResponseStatus.ERROR

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        base = super().to_dict()
        base["data"].update({
            "error_message": self.error_message,
            "error_type": self.error_type,
            "error_code": self.error_code,
            "traceback": self.traceback,
            "recovery_suggestions": self.recovery_suggestions,
        })
        return base


def create_success_response(
    agent_id: str,
    agent_type: str,
    data: Dict[str, Any],
    execution_time: float = 0.0,
    tokens_used: int = 0,
) -> BaseResponse:
    """
    Crée une réponse de succès standardisée.

    Args:
        agent_id: ID de l'agent
        agent_type: Type de l'agent
        data: Données de la réponse
        execution_time: Temps d'exécution
        tokens_used: Tokens utilisés

    Returns:
        BaseResponse avec status SUCCESS
    """
    metadata = Metadata(
        agent_id=agent_id,
        agent_type=agent_type,
        execution_time=execution_time,
        tokens_used=tokens_used,
    )

    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        metadata=metadata,
        data=data,
    )


def create_error_response(
    agent_id: str,
    agent_type: str,
    error_message: str,
    error_type: str = "UnknownError",
    error_code: str = "ERR_UNKNOWN",
    traceback: Optional[str] = None,
    recovery_suggestions: Optional[List[str]] = None,
) -> ErrorResponse:
    """
    Crée une réponse d'erreur standardisée.

    Args:
        agent_id: ID de l'agent
        agent_type: Type de l'agent
        error_message: Message d'erreur
        error_type: Type d'erreur
        error_code: Code d'erreur
        traceback: Traceback optionnel
        recovery_suggestions: Suggestions de récupération

    Returns:
        ErrorResponse
    """
    metadata = Metadata(agent_id=agent_id, agent_type=agent_type)

    return ErrorResponse(
        status=ResponseStatus.ERROR,
        metadata=metadata,
        error_message=error_message,
        error_type=error_type,
        error_code=error_code,
        traceback=traceback,
        recovery_suggestions=recovery_suggestions or [],
    )


def validate_response_schema(response: Dict[str, Any], expected_fields: List[str]) -> List[str]:
    """
    Valide qu'une réponse contient tous les champs attendus.

    Args:
        response: Réponse à valider
        expected_fields: Liste des champs requis

    Returns:
        Liste des champs manquants
    """
    missing = []
    for field in expected_fields:
        if "." in field:
            # Champ imbriqué
            parts = field.split(".")
            current = response
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    missing.append(field)
                    break
        else:
            if field not in response:
                missing.append(field)

    return missing
