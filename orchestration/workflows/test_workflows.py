"""
Tests unitaires pour les workflows Devora

Tests basiques pour vérifier que les workflows sont correctement structurés.
"""

import pytest
from orchestration.workflows import (
    FeatureDevelopmentWorkflow,
    BugResolutionWorkflow,
    SaasMvpWorkflow,
    QualityGateWorkflow,
    MigrationWorkflow,
    RefactoringWorkflow,
    PerformanceAuditWorkflow,
    ScalingWorkflow,
    IncidentResponseWorkflow,
    ReleaseManagementWorkflow,
    get_workflow,
    list_workflows,
    get_workflow_info,
    WORKFLOW_REGISTRY
)


def test_workflow_registry_complete():
    """Vérifie que le registry contient tous les 10 workflows."""
    assert len(WORKFLOW_REGISTRY) == 10
    assert "feature_development" in WORKFLOW_REGISTRY
    assert "bug_resolution" in WORKFLOW_REGISTRY
    assert "saas_mvp" in WORKFLOW_REGISTRY
    assert "quality_gate" in WORKFLOW_REGISTRY
    assert "migration" in WORKFLOW_REGISTRY
    assert "refactoring" in WORKFLOW_REGISTRY
    assert "performance_audit" in WORKFLOW_REGISTRY
    assert "scaling" in WORKFLOW_REGISTRY
    assert "incident_response" in WORKFLOW_REGISTRY
    assert "release_management" in WORKFLOW_REGISTRY


def test_list_workflows():
    """Vérifie que list_workflows retourne tous les workflows."""
    workflows = list_workflows()
    assert len(workflows) == 10
    assert isinstance(workflows, list)


def test_get_workflow_valid():
    """Vérifie que get_workflow retourne la bonne classe."""
    WorkflowClass = get_workflow("feature_development")
    assert WorkflowClass == FeatureDevelopmentWorkflow


def test_get_workflow_invalid():
    """Vérifie que get_workflow lève une erreur pour un workflow inconnu."""
    with pytest.raises(ValueError) as exc_info:
        get_workflow("unknown_workflow")
    assert "not found" in str(exc_info.value)


def test_workflow_structure_feature_development():
    """Vérifie la structure du workflow Feature Development."""
    workflow = FeatureDevelopmentWorkflow()

    assert workflow.name == "feature_development"
    assert isinstance(workflow.description, str)
    assert len(workflow.description) > 0
    assert isinstance(workflow.steps, list)
    assert len(workflow.steps) == 7
    assert isinstance(workflow.required_squads, list)
    assert len(workflow.required_squads) == 4


def test_workflow_structure_bug_resolution():
    """Vérifie la structure du workflow Bug Resolution."""
    workflow = BugResolutionWorkflow()

    assert workflow.name == "bug_resolution"
    assert isinstance(workflow.steps, list)
    assert len(workflow.steps) == 5
    assert "reproduce" in workflow.steps
    assert "diagnose" in workflow.steps
    assert "fix" in workflow.steps


def test_workflow_structure_quality_gate():
    """Vérifie la structure du workflow Quality Gate."""
    workflow = QualityGateWorkflow()

    assert workflow.name == "quality_gate"
    assert workflow.auto_fix_enabled == True
    assert isinstance(workflow.steps, list)
    assert len(workflow.steps) == 5


def test_workflow_info():
    """Vérifie que get_workflow_info retourne les bonnes informations."""
    info = get_workflow_info("feature_development")

    assert isinstance(info, dict)
    assert "name" in info
    assert "description" in info
    assert "steps" in info
    assert "required_squads" in info
    assert info["name"] == "feature_development"


def test_all_workflows_have_execute_method():
    """Vérifie que tous les workflows ont une méthode execute."""
    for workflow_name in list_workflows():
        WorkflowClass = get_workflow(workflow_name)
        workflow = WorkflowClass()
        assert hasattr(workflow, "execute")
        assert callable(workflow.execute)


def test_all_workflows_have_run_step_method():
    """Vérifie que tous les workflows ont une méthode _run_step."""
    for workflow_name in list_workflows():
        WorkflowClass = get_workflow(workflow_name)
        workflow = WorkflowClass()
        assert hasattr(workflow, "_run_step")
        assert callable(workflow._run_step)


def test_feature_development_steps():
    """Vérifie les étapes du Feature Development workflow."""
    workflow = FeatureDevelopmentWorkflow()
    expected_steps = [
        "analyze",
        "plan",
        "design",
        "implement",
        "test",
        "review",
        "deploy"
    ]
    assert workflow.steps == expected_steps


def test_saas_mvp_steps():
    """Vérifie les étapes du SaaS MVP workflow."""
    workflow = SaasMvpWorkflow()
    expected_steps = [
        "requirements",
        "architecture",
        "database",
        "backend",
        "frontend",
        "deploy"
    ]
    assert workflow.steps == expected_steps


def test_incident_response_steps():
    """Vérifie les étapes de l'Incident Response workflow."""
    workflow = IncidentResponseWorkflow()
    expected_steps = [
        "detect",
        "assess",
        "mitigate",
        "resolve",
        "postmortem"
    ]
    assert workflow.steps == expected_steps


def test_migration_workflow_squads():
    """Vérifie les squads requis pour Migration."""
    workflow = MigrationWorkflow()
    assert "data_squad" in workflow.required_squads
    assert "devops_squad" in workflow.required_squads


def test_performance_audit_workflow():
    """Vérifie la structure du Performance Audit workflow."""
    workflow = PerformanceAuditWorkflow()
    assert workflow.name == "performance_audit"
    assert "profile" in workflow.steps
    assert "analyze" in workflow.steps
    assert "optimize" in workflow.steps
    assert "verify" in workflow.steps


def test_scaling_workflow():
    """Vérifie la structure du Scaling workflow."""
    workflow = ScalingWorkflow()
    assert workflow.name == "scaling"
    assert "load_test" in workflow.steps
    assert "infrastructure" in workflow.steps


def test_release_management_workflow():
    """Vérifie la structure du Release Management workflow."""
    workflow = ReleaseManagementWorkflow()
    assert workflow.name == "release_management"
    assert "changelog" in workflow.steps
    assert "version" in workflow.steps
    assert "prod" in workflow.steps


if __name__ == "__main__":
    # Exécuter les tests avec pytest
    pytest.main([__file__, "-v"])
