# Devora Orchestration System

<div align="center">

**Système multi-agents autonome pour la transformation et le développement de projets**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-API-green.svg)](https://openrouter.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange.svg)]()

</div>

## Table des Matières

- [Vue d'Ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Les 10 Squads](#les-10-squads)
- [Les 28 Agents](#les-28-agents)
- [Les 10 Workflows](#les-10-workflows)
- [Guide d'Utilisation Rapide](#guide-dutilisation-rapide)
- [Installation](#installation)
- [Configuration](#configuration)
- [Exemples d'Utilisation](#exemples-dutilisation)
- [Documentation Complète](#documentation-complète)
- [Contributing](#contributing)

---

## Vue d'Ensemble

Le système d'orchestration Devora est une plateforme multi-agents intelligente qui permet d'automatiser et d'orchestrer des tâches complexes de développement logiciel à travers 10 squads spécialisées et 28 agents experts.

### Caractéristiques Clés

- **28 Agents Spécialisés** organisés en 10 squads
- **10 Workflows** préconfigurés pour les tâches courantes
- **Architecture Modulaire** et extensible
- **LLM-Powered** via OpenRouter API (Claude, GPT-4, Gemini, etc.)
- **Métriques en Temps Réel** (tokens, temps d'exécution, erreurs)
- **Système de Callbacks** pour le suivi de progression
- **Gestion d'Erreurs Robuste** avec retry automatique

### Cas d'Usage

- Génération de documentation technique complète
- Architecture d'API REST/GraphQL
- Design de systèmes UI/UX accessibles
- Optimisation de performances
- Tests et validation QA
- Déploiement et infrastructure DevOps
- Analyse de données et BI
- Intégration d'IA/ML

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DEVORA ORCHESTRATION SYSTEM                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────▼───────┐              ┌────────▼────────┐
            │  Base Agent   │              │  LLM Client     │
            │   (Core)      │              │ (OpenRouter)    │
            └───────┬───────┘              └─────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐     ┌────────▼────────┐
│  Agent Config  │     │ Agent Metrics   │
│  - Model       │     │ - Tokens        │
│  - Temp        │     │ - Time          │
│  - Max Tokens  │     │ - Errors        │
└────────────────┘     └─────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                            10 SQUADS                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Business   │  │   Frontend   │  │   Backend    │            │
│  │    Squad     │  │    Squad     │  │    Squad     │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │     Data     │  │   DevOps     │  │      QA      │            │
│  │    Squad     │  │    Squad     │  │    Squad     │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ Performance  │  │Accessibility │  │   AI/ML      │            │
│  │    Squad     │  │    Squad     │  │   Squad      │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
│  ┌──────────────┐                                                  │
│  │Documentation │                                                  │
│  │    Squad     │                                                  │
│  └──────────────┘                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          WORKFLOWS                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Full Stack Development    6. Data Pipeline Setup              │
│  2. API Development           7. ML Model Integration             │
│  3. Documentation Generation  8. Security Audit                   │
│  4. Performance Optimization  9. Accessibility Compliance          │
│  5. CI/CD Setup              10. Complete Project Launch           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Les 10 Squads

### 1. Business Squad
**Mission**: Définition produit et stratégie business
- **Agents**: Product Manager, Copywriter, Business Analyst

### 2. Frontend Squad
**Mission**: Design et développement d'interfaces utilisateur
- **Agents**: UI/UX Designer, Frontend Developer, CSS Specialist

### 3. Backend Squad
**Mission**: Architecture et développement backend
- **Agents**: API Architect, Backend Developer, Database Engineer

### 4. Data Squad
**Mission**: Architecture de données et analytics
- **Agents**: Database Architect, Data Engineer, BI Analyst

### 5. DevOps Squad
**Mission**: Infrastructure et déploiement
- **Agents**: Infrastructure Engineer, CI/CD Specialist, Container Orchestrator

### 6. QA Squad
**Mission**: Tests et assurance qualité
- **Agents**: Test Engineer, Automation Tester, QA Lead

### 7. Performance Squad
**Mission**: Optimisation et monitoring
- **Agents**: Performance Engineer, Load Tester, Monitoring Specialist

### 8. Accessibility Squad
**Mission**: Conformité et accessibilité
- **Agents**: Accessibility Specialist, WCAG Auditor, A11y Developer

### 9. AI/ML Squad
**Mission**: Intelligence artificielle et machine learning
- **Agents**: ML Engineer, Data Scientist, AI Architect

### 10. Documentation Squad
**Mission**: Documentation technique et guides
- **Agents**: Technical Writer, API Documenter, Tutorial Creator

---

## Les 28 Agents

### Business Squad (3 agents)
1. **Product Manager** - PRD, user stories, roadmap, priorisation RICE
2. **Copywriter** - Copy AIDA, landing pages, emails, CTAs
3. **Business Analyst** - Analyse métier, KPIs, reporting

### Frontend Squad (3 agents)
4. **UI/UX Designer** - Wireframes, design systems, WCAG compliance
5. **Frontend Developer** - React, Vue, composants shadcn/ui
6. **CSS Specialist** - Tailwind, animations, responsive design

### Backend Squad (3 agents)
7. **API Architect** - REST/GraphQL, OpenAPI, Pydantic/Zod schemas
8. **Backend Developer** - FastAPI, Node.js, microservices
9. **Database Engineer** - SQL optimization, migrations, indexing

### Data Squad (3 agents)
10. **Database Architect** - Schema design, normalization, partitioning
11. **Data Engineer** - ETL pipelines, data warehousing
12. **BI Analyst** - Dashboards, métriques, data visualization

### DevOps Squad (3 agents)
13. **Infrastructure Engineer** - Cloud (AWS/GCP/Azure), Terraform
14. **CI/CD Specialist** - GitHub Actions, Jenkins, deployment
15. **Container Orchestrator** - Docker, Kubernetes, orchestration

### QA Squad (3 agents)
16. **Test Engineer** - Test plans, test cases, manual testing
17. **Automation Tester** - Playwright, Selenium, test automation
18. **QA Lead** - Test strategy, quality metrics, release validation

### Performance Squad (3 agents)
19. **Performance Engineer** - Profiling, optimization, benchmarking
20. **Load Tester** - k6, JMeter, stress testing
21. **Monitoring Specialist** - Prometheus, Grafana, APM

### Accessibility Squad (3 agents)
22. **Accessibility Specialist** - WCAG audit, screen readers
23. **WCAG Auditor** - Compliance checking, accessibility reports
24. **A11y Developer** - ARIA, keyboard navigation, semantic HTML

### AI/ML Squad (3 agents)
25. **ML Engineer** - Model training, deployment, MLOps
26. **Data Scientist** - Feature engineering, model selection
27. **AI Architect** - AI system design, model orchestration

### Documentation Squad (1 agent)
28. **Technical Writer** - README, ADRs, guides, architecture docs

> **Note**: Actuellement, 7 agents sont implémentés. Les 21 restants suivent la même architecture BaseAgent.

---

## Les 10 Workflows

### 1. Full Stack Development
```
Business Squad → Frontend Squad → Backend Squad → QA Squad → DevOps Squad
```
Développement complet d'une application web de A à Z.

### 2. API Development
```
Business Squad → Backend Squad → Documentation Squad → QA Squad
```
Conception et développement d'API REST/GraphQL avec documentation.

### 3. Documentation Generation
```
Documentation Squad
```
Génération complète de documentation technique (README, ADRs, guides).

### 4. Performance Optimization
```
Performance Squad → Backend Squad → DevOps Squad
```
Audit, optimisation et monitoring de performances.

### 5. CI/CD Setup
```
DevOps Squad → QA Squad
```
Configuration de pipelines CI/CD et tests automatisés.

### 6. Data Pipeline Setup
```
Data Squad → DevOps Squad → Monitoring
```
Création de pipelines ETL et data warehousing.

### 7. ML Model Integration
```
AI/ML Squad → Backend Squad → DevOps Squad
```
Intégration et déploiement de modèles ML en production.

### 8. Security Audit
```
Backend Squad → QA Squad → DevOps Squad
```
Audit de sécurité complet (code, infra, API).

### 9. Accessibility Compliance
```
Accessibility Squad → Frontend Squad → QA Squad
```
Audit WCAG et mise en conformité accessibilité.

### 10. Complete Project Launch
```
Tous les Squads (orchestré)
```
Lancement complet d'un projet avec toutes les phases.

---

## Guide d'Utilisation Rapide

### Exemple Basique

```python
from orchestration.core.base_agent import BaseAgent, AgentConfig
from orchestration.agents.business_squad.product_manager import ProductManagerAgent

# Configuration
config = AgentConfig(
    name="product_manager",
    model="anthropic/claude-3.5-sonnet",
    temperature=0.7,
    max_tokens=4096,
    api_key="sk-or-v1-your-key-here"
)

# Initialisation de l'agent
pm_agent = ProductManagerAgent(config)

# Tâche à exécuter
task = {
    "task_type": "prd",
    "context": "Créer une application de gestion de tâches collaborative",
    "target_audience": "équipes de développement",
    "constraints": "MVP à livrer en 2 mois"
}

# Exécution
result = await pm_agent.execute(task)

# Résultat
print(result["output"])
print(f"Tokens utilisés: {result['metadata']['total_tokens']}")
```

### Exemple avec Callbacks

```python
def progress_callback(event: str, data: dict):
    print(f"[{event}] {data}")

config = AgentConfig(
    name="ui_designer",
    api_key="sk-or-v1-your-key-here"
)

designer = UIUXDesignerAgent(config)
designer.add_callback(progress_callback)

result = designer.run({
    "task": "design_system",
    "feature": "dashboard",
    "brand": {"primary_color": "#3B82F6", "font": "Inter"}
})
```

### Workflow Multi-Agents

```python
from orchestration.workflows.full_stack_workflow import FullStackWorkflow

workflow = FullStackWorkflow(api_key="sk-or-v1-your-key-here")

result = await workflow.execute({
    "project_name": "TaskMaster Pro",
    "description": "Application de gestion de tâches avec collaboration en temps réel",
    "tech_stack": ["React", "FastAPI", "PostgreSQL", "Redis"],
    "requirements": [
        "Authentification JWT",
        "Collaboration temps réel",
        "Notifications push",
        "Tableaux kanban"
    ]
})

# Accès aux résultats de chaque squad
prd = result["business"]["prd"]
design_system = result["frontend"]["design_system"]
api_spec = result["backend"]["api_spec"]
```

---

## Installation

### Prérequis

- Python 3.11+
- pip ou uv (gestionnaire de paquets)
- Clé API OpenRouter ([obtenir ici](https://openrouter.ai/))

### Installation Standard

```bash
# Cloner le repository
git clone https://github.com/votre-org/devora-transformation.git
cd devora-transformation/orchestration

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### Installation avec uv (Recommandé)

```bash
# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installer les dépendances
uv pip install -r requirements.txt
```

---

## Configuration

### Variables d'Environnement

Créer un fichier `.env` à la racine:

```bash
# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Modèle par défaut
DEFAULT_MODEL=anthropic/claude-3.5-sonnet

# Configuration des agents
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=4096
DEFAULT_TIMEOUT=60
DEFAULT_MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO
```

### Configuration des Agents

```python
from orchestration.core.base_agent import AgentConfig

# Configuration personnalisée
custom_config = AgentConfig(
    name="custom_agent",
    model="openai/gpt-4o",  # Ou autre modèle OpenRouter
    temperature=0.5,        # Créativité (0.0 = déterministe, 1.0 = créatif)
    max_tokens=8192,        # Longueur maximale de réponse
    api_key=os.getenv("OPENROUTER_API_KEY"),
    timeout=120,            # Timeout en secondes
    max_retries=5,          # Nombre de tentatives
    log_level="DEBUG"       # Niveau de logging
)
```

---

## Exemples d'Utilisation

### 1. Générer un PRD Complet

```python
from orchestration.agents.business_squad.product_manager import ProductManagerAgent
from orchestration.core.base_agent import AgentConfig

config = AgentConfig(
    name="pm",
    api_key="sk-or-v1-your-key-here"
)

pm = ProductManagerAgent(config)

prd = await pm.generate_prd(
    feature_description="Marketplace de services freelance avec système de paiement intégré",
    target_audience="freelances et clients"
)

print(prd)
```

### 2. Créer un Design System

```python
from orchestration.agents.frontend_squad.ui_ux_designer import UIUXDesignerAgent

designer = UIUXDesignerAgent(config)

design_system = await designer.create_design_system(
    brand={
        "primary_color": "#6366F1",
        "secondary_color": "#EC4899",
        "font_family": "Inter",
        "brand_name": "TaskMaster"
    },
    accessibility_level="WCAG AA"
)

print(design_system["result"])
```

### 3. Architecturer une API

```python
from orchestration.agents.backend_squad.api_architect import APIArchitect

architect = APIArchitect(config)

api_spec = await architect.execute({
    "requirements": [
        "CRUD utilisateurs",
        "Authentification JWT",
        "Gestion de projets",
        "WebSocket temps réel"
    ],
    "data_models": [
        {"name": "User", "fields": ["id", "email", "name", "role"]},
        {"name": "Project", "fields": ["id", "name", "description", "owner_id"]}
    ],
    "api_type": "rest",
    "auth_type": "jwt",
    "versioning": True
})

print(api_spec["openapi_spec"])
```

### 4. Générer de la Documentation

```python
from orchestration.agents.documentation_squad.technical_writer import TechnicalWriterAgent

writer = TechnicalWriterAgent(config)

readme = await writer.generate_readme(
    project_name="TaskMaster Pro",
    context="Application de gestion de tâches collaborative avec temps réel",
    tech_stack=["React", "FastAPI", "PostgreSQL", "Redis", "WebSocket"]
)

with open("README.md", "w") as f:
    f.write(readme["output"]["content"])
```

### 5. Workflow Complet

```python
# Workflow de développement d'API
from orchestration.workflows import APIDevWorkflow

workflow = APIDevWorkflow(api_key="sk-or-v1-your-key-here")

result = await workflow.run({
    "project_name": "TaskAPI",
    "description": "API REST pour gestion de tâches",
    "requirements": [
        "Authentification JWT",
        "CRUD tâches",
        "Filtres et recherche",
        "Pagination",
        "Rate limiting"
    ]
})

# Résultats disponibles
print(result["prd"])           # Product Requirements
print(result["api_spec"])      # OpenAPI Specification
print(result["schemas"])       # Validation Schemas
print(result["documentation"]) # API Documentation
print(result["tests"])         # Test Cases
```

---

## Documentation Complète

- **[AGENTS.md](./AGENTS.md)** - Documentation détaillée de chaque agent
- **[WORKFLOWS.md](./WORKFLOWS.md)** - Guide des workflows et cas d'usage
- **[API.md](./API.md)** - Documentation de l'API REST (si serveur déployé)
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Architecture du système Devora
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Guide de contribution

---

## Métriques et Monitoring

Chaque agent fournit des métriques détaillées:

```python
result = agent.run(task)

metrics = result["metrics"]
print(f"Tokens totaux: {metrics['total_tokens']}")
print(f"Temps d'exécution: {metrics['execution_time']:.2f}s")
print(f"Tentatives: {metrics['retry_count']}")
print(f"Erreurs: {metrics['error_count']}")
```

### Callbacks pour Suivi en Temps Réel

```python
def detailed_callback(event: str, data: dict):
    if event == "agent_started":
        print(f"🚀 Démarrage: {data['agent']}")
    elif event == "validation_complete":
        print("✅ Validation réussie")
    elif event == "execution_complete":
        print(f"⏱️  Exécution: {data['time']:.2f}s")
    elif event == "agent_completed":
        print(f"✨ Terminé - {data['metrics']['total_tokens']} tokens")
    elif event == "agent_failed":
        print(f"❌ Erreur: {data['error']}")

agent.add_callback(detailed_callback)
```

---

## Modèles Supportés

Tous les modèles disponibles via [OpenRouter](https://openrouter.ai/models):

### Recommandés pour Production
- `anthropic/claude-3.5-sonnet` - Excellent équilibre qualité/prix
- `openai/gpt-4o` - Performance maximale
- `google/gemini-2.0-flash-exp` - Rapide et économique

### Pour Développement
- `anthropic/claude-3-haiku` - Rapide et peu coûteux
- `google/gemini-flash-1.5` - Bon compromis
- `openai/gpt-4o-mini` - Version allégée de GPT-4o

### Spécialisés
- `anthropic/claude-opus-4.5` - Tasks complexes
- `google/gemini-pro-1.5` - Long contexte (1M tokens)
- `meta-llama/llama-3.1-70b` - Open source performant

---

## Limites et Contraintes

### Limites Actuelles
- 7 agents implémentés sur 28 prévus
- Pas de workflows prédéfinis (structure en place)
- Pas d'API REST server (agents utilisables en Python uniquement)
- Pas de UI web pour orchestration

### Limites Techniques
- Rate limiting dépend du fournisseur LLM
- Timeout par défaut: 60 secondes
- Max retries: 3 tentatives
- Tokens max par requête: 4096 (configurable)

---

## Roadmap

### Phase 1 - Agents Core (En cours)
- [x] BaseAgent avec LLM integration
- [x] Product Manager Agent
- [x] UI/UX Designer Agent
- [x] API Architect Agent
- [x] Technical Writer Agent
- [ ] Compléter les 21 agents restants

### Phase 2 - Workflows
- [ ] Implémenter les 10 workflows prédéfinis
- [ ] Système d'orchestration inter-agents
- [ ] Gestion de dépendances entre agents
- [ ] Parallélisation des tâches

### Phase 3 - API & Interface
- [ ] Serveur FastAPI pour orchestration
- [ ] WebSocket pour suivi temps réel
- [ ] Interface web d'orchestration
- [ ] Dashboard de monitoring

### Phase 4 - Avancé
- [ ] Agents auto-apprenants
- [ ] Fine-tuning de modèles
- [ ] Cache intelligent
- [ ] Mode offline avec modèles locaux

---

## Contributing

Les contributions sont les bienvenues! Consultez [CONTRIBUTING.md](./CONTRIBUTING.md) pour:

- Guide de développement
- Standards de code
- Process de PR
- Architecture des agents

### Développer un Nouvel Agent

```python
from orchestration.core.base_agent import BaseAgent, AgentConfig
from typing import Any, Dict

class MonNouvelAgent(BaseAgent):
    """Description de l'agent."""

    def validate_input(self, input_data: Any) -> bool:
        # Valider les inputs
        return True

    def execute(self, input_data: Any, **kwargs) -> Any:
        # Logique métier
        prompt = self._build_prompt(input_data)
        response = self._call_llm(prompt, system_message="Ton système prompt")
        return response["content"]

    def format_output(self, raw_output: Any) -> Dict[str, Any]:
        # Formater la sortie
        return {"result": raw_output}
```

---

## Licence

MIT License - voir [LICENSE](../LICENSE)

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/votre-org/devora-transformation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/votre-org/devora-transformation/discussions)
- **Email**: support@devora.ai

---

## Remerciements

Construit avec:
- [OpenRouter](https://openrouter.ai/) - API unifiée pour LLMs
- [FastAPI](https://fastapi.tiangolo.com/) - Framework backend
- [Anthropic Claude](https://www.anthropic.com/) - Modèles LLM de pointe
- [OpenAI](https://openai.com/) - GPT-4 et modèles associés

---

<div align="center">

**Devora Orchestration System** - Code Intelligemment Orchestré

[Documentation](./AGENTS.md) • [Workflows](./WORKFLOWS.md) • [API](./API.md)

</div>
