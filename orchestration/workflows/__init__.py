"""
Devora Orchestration Workflows

Ce module expose tous les workflows disponibles pour le système d'orchestration Devora.

Workflows disponibles:
- FeatureDevelopmentWorkflow: Développement de features complètes
- BugResolutionWorkflow: Résolution systématique de bugs
- SaasMvpWorkflow: Création de MVP SaaS de A à Z
- QualityGateWorkflow: Vérification qualité automatique
- MigrationWorkflow: Migrations sécurisées (database, framework, infrastructure)
- RefactoringWorkflow: Refactoring systématique
- PerformanceAuditWorkflow: Audit de performance complet
- ScalingWorkflow: Préparation au scaling
- IncidentResponseWorkflow: Réponse aux incidents critiques
- ReleaseManagementWorkflow: Gestion des releases

Usage:
    from orchestration.workflows import FeatureDevelopmentWorkflow

    workflow = FeatureDevelopmentWorkflow()
    result = await workflow.execute(context, orchestrator)
"""

from .feature_development import FeatureDevelopmentWorkflow
from .bug_resolution import BugResolutionWorkflow
from .saas_mvp import SaasMvpWorkflow
from .quality_gate import QualityGateWorkflow
from .migration import MigrationWorkflow
from .refactoring import RefactoringWorkflow
from .performance_audit import PerformanceAuditWorkflow
from .scaling import ScalingWorkflow
from .incident_response import IncidentResponseWorkflow
from .release_management import ReleaseManagementWorkflow


__all__ = [
    "FeatureDevelopmentWorkflow",
    "BugResolutionWorkflow",
    "SaasMvpWorkflow",
    "QualityGateWorkflow",
    "MigrationWorkflow",
    "RefactoringWorkflow",
    "PerformanceAuditWorkflow",
    "ScalingWorkflow",
    "IncidentResponseWorkflow",
    "ReleaseManagementWorkflow",
]


# Registry des workflows disponibles
WORKFLOW_REGISTRY = {
    "feature_development": FeatureDevelopmentWorkflow,
    "bug_resolution": BugResolutionWorkflow,
    "saas_mvp": SaasMvpWorkflow,
    "quality_gate": QualityGateWorkflow,
    "migration": MigrationWorkflow,
    "refactoring": RefactoringWorkflow,
    "performance_audit": PerformanceAuditWorkflow,
    "scaling": ScalingWorkflow,
    "incident_response": IncidentResponseWorkflow,
    "release_management": ReleaseManagementWorkflow,
}


def get_workflow(workflow_name: str):
    """
    Récupère une classe de workflow par son nom.

    Args:
        workflow_name: Nom du workflow (ex: "feature_development")

    Returns:
        Classe du workflow correspondant

    Raises:
        ValueError: Si le workflow n'existe pas
    """
    if workflow_name not in WORKFLOW_REGISTRY:
        available = ", ".join(WORKFLOW_REGISTRY.keys())
        raise ValueError(
            f"Workflow '{workflow_name}' not found. "
            f"Available workflows: {available}"
        )

    return WORKFLOW_REGISTRY[workflow_name]


def list_workflows():
    """
    Liste tous les workflows disponibles.

    Returns:
        Liste des noms de workflows disponibles
    """
    return list(WORKFLOW_REGISTRY.keys())


def get_workflow_info(workflow_name: str):
    """
    Récupère les informations sur un workflow.

    Args:
        workflow_name: Nom du workflow

    Returns:
        Dictionnaire avec les informations du workflow
    """
    workflow_class = get_workflow(workflow_name)
    workflow_instance = workflow_class()

    return {
        "name": workflow_instance.name,
        "description": workflow_instance.description,
        "steps": workflow_instance.steps,
        "required_squads": workflow_instance.required_squads
    }
