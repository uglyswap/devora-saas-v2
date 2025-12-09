"""
Exemples d'utilisation des workflows Devora

Ce fichier montre comment utiliser les différents workflows disponibles.
"""

import asyncio
from orchestration.workflows import (
    FeatureDevelopmentWorkflow,
    BugResolutionWorkflow,
    QualityGateWorkflow,
    SaasMvpWorkflow,
    get_workflow,
    list_workflows,
    get_workflow_info
)


async def example_feature_development():
    """Exemple: Développement d'une nouvelle feature."""
    print("\n=== Feature Development Workflow ===\n")

    workflow = FeatureDevelopmentWorkflow()

    context = {
        "feature_description": "Add user profile page with avatar upload",
        "requirements": [
            "Display user information (name, email, bio)",
            "Edit profile functionality",
            "Upload and crop avatar image",
            "Privacy settings"
        ],
        "priority": "P1",
        "target_audience": "All authenticated users",
        "constraints": "Must work on mobile devices"
    }

    # Note: orchestrator doit être une instance réelle d'orchestrateur
    # result = await workflow.execute(context, orchestrator)

    print(f"Workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Steps: {workflow.steps}")
    print(f"Required squads: {workflow.required_squads}")


async def example_bug_resolution():
    """Exemple: Résolution d'un bug."""
    print("\n=== Bug Resolution Workflow ===\n")

    workflow = BugResolutionWorkflow()

    context = {
        "bug_description": "Login button not working on Safari",
        "severity": "Élevée",
        "steps_to_reproduce": [
            "1. Open app in Safari",
            "2. Navigate to /login",
            "3. Click login button",
            "4. Nothing happens"
        ],
        "expected_behavior": "User should be redirected to dashboard",
        "actual_behavior": "Button click has no effect",
        "environment": "production",
        "affected_component": "frontend"
    }

    print(f"Workflow: {workflow.name}")
    print(f"Steps: {workflow.steps}")


async def example_quality_gate():
    """Exemple: Quality gate avant commit."""
    print("\n=== Quality Gate Workflow ===\n")

    workflow = QualityGateWorkflow()

    context = {
        "target_path": "./src",
        "auto_fix": True,
        "skip_tests": False,
        "test_types": ["unit", "integration"],
        "fail_threshold": 80
    }

    print(f"Workflow: {workflow.name}")
    print(f"Auto-fix enabled: {workflow.auto_fix_enabled}")
    print(f"Steps: {workflow.steps}")


async def example_saas_mvp():
    """Exemple: Création d'un MVP SaaS."""
    print("\n=== SaaS MVP Workflow ===\n")

    workflow = SaasMvpWorkflow()

    context = {
        "product_name": "TaskMaster",
        "product_vision": "Simple task management for small teams",
        "target_market": "Remote teams of 5-20 people",
        "core_features": [
            "Task creation and assignment",
            "Team collaboration",
            "Progress tracking",
            "Email notifications"
        ],
        "business_model": "subscription",
        "tech_preferences": {
            "backend": "Node.js + Express",
            "frontend": "React + TypeScript",
            "database": "PostgreSQL (Supabase)",
            "hosting": "Vercel"
        }
    }

    print(f"Workflow: {workflow.name}")
    print(f"Steps: {workflow.steps}")
    print(f"Required squads: {workflow.required_squads}")


async def example_dynamic_workflow():
    """Exemple: Utilisation dynamique des workflows."""
    print("\n=== Dynamic Workflow Usage ===\n")

    # Lister tous les workflows
    workflows = list_workflows()
    print(f"Available workflows: {workflows}\n")

    # Obtenir des infos sur un workflow
    for workflow_name in workflows[:3]:  # Premiers 3 workflows
        info = get_workflow_info(workflow_name)
        print(f"\nWorkflow: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Steps: {', '.join(info['steps'])}")
        print(f"Required squads: {', '.join(info['required_squads'])}")

    # Récupérer un workflow dynamiquement
    print("\n--- Dynamic workflow instantiation ---")
    WorkflowClass = get_workflow('bug_resolution')
    workflow = WorkflowClass()
    print(f"Dynamically created: {workflow.name}")


async def example_incident_response():
    """Exemple: Réponse à un incident de production."""
    print("\n=== Incident Response Workflow ===\n")

    from orchestration.workflows import IncidentResponseWorkflow

    workflow = IncidentResponseWorkflow()

    context = {
        "incident_description": "API gateway returning 503 errors",
        "alert_source": "monitoring",
        "affected_service": "api-gateway",
        "environment": "production",
        "initial_severity": "SEV1"
    }

    print(f"Workflow: {workflow.name}")
    print(f"Steps: {workflow.steps}")
    print("This is a critical workflow for production incidents")


async def example_release_management():
    """Exemple: Gestion d'une release."""
    print("\n=== Release Management Workflow ===\n")

    from orchestration.workflows import ReleaseManagementWorkflow

    workflow = ReleaseManagementWorkflow()

    context = {
        "release_type": "minor",
        "current_version": "1.2.3",
        "release_branch": "release/1.3.0",
        "features": [
            "User profiles",
            "Dark mode support",
            "Export to PDF"
        ],
        "fixes": [
            "Fixed login bug on Safari",
            "Improved performance on mobile"
        ],
        "breaking_changes": [],
        "auto_deploy": False  # Manual approval needed for production
    }

    print(f"Workflow: {workflow.name}")
    print(f"Steps: {workflow.steps}")


async def main():
    """Exécute tous les exemples."""
    print("=" * 60)
    print("DEVORA ORCHESTRATION WORKFLOWS - EXAMPLES")
    print("=" * 60)

    await example_feature_development()
    await example_bug_resolution()
    await example_quality_gate()
    await example_saas_mvp()
    await example_incident_response()
    await example_release_management()
    await example_dynamic_workflow()

    print("\n" + "=" * 60)
    print("Pour exécuter réellement un workflow, vous devez:")
    print("1. Avoir une instance d'orchestrateur configurée")
    print("2. Passer le contexte approprié")
    print("3. Appeler await workflow.execute(context, orchestrator)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Exécuter les exemples
    asyncio.run(main())
