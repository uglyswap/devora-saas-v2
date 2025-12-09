# Devora Orchestration Workflows

Ce dossier contient 10 workflows professionnels pour le système d'orchestration Devora.

## Workflows disponibles

### 1. Feature Development (`feature_development.py`)
**Description:** Workflow complet de développement de feature
**Étapes:** Analyze → Plan → Design → Implement → Test → Review → Deploy
**Squads:** Product, Frontend, Backend, QA
**Durée estimée:** 2-4 heures

### 2. Bug Resolution (`bug_resolution.py`)
**Description:** Workflow systématique de résolution de bugs
**Étapes:** Reproduce → Diagnose → Fix → Test → Review
**Squads:** QA, Frontend/Backend (selon le composant)
**Durée estimée:** 1-2 heures

### 3. SaaS MVP (`saas_mvp.py`)
**Description:** Création de MVP SaaS complet de A à Z
**Étapes:** Requirements → Architecture → Database → Backend → Frontend → Deploy
**Squads:** All squads (Product, Backend, Frontend, Data, DevOps, QA)
**Durée estimée:** 8-16 heures

### 4. Quality Gate (`quality_gate.py`)
**Description:** Vérification qualité automatique avec auto-fix
**Étapes:** TypeCheck → Lint → Test → Security → Performance
**Squads:** QA
**Features:** Auto-fix activé, score qualité global
**Durée estimée:** 30 minutes

### 5. Migration (`migration.py`)
**Description:** Workflow sécurisé pour migrations (database, framework, infrastructure)
**Étapes:** Analyze → Plan → Backup → Migrate → Verify → Rollback Plan
**Squads:** Data, DevOps
**Durée estimée:** 3-6 heures

### 6. Refactoring (`refactoring.py`)
**Description:** Refactoring systématique avec tests de non-régression
**Étapes:** Analyze → Plan → Refactor → Test → Review
**Squads:** QA, Frontend/Backend
**Durée estimée:** 2-4 heures

### 7. Performance Audit (`performance_audit.py`)
**Description:** Audit de performance complet
**Étapes:** Profile → Analyze → Optimize → Verify
**Squads:** Performance
**Métriques:** Lighthouse, Web Vitals, Bundle size, Memory, Network
**Durée estimée:** 3-6 heures

### 8. Scaling (`scaling.py`)
**Description:** Préparation au scaling de l'application
**Étapes:** Load Test → Analyze → Optimize → Infrastructure
**Squads:** Performance, DevOps
**Durée estimée:** 4-8 heures

### 9. Incident Response (`incident_response.py`)
**Description:** Réponse aux incidents critiques en production
**Étapes:** Detect → Assess → Mitigate → Resolve → Postmortem
**Squads:** DevOps, QA
**Sévérités:** SEV1 (Critique) à SEV4 (Faible)
**Durée estimée:** 1-2 heures

### 10. Release Management (`release_management.py`)
**Description:** Gestion complète des releases
**Étapes:** Changelog → Version → QA → Stage → Prod → Monitor
**Squads:** DevOps, Documentation, QA
**Types:** major, minor, patch, hotfix
**Durée estimée:** 1.5-3 heures

## Usage

### Import d'un workflow

```python
from orchestration.workflows import FeatureDevelopmentWorkflow

# Créer une instance du workflow
workflow = FeatureDevelopmentWorkflow()

# Préparer le contexte
context = {
    "feature_description": "Add user profile page",
    "requirements": ["Display user info", "Edit profile", "Upload avatar"],
    "priority": "P1",
    "target_audience": "All users"
}

# Exécuter le workflow
result = await workflow.execute(context, orchestrator)
```

### Lister les workflows disponibles

```python
from orchestration.workflows import list_workflows, get_workflow_info

# Lister tous les workflows
workflows = list_workflows()
# ['feature_development', 'bug_resolution', ...]

# Obtenir les informations sur un workflow
info = get_workflow_info('feature_development')
```

### Récupérer un workflow dynamiquement

```python
from orchestration.workflows import get_workflow

# Récupérer la classe du workflow
WorkflowClass = get_workflow('bug_resolution')

# Instancier et exécuter
workflow = WorkflowClass()
result = await workflow.execute(context, orchestrator)
```

## Structure d'un workflow

Chaque workflow est une classe Python avec:

- **name** (str): Nom unique du workflow
- **description** (str): Description courte
- **steps** (List[str]): Liste des étapes
- **required_squads** (List[str]): Squads nécessaires
- **execute(context, orchestrator)**: Méthode principale async
- **_run_step(step_name, context)**: Exécution d'une étape

## Résultat d'exécution

Tous les workflows retournent un dictionnaire avec:

```python
{
    "workflow": "feature_development",
    "status": "completed",
    "started_at": "2025-12-09T03:30:00Z",
    "completed_at": "2025-12-09T05:45:00Z",
    "steps": {...},
    "context": {...}
}
```

## Squads disponibles

- **business_squad**: Product Manager
- **frontend_squad**: Frontend Developer, UI Designer
- **backend_squad**: Backend Developer, Backend Architect
- **data_squad**: Database Architect
- **devops_squad**: DevOps Engineer
- **qa_squad**: QA Engineer, Code Reviewer
- **performance_squad**: Performance Engineer
- **documentation_squad**: Technical Writer

## Bonnes pratiques

1. **Toujours passer un contexte complet**
2. **Gérer les erreurs** - Vérifier le status du résultat
3. **Logger les exécutions** - Chaque workflow log automatiquement
4. **Itérer sur les étapes** - Examiner steps pour le debugging
5. **Utiliser dry_run** - Certains workflows supportent un mode test
