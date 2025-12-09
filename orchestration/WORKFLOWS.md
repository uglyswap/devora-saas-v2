# Workflows Documentation

Guide complet des workflows d'orchestration multi-agents Devora.

---

## Table des Matières

- [Introduction](#introduction)
- [Architecture des Workflows](#architecture-des-workflows)
- [Les 10 Workflows](#les-10-workflows)
  - [1. Full Stack Development](#1-full-stack-development)
  - [2. API Development](#2-api-development)
  - [3. Documentation Generation](#3-documentation-generation)
  - [4. Performance Optimization](#4-performance-optimization)
  - [5. CI/CD Setup](#5-cicd-setup)
  - [6. Data Pipeline Setup](#6-data-pipeline-setup)
  - [7. ML Model Integration](#7-ml-model-integration)
  - [8. Security Audit](#8-security-audit)
  - [9. Accessibility Compliance](#9-accessibility-compliance)
  - [10. Complete Project Launch](#10-complete-project-launch)
- [Workflow Patterns](#workflow-patterns)
- [Création de Workflows Custom](#création-de-workflows-custom)
- [Exemples Pratiques](#exemples-pratiques)
- [Best Practices](#best-practices)

---

## Introduction

Les workflows Devora orchestrent automatiquement plusieurs agents pour accomplir des tâches complexes de bout en bout. Chaque workflow définit:

- **Séquence d'agents** à exécuter
- **Données partagées** entre agents
- **Conditions de transition** entre étapes
- **Gestion d'erreurs** et retry logic
- **Métriques agrégées** de performance

### Avantages

- **Automatisation complète** de tâches multi-étapes
- **Cohérence garantie** entre outputs d'agents
- **Traçabilité** complète du processus
- **Optimisation** du flow de données
- **Réutilisabilité** de patterns éprouvés

---

## Architecture des Workflows

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKFLOW ENGINE                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼────────┐     ┌────────▼────────┐
            │ Workflow State │     │ Agent Registry  │
            │   - Current    │     │   - Available   │
            │   - History    │     │   - Loaded      │
            │   - Context    │     │   - Health      │
            └────────────────┘     └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     WORKFLOW EXECUTION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input → [Agent 1] → [Validation] → [Agent 2] → ... → Output  │
│              │            │             │                       │
│              ↓            ↓             ↓                       │
│          Context      Check OK?     Context                    │
│          Update                     Update                     │
│                                                                 │
│  [Error Handler] ←─── Error? ←─── [Retry Logic]               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        SHARED CONTEXT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  {                                                              │
│    "project_name": str,                                         │
│    "requirements": List[str],                                   │
│    "tech_stack": List[str],                                     │
│    "outputs": {                                                 │
│      "agent_1": {...},    # Output du premier agent            │
│      "agent_2": {...},    # Output du deuxième agent           │
│      ...                                                        │
│    },                                                           │
│    "metrics": {                                                 │
│      "total_tokens": int,                                       │
│      "total_time": float,                                       │
│      "agents_executed": int                                     │
│    }                                                            │
│  }                                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Les 10 Workflows

### 1. Full Stack Development

**Objectif**: Développement complet d'une application web de A à Z

**Squads Impliquées**:
```
Business Squad → Frontend Squad → Backend Squad → Data Squad → QA Squad → DevOps Squad
```

**Étapes**:

1. **Business Analysis** (Business Squad)
   - Product Manager: Génère PRD complet
   - Business Analyst: Définit KPIs et métriques
   - Copywriter: Crée copy pour landing page

2. **Design & Frontend** (Frontend Squad)
   - UI/UX Designer: Crée design system et wireframes
   - Frontend Developer: Développe composants React
   - CSS Specialist: Implémente styling Tailwind

3. **Backend Architecture** (Backend Squad)
   - API Architect: Design API REST/GraphQL
   - Backend Developer: Implémente endpoints
   - Database Engineer: Optimise queries

4. **Data Layer** (Data Squad)
   - Database Architect: Design schema
   - Data Engineer: Setup ETL si nécessaire
   - BI Analyst: Configure dashboards analytics

5. **Quality Assurance** (QA Squad)
   - Test Engineer: Crée test plan
   - Automation Tester: Implémente tests E2E
   - QA Lead: Valide release

6. **Deployment** (DevOps Squad)
   - Infrastructure Engineer: Setup cloud infra
   - CI/CD Specialist: Configure pipeline
   - Container Orchestrator: Deploy sur Kubernetes

**Input Format**:

```python
{
    "project_name": str,
    "description": str,
    "target_audience": str,
    "tech_stack": {
        "frontend": List[str],    # Ex: ["React", "Tailwind", "shadcn/ui"]
        "backend": List[str],     # Ex: ["FastAPI", "PostgreSQL", "Redis"]
        "infrastructure": List[str]  # Ex: ["AWS", "Docker", "Kubernetes"]
    },
    "requirements": List[str],
    "timeline": str,              # Ex: "3 mois"
    "budget": str,                # Optionnel
    "team_size": int             # Optionnel
}
```

**Output Format**:

```python
{
    "status": "success" | "partial" | "failed",
    "deliverables": {
        "business": {
            "prd": str,                    # Product Requirements Document
            "kpis": List[Dict],            # KPIs définis
            "copy": Dict[str, str]         # Landing page copy
        },
        "frontend": {
            "design_system": Dict,         # Design system complet
            "wireframes": List[Dict],      # Wireframes pages principales
            "components": List[str],       # Code composants React
            "styles": str                  # CSS/Tailwind config
        },
        "backend": {
            "api_spec": Dict,              # OpenAPI specification
            "endpoints": List[str],        # Code endpoints
            "schemas": List[str],          # Pydantic/Zod schemas
            "database": {
                "schema": str,             # SQL schema
                "migrations": List[str]    # Migration scripts
            }
        },
        "data": {
            "architecture": str,           # Data architecture doc
            "etl_pipelines": List[str],   # ETL code si applicable
            "dashboards": List[Dict]       # Config dashboards
        },
        "qa": {
            "test_plan": str,             # Plan de tests
            "test_suites": List[str],     # Code tests automatisés
            "coverage_report": Dict       # Rapport coverage
        },
        "devops": {
            "infrastructure": str,         # Terraform/IaC code
            "ci_cd": str,                 # GitHub Actions config
            "deployment": str              # K8s manifests
        },
        "documentation": {
            "readme": str,                # README.md
            "architecture": str,          # ARCHITECTURE.md
            "deployment_guide": str,      # Guide déploiement
            "api_docs": str              # Documentation API
        }
    },
    "metrics": {
        "total_tokens": int,
        "total_time": float,
        "agents_executed": int,
        "success_rate": float
    },
    "timeline": {
        "estimated_completion": str,
        "phases": List[Dict]
    }
}
```

**Exemple d'Utilisation**:

```python
from orchestration.workflows.full_stack import FullStackWorkflow

workflow = FullStackWorkflow(api_key="sk-or-v1-xxx")

result = await workflow.execute({
    "project_name": "TaskMaster Pro",
    "description": "Application de gestion de tâches collaborative avec temps réel",
    "target_audience": "Équipes de développement 5-50 personnes",
    "tech_stack": {
        "frontend": ["React 18", "Tailwind CSS", "shadcn/ui", "Zustand"],
        "backend": ["FastAPI", "PostgreSQL", "Redis", "WebSocket"],
        "infrastructure": ["AWS", "Docker", "Kubernetes", "GitHub Actions"]
    },
    "requirements": [
        "Authentification JWT",
        "Collaboration temps réel",
        "Tableaux kanban",
        "Notifications push",
        "Intégrations (Slack, GitHub)",
        "API REST + WebSocket",
        "Mobile responsive"
    ],
    "timeline": "3 mois",
    "team_size": 5
})

# Accès aux livrables
print(result["deliverables"]["business"]["prd"])
print(result["deliverables"]["frontend"]["design_system"])
print(result["deliverables"]["backend"]["api_spec"])
```

---

### 2. API Development

**Objectif**: Conception et développement d'API REST/GraphQL complète avec documentation

**Squads Impliquées**:
```
Business Squad → Backend Squad → Documentation Squad → QA Squad
```

**Étapes**:

1. **Requirements Analysis** (Business Squad)
   - Product Manager: Définit requirements API
   - Business Analyst: Identifie use cases et métriques

2. **API Design** (Backend Squad)
   - API Architect: Crée OpenAPI spec
   - Backend Developer: Implémente endpoints
   - Database Engineer: Optimise queries

3. **Documentation** (Documentation Squad)
   - Technical Writer: Génère API documentation
   - Create guides (Getting Started, Authentication, etc.)

4. **Testing** (QA Squad)
   - Automation Tester: Tests API automatisés
   - Load Tester: Performance testing
   - QA Lead: Validation finale

**Input Format**:

```python
{
    "api_name": str,
    "description": str,
    "api_type": "rest" | "graphql",
    "auth_type": "jwt" | "oauth2" | "api_key",
    "versioning": bool,
    "requirements": List[str],        # Endpoints requis
    "data_models": List[Dict],        # Modèles de données
    "rate_limits": Dict[str, int],   # Optionnel
    "target_qps": int                # Queries per second cible
}
```

**Output Format**:

```python
{
    "status": "success" | "failed",
    "api_specification": {
        "openapi": Dict,              # OpenAPI 3.1 spec complet
        "graphql_schema": str,        # Si type=graphql
        "postman_collection": Dict    # Collection Postman
    },
    "implementation": {
        "endpoints": List[str],       # Code endpoints
        "schemas": List[str],         # Validation schemas
        "middleware": List[str],      # Auth, CORS, etc.
        "tests": List[str]           # Tests unitaires
    },
    "documentation": {
        "readme": str,               # README API
        "getting_started": str,      # Guide démarrage
        "authentication": str,       # Guide auth
        "examples": List[Dict],      # Exemples d'usage
        "changelog": str            # CHANGELOG.md
    },
    "testing": {
        "test_suite": str,          # Tests automatisés
        "load_tests": str,          # Scripts k6/JMeter
        "coverage": float           # % coverage
    }
}
```

**Exemple**:

```python
from orchestration.workflows.api_development import APIDevWorkflow

workflow = APIDevWorkflow(api_key="sk-or-v1-xxx")

result = await workflow.execute({
    "api_name": "TaskMaster API",
    "description": "API REST pour gestion de tâches collaborative",
    "api_type": "rest",
    "auth_type": "jwt",
    "versioning": True,
    "requirements": [
        "CRUD utilisateurs",
        "CRUD projets et tâches",
        "Filtres et recherche avancée",
        "WebSocket pour temps réel",
        "Upload de fichiers",
        "Webhooks pour intégrations"
    ],
    "data_models": [
        {
            "name": "User",
            "fields": {
                "id": "uuid",
                "email": "string",
                "name": "string",
                "role": "enum"
            }
        },
        {
            "name": "Task",
            "fields": {
                "id": "uuid",
                "title": "string",
                "status": "enum",
                "assignee_id": "uuid"
            }
        }
    ],
    "rate_limits": {
        "anonymous": 100,
        "authenticated": 1000,
        "premium": 10000
    },
    "target_qps": 1000
})

# Sauvegarder les outputs
with open("openapi.json", "w") as f:
    json.dump(result["api_specification"]["openapi"], f, indent=2)

with open("API_README.md", "w") as f:
    f.write(result["documentation"]["readme"])
```

---

### 3. Documentation Generation

**Objectif**: Génération complète de documentation technique professionnelle

**Squads Impliquées**:
```
Documentation Squad
```

**Étapes**:

1. **Analysis** - Analyse du projet et code
2. **Generation** - Génération docs (README, ADRs, guides)
3. **Review** - Vérification qualité et complétude
4. **Publishing** - Formatage final et export

**Input Format**:

```python
{
    "project_name": str,
    "project_type": "library" | "application" | "api" | "service",
    "tech_stack": List[str],
    "source_code_path": str,         # Optionnel: path vers code
    "existing_docs": List[str],      # Docs existantes à inclure
    "documentation_types": [         # Types de docs à générer
        "readme",
        "architecture",
        "api_reference",
        "installation",
        "contributing",
        "adr"
    ],
    "target_audiences": List[str],   # Ex: ["developers", "users", "contributors"]
    "include_diagrams": bool,
    "output_format": "markdown" | "html" | "pdf"
}
```

**Output Format**:

```python
{
    "status": "success",
    "documents": {
        "README.md": str,
        "ARCHITECTURE.md": str,
        "INSTALLATION.md": str,
        "CONTRIBUTING.md": str,
        "API.md": str,
        "adrs/": List[str]           # Liste d'ADRs
    },
    "diagrams": {
        "architecture.mmd": str,     # Mermaid diagrams
        "dataflow.mmd": str
    },
    "metadata": {
        "word_count": int,
        "readability_score": float,
        "completion_time": float
    }
}
```

**Exemple**:

```python
from orchestration.workflows.documentation import DocumentationWorkflow

workflow = DocumentationWorkflow(api_key="sk-or-v1-xxx")

result = await workflow.execute({
    "project_name": "TaskMaster Pro",
    "project_type": "application",
    "tech_stack": ["React", "FastAPI", "PostgreSQL"],
    "documentation_types": [
        "readme",
        "architecture",
        "installation",
        "api_reference",
        "contributing"
    ],
    "target_audiences": ["developers", "contributors"],
    "include_diagrams": True
})

# Écrire tous les fichiers
for filename, content in result["documents"].items():
    with open(filename, "w") as f:
        f.write(content)
```

---

### 4. Performance Optimization

**Objectif**: Audit et optimisation complète des performances

**Squads Impliquées**:
```
Performance Squad → Backend Squad → DevOps Squad
```

**Étapes**:

1. **Profiling** (Performance Squad)
   - Performance Engineer: Profile application
   - Identifie bottlenecks

2. **Load Testing** (Performance Squad)
   - Load Tester: Tests de charge
   - Détermine limites actuelles

3. **Optimization** (Backend Squad)
   - Backend Developer: Optimise code
   - Database Engineer: Optimise queries et indexes

4. **Monitoring Setup** (DevOps Squad)
   - Monitoring Specialist: Configure APM
   - Setup alertes performance

**Input Format**:

```python
{
    "application_url": str,
    "application_type": "web" | "api" | "mobile",
    "current_metrics": {
        "response_time_p95": float,    # ms
        "throughput": int,             # req/s
        "error_rate": float,           # %
        "cpu_usage": float,            # %
        "memory_usage": float          # GB
    },
    "target_metrics": {
        "response_time_p95": float,
        "throughput": int,
        "error_rate": float,
        "uptime": float               # % (ex: 99.9)
    },
    "constraints": List[str],         # Ex: "No breaking changes"
    "budget": str                     # Infrastructure budget
}
```

**Output Format**:

```python
{
    "status": "success",
    "analysis": {
        "bottlenecks": List[Dict],    # Bottlenecks identifiés
        "recommendations": List[str],
        "quick_wins": List[str],      # Optimisations rapides
        "long_term": List[str]        # Améliorations à long terme
    },
    "load_testing": {
        "baseline": Dict,             # Métriques avant
        "target": Dict,               # Métriques après
        "test_scripts": List[str]     # Scripts k6/JMeter
    },
    "optimizations": {
        "code_changes": List[str],    # Patches de code
        "database": List[str],        # Optimisations DB
        "infrastructure": List[str],  # Changements infra
        "caching": Dict              # Stratégie de cache
    },
    "monitoring": {
        "dashboards": List[Dict],    # Grafana dashboards
        "alerts": List[Dict],        # Règles d'alerte
        "apm_config": str           # Config APM
    },
    "estimated_improvement": {
        "response_time": str,        # Ex: "-50%"
        "throughput": str,           # Ex: "+200%"
        "cost_savings": str         # Ex: "-30%"
    }
}
```

---

### 5. CI/CD Setup

**Objectif**: Configuration complète de pipeline CI/CD

**Squads Impliquées**:
```
DevOps Squad → QA Squad
```

**Étapes**:

1. **Pipeline Design** (DevOps Squad)
   - CI/CD Specialist: Design workflow
   - Define stages et gates

2. **Testing Integration** (QA Squad)
   - Automation Tester: Intègre tests auto
   - Configure test reporting

3. **Deployment Strategy** (DevOps Squad)
   - Container Orchestrator: Setup déploiement
   - Blue-green ou rolling deployment

4. **Monitoring** (DevOps Squad)
   - Setup monitoring post-deploy
   - Configure rollback automatique

**Input Format**:

```python
{
    "repository_url": str,
    "git_provider": "github" | "gitlab" | "bitbucket",
    "tech_stack": List[str],
    "environments": [
        {"name": "dev", "auto_deploy": True},
        {"name": "staging", "auto_deploy": True},
        {"name": "production", "auto_deploy": False, "requires_approval": True}
    ],
    "testing_requirements": {
        "unit_tests": bool,
        "integration_tests": bool,
        "e2e_tests": bool,
        "minimum_coverage": float    # Ex: 80.0
    },
    "deployment_target": "kubernetes" | "ecs" | "app_engine" | "vercel",
    "notifications": List[str]       # Ex: ["slack", "email"]
}
```

**Output Format**:

```python
{
    "status": "success",
    "pipeline_config": {
        "github_actions": str,        # .github/workflows/ci.yml
        "gitlab_ci": str,            # .gitlab-ci.yml (si applicable)
        "dockerfile": str,           # Dockerfile optimisé
        "docker_compose": str        # docker-compose.yml
    },
    "testing": {
        "test_commands": List[str],
        "coverage_config": str,
        "test_reports": str          # Config reporting
    },
    "deployment": {
        "kubernetes": List[str],     # K8s manifests
        "helm_chart": str,          # Si Helm
        "deployment_script": str    # Script de déploiement
    },
    "documentation": {
        "cicd_guide": str,          # Guide CI/CD
        "troubleshooting": str      # Guide troubleshooting
    }
}
```

---

### 6. Data Pipeline Setup

**Objectif**: Configuration de pipeline ETL/ELT complet

**Squads Impliquées**:
```
Data Squad → DevOps Squad
```

**Étapes**:

1. **Architecture** (Data Squad)
   - Data Engineer: Design pipeline ETL
   - Database Architect: Design data warehouse

2. **Implementation** (Data Squad)
   - Data Engineer: Implémente transformations
   - BI Analyst: Crée dashboards

3. **Deployment** (DevOps Squad)
   - Infrastructure Engineer: Deploy pipeline
   - Monitoring Specialist: Monitor data quality

**Input & Output**: Voir exemples détaillés en section suivante.

---

### 7. ML Model Integration

**Objectif**: Intégration et déploiement de modèle ML en production

**Squads Impliquées**:
```
AI/ML Squad → Backend Squad → DevOps Squad
```

**Étapes**:

1. **Model Preparation** (AI/ML Squad)
   - ML Engineer: Prépare modèle pour production
   - Data Scientist: Valide métriques

2. **API Integration** (Backend Squad)
   - Backend Developer: Crée endpoints ML
   - API Architect: Design API pour inférence

3. **Deployment** (DevOps Squad)
   - Deploy modèle (TensorFlow Serving, etc.)
   - Setup monitoring ML-specific

---

### 8. Security Audit

**Objectif**: Audit de sécurité complet (code, infra, API)

**Squads Impliquées**:
```
Backend Squad → QA Squad → DevOps Squad
```

**Détails complets** dans section suivante.

---

### 9. Accessibility Compliance

**Objectif**: Audit WCAG et mise en conformité accessibilité

**Squads Impliquées**:
```
Accessibility Squad → Frontend Squad → QA Squad
```

**Détails complets** dans section suivante.

---

### 10. Complete Project Launch

**Objectif**: Lancement complet d'un projet de A à Z

**Squads Impliquées**:
```
Tous les Squads (orchestration complète)
```

**Phases**:

1. **Discovery & Planning** (Business Squad)
2. **Design & Architecture** (Frontend + Backend + Data Squads)
3. **Development** (Tous les dev squads)
4. **Testing & QA** (QA + Performance + Accessibility Squads)
5. **Documentation** (Documentation Squad)
6. **Deployment & Launch** (DevOps Squad)
7. **Post-Launch Monitoring** (Performance + DevOps Squads)

**Timeline**: 2-6 mois selon complexité

---

## Workflow Patterns

### Pattern 1: Sequential

```
Agent A → Agent B → Agent C → Agent D
```

**Usage**: Quand chaque agent dépend de l'output du précédent.

**Exemple**: Documentation Workflow
```python
Analysis → Generation → Review → Publishing
```

### Pattern 2: Parallel

```
Agent A →┐
Agent B →├→ Aggregator → Next Step
Agent C →┘
```

**Usage**: Quand plusieurs agents peuvent travailler en parallèle.

**Exemple**: Full Stack Workflow (phase Design)
```python
UI/UX Designer    →┐
Frontend Dev      →├→ Frontend Integration → Backend Phase
CSS Specialist    →┘
```

### Pattern 3: Conditional

```
Agent A → Condition? → Agent B (if true)
                    → Agent C (if false)
```

**Usage**: Workflow branches selon conditions.

**Exemple**: API Development
```python
API Architect → Type? → REST Path (OpenAPI)
                     → GraphQL Path (Schema)
```

### Pattern 4: Iterative

```
Agent A → Agent B → Validation → OK? → Output
                         ↑        ↓ NOK
                         └────────┘ (retry avec feedback)
```

**Usage**: Raffinement itératif jusqu'à validation.

**Exemple**: Performance Optimization
```python
Profile → Optimize → Test → Meets Target? → Done
                      ↑          ↓ No
                      └──────────┘
```

---

## Création de Workflows Custom

### Structure de Base

```python
from orchestration.workflows.base import BaseWorkflow
from orchestration.agents.business_squad.product_manager import ProductManagerAgent
from orchestration.agents.frontend_squad.ui_ux_designer import UIUXDesignerAgent
from typing import Dict, Any

class CustomWorkflow(BaseWorkflow):
    """Votre workflow personnalisé."""

    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        super().__init__(api_key, model)

        # Initialiser les agents nécessaires
        self.pm = ProductManagerAgent(self._create_config("pm"))
        self.designer = UIUXDesignerAgent(self._create_config("designer"))

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute le workflow."""
        context = self._init_context(input_data)

        try:
            # Étape 1: Product Manager
            prd_result = await self._run_agent(
                agent=self.pm,
                input_data={
                    "task_type": "prd",
                    "context": input_data["description"]
                },
                context=context,
                step_name="product_management"
            )

            # Étape 2: UI/UX Designer
            design_result = await self._run_agent(
                agent=self.designer,
                input_data={
                    "task": "design_system",
                    "requirements": prd_result["output"]
                },
                context=context,
                step_name="design"
            )

            # Agréger les résultats
            return self._format_output(context)

        except Exception as e:
            return self._handle_error(e, context)

    def _init_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialise le contexte partagé."""
        return {
            "project_name": input_data["project_name"],
            "start_time": time.time(),
            "outputs": {},
            "metrics": {
                "total_tokens": 0,
                "total_time": 0.0,
                "agents_executed": 0
            }
        }

    async def _run_agent(
        self,
        agent,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        step_name: str
    ) -> Dict[str, Any]:
        """Exécute un agent et met à jour le contexte."""
        self.logger.info(f"Running step: {step_name}")

        result = await agent.execute(input_data)

        # Mettre à jour contexte
        context["outputs"][step_name] = result
        context["metrics"]["total_tokens"] += result.get("metadata", {}).get("total_tokens", 0)
        context["metrics"]["agents_executed"] += 1

        return result

    def _format_output(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Formate l'output final."""
        context["metrics"]["total_time"] = time.time() - context["start_time"]

        return {
            "status": "success",
            "outputs": context["outputs"],
            "metrics": context["metrics"]
        }
```

### Utilisation

```python
workflow = CustomWorkflow(api_key="sk-or-v1-xxx")

result = await workflow.execute({
    "project_name": "Mon Projet",
    "description": "Description du projet..."
})
```

---

## Exemples Pratiques

### Exemple 1: SaaS Complet (Full Stack)

```python
from orchestration.workflows.full_stack import FullStackWorkflow

async def build_saas():
    workflow = FullStackWorkflow(api_key="sk-or-v1-xxx")

    result = await workflow.execute({
        "project_name": "InvoiceFlow",
        "description": "SaaS de facturation pour freelances et PME",
        "target_audience": "Freelances et PME 1-20 employés",
        "tech_stack": {
            "frontend": ["Next.js 14", "Tailwind", "shadcn/ui", "React Query"],
            "backend": ["FastAPI", "PostgreSQL", "Redis", "Stripe"],
            "infrastructure": ["Vercel", "Supabase", "Upstash"]
        },
        "requirements": [
            "Authentification (email + OAuth Google)",
            "Gestion clients",
            "Création/envoi factures PDF",
            "Paiements Stripe",
            "Dashboard analytics",
            "Exports comptables",
            "Multi-devises",
            "Templates personnalisables"
        ],
        "timeline": "4 mois",
        "team_size": 3
    })

    # Sauvegarder tous les livrables
    deliverables = result["deliverables"]

    # PRD
    with open("docs/PRD.md", "w") as f:
        f.write(deliverables["business"]["prd"])

    # Design System
    with open("design-system.json", "w") as f:
        json.dump(deliverables["frontend"]["design_system"], f, indent=2)

    # OpenAPI Spec
    with open("openapi.json", "w") as f:
        json.dump(deliverables["backend"]["api_spec"], f, indent=2)

    # CI/CD
    with open(".github/workflows/ci.yml", "w") as f:
        f.write(deliverables["devops"]["ci_cd"])

    # README
    with open("README.md", "w") as f:
        f.write(deliverables["documentation"]["readme"])

    print(f"✅ Workflow terminé!")
    print(f"📊 Tokens utilisés: {result['metrics']['total_tokens']}")
    print(f"⏱️  Temps total: {result['metrics']['total_time']:.2f}s")
```

### Exemple 2: API GraphQL

```python
from orchestration.workflows.api_development import APIDevWorkflow

async def build_graphql_api():
    workflow = APIDevWorkflow(api_key="sk-or-v1-xxx")

    result = await workflow.execute({
        "api_name": "E-commerce GraphQL API",
        "description": "API GraphQL pour plateforme e-commerce",
        "api_type": "graphql",
        "auth_type": "jwt",
        "versioning": False,  # GraphQL handle versioning differently
        "requirements": [
            "Query: products (avec filtres, recherche, pagination)",
            "Query: product (par ID)",
            "Query: cart",
            "Mutation: addToCart",
            "Mutation: checkout",
            "Subscription: orderUpdates"
        ],
        "data_models": [
            {
                "name": "Product",
                "fields": {
                    "id": "ID!",
                    "name": "String!",
                    "price": "Float!",
                    "category": "Category!",
                    "stock": "Int!"
                }
            },
            {
                "name": "Cart",
                "fields": {
                    "id": "ID!",
                    "items": "[CartItem!]!",
                    "total": "Float!"
                }
            }
        ],
        "target_qps": 5000
    })

    # Générer code GraphQL
    schema = result["api_specification"]["graphql_schema"]
    with open("schema.graphql", "w") as f:
        f.write(schema)

    # Générer resolvers
    resolvers = result["implementation"]["endpoints"]
    for i, resolver_code in enumerate(resolvers):
        with open(f"resolvers/resolver_{i}.py", "w") as f:
            f.write(resolver_code)

    print("✅ GraphQL API générée!")
```

### Exemple 3: Migration Performance

```python
from orchestration.workflows.performance import PerformanceWorkflow

async def optimize_slow_api():
    workflow = PerformanceWorkflow(api_key="sk-or-v1-xxx")

    result = await workflow.execute({
        "application_url": "https://api.myapp.com",
        "application_type": "api",
        "current_metrics": {
            "response_time_p95": 2500,   # 2.5s - trop lent!
            "throughput": 50,             # req/s
            "error_rate": 2.5,           # %
            "cpu_usage": 80.0,           # %
            "memory_usage": 6.0          # GB
        },
        "target_metrics": {
            "response_time_p95": 200,    # <200ms
            "throughput": 500,           # 10x plus
            "error_rate": 0.1,           # <0.1%
            "uptime": 99.9
        },
        "constraints": [
            "No breaking API changes",
            "Budget: $500/month max increase"
        ]
    })

    # Analyse
    print("🔍 Bottlenecks identifiés:")
    for bottleneck in result["analysis"]["bottlenecks"]:
        print(f"  - {bottleneck['issue']}: {bottleneck['impact']}")

    # Quick wins
    print("\n⚡ Quick Wins:")
    for win in result["analysis"]["quick_wins"]:
        print(f"  - {win}")

    # Optimisations
    print("\n🔧 Code changes:")
    for change_file in result["optimizations"]["code_changes"]:
        with open(f"patches/{change_file['filename']}", "w") as f:
            f.write(change_file['content'])

    # DB optimizations
    print("\n💾 Database optimizations:")
    for sql in result["optimizations"]["database"]:
        print(f"  - {sql}")

    print(f"\n📈 Amélioration estimée:")
    print(f"  - Response time: {result['estimated_improvement']['response_time']}")
    print(f"  - Throughput: {result['estimated_improvement']['throughput']}")
```

---

## Best Practices

### 1. Workflow Design

```python
# ✅ BON: Découper en étapes logiques
class MyWorkflow(BaseWorkflow):
    async def execute(self, input_data):
        # Phase 1: Analysis
        analysis = await self._analyze(input_data)

        # Phase 2: Design
        design = await self._design(analysis)

        # Phase 3: Implementation
        implementation = await self._implement(design)

        # Phase 4: Validation
        return await self._validate(implementation)

# ❌ MAUVAIS: Tout dans une seule méthode
class BadWorkflow(BaseWorkflow):
    async def execute(self, input_data):
        # 500 lignes de code...
```

### 2. Error Handling

```python
# ✅ BON: Gestion d'erreurs par étape
async def _run_step(self, agent, input_data, step_name):
    try:
        result = await agent.execute(input_data)
        self._update_context(step_name, result)
        return result
    except Exception as e:
        self.logger.error(f"Step {step_name} failed: {str(e)}")
        # Retry logic
        if self.retry_count < self.max_retries:
            return await self._retry_step(agent, input_data, step_name)
        raise

# ❌ MAUVAIS: Ignorer les erreurs
async def _run_step(self, agent, input_data, step_name):
    result = await agent.execute(input_data)
    return result  # Pas de try/catch!
```

### 3. Context Management

```python
# ✅ BON: Context partagé structuré
context = {
    "project": {...},
    "config": {...},
    "outputs": {
        "step1": {...},
        "step2": {...}
    },
    "metrics": {...}
}

# Accès facile aux outputs précédents
previous_output = context["outputs"]["step1"]["result"]

# ❌ MAUVAIS: Variables globales
global prd_result
global design_result
# Hard to track, error-prone
```

### 4. Monitoring & Logging

```python
# ✅ BON: Logging structuré
self.logger.info(
    f"Step completed",
    extra={
        "step": step_name,
        "tokens": result["metrics"]["total_tokens"],
        "time": result["metrics"]["execution_time"],
        "success": True
    }
)

# ❌ MAUVAIS: Logging basique
print(f"Step done: {step_name}")
```

### 5. Output Formatting

```python
# ✅ BON: Output structuré et documenté
return {
    "status": "success" | "partial" | "failed",
    "deliverables": {...},      # Tous les livrables
    "metrics": {...},           # Métriques agrégées
    "errors": [...],            # Erreurs rencontrées (si any)
    "warnings": [...],          # Warnings
    "metadata": {
        "workflow_version": "1.0",
        "execution_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat()
    }
}

# ❌ MAUVAIS: Output non structuré
return {"result": some_data, "ok": True}
```

---

## Performance & Coûts

### Estimation des Coûts par Workflow

| Workflow | Agents | Tokens Avg | Coût Estimé* | Temps |
|----------|--------|------------|--------------|-------|
| Documentation | 1 | 8,000 | $0.10 | 1 min |
| API Development | 4 | 20,000 | $0.25 | 5 min |
| Performance Opt | 5 | 25,000 | $0.30 | 7 min |
| Full Stack | 18+ | 80,000+ | $1.00+ | 20+ min |

*Coûts basés sur Claude 3.5 Sonnet via OpenRouter (~$0.012/1K tokens)

### Optimisation des Coûts

```python
# 1. Utiliser modèles adaptés par étape
config_cheap = AgentConfig(
    model="anthropic/claude-3-haiku",  # Pour tâches simples
    temperature=0.5
)

config_premium = AgentConfig(
    model="anthropic/claude-3.5-sonnet",  # Pour tâches complexes
    temperature=0.7
)

# 2. Caching des résultats
cache = {}

async def _run_with_cache(self, agent, input_data, cache_key):
    if cache_key in cache:
        return cache[cache_key]

    result = await agent.execute(input_data)
    cache[cache_key] = result
    return result

# 3. Parallélisation quand possible
results = await asyncio.gather(
    agent1.execute(data1),
    agent2.execute(data2),
    agent3.execute(data3)
)
```

---

## Troubleshooting

### Workflow Bloqué

```python
# Ajouter timeout
import asyncio

try:
    result = await asyncio.wait_for(
        workflow.execute(input_data),
        timeout=300  # 5 minutes max
    )
except asyncio.TimeoutError:
    logger.error("Workflow timeout")
```

### Agent Échoue Fréquemment

```python
# Augmenter retries et timeout
config = AgentConfig(
    max_retries=5,
    timeout=180
)

# Ajouter logging détaillé
config.log_level = "DEBUG"
```

### Métriques Élevées

```python
# Monitor tokens usage
if result["metrics"]["total_tokens"] > 50000:
    logger.warning(f"High token usage: {result['metrics']['total_tokens']}")

# Ajuster température pour réponses plus courtes
config.temperature = 0.3  # Plus déterministe et concis
```

---

**Documentation maintenue par**: DevOps Squad
**Dernière mise à jour**: 2024-12-09
**Version**: 1.0
