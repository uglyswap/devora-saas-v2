# Documentation des Agents

Guide complet de tous les agents du système d'orchestration Devora.

---

## Table des Matières

- [Architecture BaseAgent](#architecture-baseagent)
- [Business Squad](#business-squad)
- [Frontend Squad](#frontend-squad)
- [Backend Squad](#backend-squad)
- [Data Squad](#data-squad)
- [DevOps Squad](#devops-squad)
- [QA Squad](#qa-squad)
- [Performance Squad](#performance-squad)
- [Accessibility Squad](#accessibility-squad)
- [AI/ML Squad](#aiml-squad)
- [Documentation Squad](#documentation-squad)
- [Exemples d'Utilisation](#exemples-dutilisation)

---

## Architecture BaseAgent

Tous les agents héritent de `BaseAgent` qui fournit:

### Fonctionnalités Core

```python
class BaseAgent(ABC):
    """Classe de base pour tous les agents."""

    # Configuration
    config: AgentConfig

    # État
    status: AgentStatus  # IDLE, RUNNING, COMPLETED, FAILED, PAUSED

    # Métriques
    metrics: AgentMetrics  # tokens, temps, erreurs

    # Callbacks
    callbacks: List[Callable]  # Suivi de progression

    # Méthodes abstraites
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool

    @abstractmethod
    def execute(self, input_data: Any, **kwargs) -> Any

    @abstractmethod
    def format_output(self, raw_output: Any) -> Dict[str, Any]
```

### Configuration Standard

```python
AgentConfig(
    name: str,              # Nom unique de l'agent
    model: str,             # Modèle LLM (ex: "anthropic/claude-3.5-sonnet")
    temperature: float,     # 0.0 - 1.0 (créativité)
    max_tokens: int,        # Longueur max de réponse
    api_key: str,          # Clé OpenRouter
    timeout: int,          # Timeout en secondes
    max_retries: int,      # Nombre de tentatives
    log_level: str         # DEBUG, INFO, WARNING, ERROR
)
```

### Métriques Disponibles

```python
AgentMetrics(
    total_tokens: int,        # Total tokens utilisés
    prompt_tokens: int,       # Tokens dans le prompt
    completion_tokens: int,   # Tokens dans la réponse
    execution_time: float,    # Temps d'exécution (secondes)
    retry_count: int,         # Nombre de retries
    error_count: int          # Nombre d'erreurs
)
```

---

## Business Squad

### 1. Product Manager Agent

**Responsabilités**: PRD, user stories, roadmap, priorisation RICE

#### Capacités

- Génération de Product Requirement Documents (PRD)
- Création de user stories au format Agile
- Définition de roadmap produit
- Priorisation de features avec framework RICE

#### Input Format

```python
{
    "task_type": "prd" | "user_story" | "roadmap" | "prioritization",
    "context": str,              # Description du besoin
    "target_audience": str,      # Audience cible
    "constraints": str           # Contraintes (optionnel)
}
```

#### Output Format

```python
{
    "status": "success" | "error",
    "output": str,               # Contenu généré en markdown
    "metadata": {
        "task_type": str,
        "timestamp": str,
        "target_audience": str
    }
}
```

#### Exemples

**Générer un PRD**:
```python
prd = await pm_agent.generate_prd(
    feature_description="Application mobile de livraison de repas avec suivi en temps réel",
    target_audience="utilisateurs urbains 18-45 ans"
)
```

**Créer des User Stories**:
```python
stories = await pm_agent.create_user_stories(
    feature_description="Système de paiement sécurisé avec carte et wallet",
    persona="utilisateur mobile"
)
```

**Prioriser avec RICE**:
```python
prioritization = await pm_agent.prioritize_features([
    "Paiement Apple Pay",
    "Programme de fidélité",
    "Recommandations IA",
    "Mode sombre"
])
```

#### System Prompt

```
Tu es un Product Manager expert avec 10+ ans d'expérience.

Responsabilités:
- Créer des PRD détaillés et actionnables
- Rédiger des user stories: "En tant que [persona], je veux [action] afin de [bénéfice]"
- Définir roadmaps avec priorisation RICE (Reach, Impact, Confidence, Effort)
- Analyser les besoins et les transformer en specs techniques
- Définir critères d'acceptation et KPIs

Principes:
- User-centric: partir du besoin utilisateur
- Data-driven: baser sur des métriques
- Itératif: privilégier MVP et amélioration continue
- Collaboratif: travailler en équipe
```

---

### 2. Copywriter Agent

**Responsabilités**: Copy marketing, landing pages, emails, CTAs

#### Capacités

- Copywriting AIDA (Attention, Intérêt, Désir, Action)
- Landing pages persuasives
- Emails de conversion
- CTAs optimisés
- A/B testing variants

#### Input Format

```python
{
    "copy_type": "landing" | "email" | "cta" | "ad" | "product",
    "product_name": str,
    "target_audience": str,
    "tone": "professional" | "casual" | "urgent" | "friendly",
    "goal": str,                # Objectif (ex: "convertir en inscription")
    "key_points": List[str]     # Points clés à inclure
}
```

#### Exemples de Prompts

**Landing Page**:
```python
copy = await copywriter.generate_landing_page(
    product_name="TaskMaster Pro",
    target_audience="équipes remote",
    tone="professional",
    key_points=[
        "Collaboration temps réel",
        "Intégrations illimitées",
        "Prix transparent"
    ]
)
```

**Email Marketing**:
```python
email = await copywriter.generate_email(
    campaign_type="onboarding",
    goal="activer les nouveaux utilisateurs",
    tone="friendly"
)
```

---

### 3. Business Analyst Agent

**Responsabilités**: Analyse métier, KPIs, reporting, ROI

#### Capacités

- Analyse de business case
- Définition de KPIs et métriques
- Calculs de ROI et projections
- Analyse de marché
- Tableaux de bord analytiques

#### Input Format

```python
{
    "analysis_type": "kpi" | "roi" | "market" | "competitor" | "swot",
    "context": str,
    "data": Dict[str, Any],     # Données disponibles
    "timeframe": str,           # Période d'analyse
    "objectives": List[str]     # Objectifs business
}
```

---

## Frontend Squad

### 4. UI/UX Designer Agent

**Responsabilités**: Design d'interface, UX, systèmes de design, accessibilité

#### Capacités

- Génération de wireframes
- Création de design systems
- User flows et journey maps
- Analyse d'accessibilité WCAG
- Spécifications de composants
- Design responsive

#### Input Format

```python
{
    "task": "wireframe" | "design_system" | "user_flow" | "component_spec" | "accessibility_audit",
    "feature": str,
    "requirements": str,
    "brand": {
        "primary_color": str,    # Ex: "#3B82F6"
        "font": str,             # Ex: "Inter"
        "brand_name": str
    },
    "target_audience": str,
    "accessibility_level": "WCAG A" | "WCAG AA" | "WCAG AAA"
}
```

#### Output Format

```python
{
    "status": "success" | "error",
    "result": {
        "wireframes": [...],           # Si task=wireframe
        "design_system": {...},        # Si task=design_system
        "user_flows": [...],           # Si task=user_flow
        "accessibility_notes": [...]   # Pour tous
    },
    "recommendations": [...]
}
```

#### Exemples

**Créer un Design System**:
```python
design_system = await designer.create_design_system(
    brand={
        "primary_color": "#6366F1",
        "secondary_color": "#EC4899",
        "font_family": "Inter",
        "brand_name": "TaskMaster"
    },
    accessibility_level="WCAG AA"
)

# Résultat inclut:
# - Palette de couleurs complète (50-900)
# - Échelle typographique
# - Système d'espacement
# - Composants shadcn/ui
# - Modes clair/sombre
```

**Générer des Wireframes**:
```python
wireframes = await designer.generate_wireframe(
    feature="Dashboard analytics",
    requirements="3 colonnes: KPIs, graphiques, activité récente. Responsive mobile."
)
```

**Audit d'Accessibilité**:
```python
audit = await designer.execute({
    "task": "accessibility_audit",
    "feature": "Formulaire de contact",
    "accessibility_level": "WCAG AAA"
})

# Vérifie:
# - Contraste des couleurs
# - Navigation clavier
# - ARIA labels
# - Screen reader support
```

#### System Prompt Highlights

```
Expert UI/UX Designer avec expertise en:

Design Systems:
- Atomic design methodology
- Design tokens et variables
- shadcn/ui + Tailwind CSS
- Dark mode considerations

Accessibilité:
- WCAG 2.1 AA/AAA compliance
- Screen readers
- Keyboard navigation
- Contrast ratios (4.5:1 text)

Outputs:
- Détaillés et actionnables
- Codes couleurs spécifiques
- Références shadcn/ui
- Annotations accessibilité
```

---

### 5. Frontend Developer Agent

**Responsabilités**: Développement React/Vue, composants, intégrations

#### Capacités

- Développement de composants React/Vue
- Intégration shadcn/ui
- State management (Zustand, Redux)
- React hooks custom
- Optimisation de performances
- Tests unitaires (Vitest, Jest)

#### Input Format

```python
{
    "component_type": "page" | "component" | "hook" | "utility",
    "framework": "react" | "vue" | "svelte",
    "ui_library": "shadcn" | "material-ui" | "chakra",
    "requirements": str,
    "props": List[Dict],        # Props attendues
    "state_management": str     # Optionnel
}
```

---

### 6. CSS Specialist Agent

**Responsabilités**: Styling avancé, animations, responsive

#### Capacités

- Tailwind CSS utility-first
- Animations CSS/Framer Motion
- Responsive design (mobile-first)
- CSS Grid & Flexbox expert
- Performance CSS
- Dark mode implementation

---

## Backend Squad

### 7. API Architect Agent

**Responsabilités**: Architecture API, OpenAPI, validation schemas

#### Capacités

- Design d'API REST/GraphQL
- Génération de spécifications OpenAPI 3.1
- Création de schemas Pydantic (Python) et Zod (TypeScript)
- Stratégies de versioning
- Authentication flows (JWT, OAuth2, API keys)
- Rate limiting & caching

#### Input Format

```python
{
    "requirements": List[str],      # Requirements fonctionnels
    "data_models": List[Dict],      # Modèles de données
    "api_type": "rest" | "graphql",
    "auth_type": "jwt" | "oauth2" | "api_key",
    "versioning": bool
}
```

#### Output Format

```python
{
    "success": bool,
    "api_spec": {
        "openapi": "3.1.0",
        "info": {...},
        "paths": {...},
        "components": {...}
    },
    "schemas": [
        {
            "name": str,
            "language": "python" | "typescript",
            "content": str           # Code du schema
        }
    ],
    "endpoints": [
        {
            "path": str,
            "method": str,
            "description": str,
            "auth_required": bool,
            "rate_limit": str,
            "request_schema": str,
            "response_schema": str
        }
    ],
    "documentation": str
}
```

#### Exemples

**Architurer une API REST**:
```python
api_spec = await architect.execute({
    "requirements": [
        "CRUD utilisateurs",
        "Authentification JWT",
        "Gestion de projets et tâches",
        "WebSocket pour temps réel",
        "Upload de fichiers"
    ],
    "data_models": [
        {
            "name": "User",
            "fields": ["id", "email", "name", "role", "created_at"]
        },
        {
            "name": "Project",
            "fields": ["id", "name", "description", "owner_id", "members"]
        },
        {
            "name": "Task",
            "fields": ["id", "title", "description", "status", "project_id"]
        }
    ],
    "api_type": "rest",
    "auth_type": "jwt",
    "versioning": True
})

# Génère:
# - Spec OpenAPI 3.1 complète
# - Endpoints REST avec verbes HTTP
# - Schemas Pydantic pour validation
# - Documentation interactive
```

**Générer des Schemas de Validation**:
```python
schemas = await architect.generate_validation_schemas(
    data_models=[
        {
            "name": "UserCreate",
            "fields": {
                "email": {"type": "str", "format": "email", "required": True},
                "password": {"type": "str", "min_length": 8, "required": True},
                "name": {"type": "str", "max_length": 100}
            }
        }
    ],
    language="python"  # Génère Pydantic
)

# Ou language="typescript" pour Zod
```

**Design GraphQL Schema**:
```python
graphql = await architect.execute({
    "api_type": "graphql",
    "data_models": [...],
    "requirements": [
        "Queries: user, users, project, projects",
        "Mutations: createUser, updateProject, deleteTask",
        "Subscriptions: taskUpdated"
    ]
})

# Génère schema GraphQL complet avec resolvers
```

#### System Prompt Highlights

```
Expert API Architect avec:

Expertise:
- REST, GraphQL, RPC patterns
- OpenAPI 3.1 specification
- Pydantic v2 & Zod validation
- JWT, OAuth2, API keys
- Rate limiting, caching
- Pagination (offset, cursor)

Best Practices:
- Consistent naming (camelCase JSON)
- Proper HTTP status codes
- Idempotent operations
- HATEOAS discoverability
- Input validation
- Security-first design

Output:
- Complete OpenAPI spec
- Validation schemas
- Endpoint documentation
- Security schemes
- Example requests/responses
```

---

### 8. Backend Developer Agent

**Responsabilités**: Développement backend, microservices, business logic

#### Capacités

- Développement FastAPI/Node.js/Django
- Architecture microservices
- Business logic implementation
- Database integration (ORM)
- Async processing (Celery, Bull)
- Caching (Redis)

---

### 9. Database Engineer Agent

**Responsabilités**: Optimisation SQL, migrations, indexing

#### Capacités

- Query optimization
- Index design
- Migration scripts
- Performance tuning
- Replication setup
- Backup strategies

---

## Data Squad

### 10. Database Architect Agent

**Responsabilités**: Schema design, normalisation, partitioning

#### Capacités

- Database schema design (SQL/NoSQL)
- Normalization (1NF à 5NF)
- Denormalization strategies
- Partitioning & sharding
- Relationship modeling
- Constraints & indexes

#### Input Format

```python
{
    "database_type": "postgresql" | "mysql" | "mongodb" | "redis",
    "entities": List[Dict],         # Entités du domaine
    "relationships": List[Dict],    # Relations entre entités
    "scale": "small" | "medium" | "large" | "enterprise",
    "access_patterns": List[str]    # Patterns d'accès prévus
}
```

#### Exemples

**Design de Schema SQL**:
```python
schema = await db_architect.design_schema(
    database_type="postgresql",
    entities=[
        {
            "name": "users",
            "attributes": ["id", "email", "name", "created_at"],
            "primary_key": "id",
            "indexes": ["email"]
        },
        {
            "name": "orders",
            "attributes": ["id", "user_id", "total", "status", "created_at"],
            "foreign_keys": [{"column": "user_id", "references": "users.id"}]
        }
    ],
    scale="medium",
    access_patterns=[
        "Frequent: get user orders",
        "Frequent: filter orders by status",
        "Rare: full order history"
    ]
)

# Génère:
# - CREATE TABLE statements
# - Indexes optimaux
# - Foreign keys avec CASCADE
# - Triggers si nécessaires
```

---

### 11. Data Engineer Agent

**Responsabilités**: ETL pipelines, data warehousing, streaming

#### Capacités

- ETL/ELT pipeline design
- Data warehouse modeling (Kimball, Inmon)
- Stream processing (Kafka, Flink)
- Data quality validation
- Airflow DAGs
- DBT transformations

---

### 12. BI Analyst Agent

**Responsabilités**: Dashboards, métriques, data visualization

#### Capacités

- Dashboard design (Metabase, Looker)
- KPI définition
- SQL analytics queries
- Data storytelling
- Metric frameworks (AARRR, HEART)
- A/B test analysis

---

## DevOps Squad

### 13. Infrastructure Engineer Agent

**Responsabilités**: Cloud infrastructure, IaC, scaling

#### Capacités

- Infrastructure as Code (Terraform, Pulumi)
- Cloud platforms (AWS, GCP, Azure)
- Kubernetes cluster setup
- Networking & security groups
- Auto-scaling configuration
- Cost optimization

#### Input Format

```python
{
    "cloud_provider": "aws" | "gcp" | "azure" | "digitalocean",
    "services": List[str],           # Services à déployer
    "environment": "dev" | "staging" | "production",
    "scaling": {
        "type": "horizontal" | "vertical",
        "min": int,
        "max": int
    },
    "region": str,
    "budget_constraint": str         # Optionnel
}
```

---

### 14. CI/CD Specialist Agent

**Responsabilités**: Pipelines, automated deployment, testing

#### Capacités

- GitHub Actions workflows
- GitLab CI/CD
- Jenkins pipelines
- Automated testing integration
- Docker build & push
- Blue-green deployments
- Rollback strategies

---

### 15. Container Orchestrator Agent

**Responsabilités**: Docker, Kubernetes, container management

#### Capacités

- Dockerfile optimization
- Kubernetes manifests (Deployment, Service, Ingress)
- Helm charts
- Container security scanning
- Resource limits & requests
- Health checks & probes

---

## QA Squad

### 16. Test Engineer Agent

**Responsabilités**: Test strategy, test cases, manual testing

#### Capacités

- Test plan creation
- Test case generation (functional, edge cases)
- Acceptance criteria validation
- Exploratory testing guides
- Bug report templates
- QA checklists

---

### 17. Automation Tester Agent

**Responsabilités**: Test automation, E2E testing, frameworks

#### Capacités

- Playwright/Selenium test generation
- API test automation (Postman, Rest Assured)
- Unit test scaffolding
- Integration test suites
- Load test scripts (k6, JMeter)
- Test data generation

---

### 18. QA Lead Agent

**Responsabilités**: Quality metrics, release validation, standards

#### Capacités

- Quality metrics dashboard
- Release checklists
- Regression test suites
- Performance benchmarks
- Security test plans
- Compliance validation

---

## Performance Squad

### 19. Performance Engineer Agent

**Responsabilités**: Profiling, optimization, benchmarking

#### Capacités

- Performance profiling (Python, Node.js)
- Bottleneck identification
- Optimization recommendations
- Benchmark suite creation
- Memory leak detection
- Database query optimization

#### Input Format

```python
{
    "system_type": "web" | "api" | "database" | "mobile",
    "current_metrics": {
        "response_time": float,      # ms
        "throughput": int,           # req/s
        "error_rate": float          # %
    },
    "target_metrics": {
        "response_time": float,
        "throughput": int,
        "uptime": float              # %
    },
    "constraints": List[str]
}
```

---

### 20. Load Tester Agent

**Responsabilités**: Load testing, stress testing, capacity planning

#### Capacités

- k6 test scripts
- JMeter test plans
- Locust scenarios
- Stress test scenarios
- Spike test patterns
- Capacity planning analysis

---

### 21. Monitoring Specialist Agent

**Responsabilités**: APM, alerting, observability

#### Capacités

- Prometheus metrics design
- Grafana dashboard configuration
- Alert rules (PagerDuty, Opsgenie)
- Log aggregation (ELK stack)
- Tracing setup (Jaeger, Zipkin)
- SLO/SLA monitoring

---

## Accessibility Squad

### 22. Accessibility Specialist Agent

**Responsabilités**: WCAG compliance, screen readers, inclusive design

#### Capacités

- WCAG 2.1 audit (A, AA, AAA)
- Screen reader testing guides
- Color contrast validation
- Keyboard navigation review
- ARIA implementation
- Accessibility statements

---

### 23. WCAG Auditor Agent

**Responsabilités**: Automated accessibility testing, compliance reports

#### Capacités

- Axe-core integration
- Pa11y automation
- Lighthouse accessibility scores
- Compliance checklists
- Remediation prioritization
- Accessibility reports

---

### 24. A11y Developer Agent

**Responsabilités**: Accessible component development, ARIA

#### Capacités

- Accessible component patterns
- ARIA attributes implementation
- Focus management
- Skip links
- Semantic HTML
- Form accessibility

---

## AI/ML Squad

### 25. ML Engineer Agent

**Responsabilités**: Model training, deployment, MLOps

#### Capacités

- Model architecture selection
- Training pipeline setup
- Hyperparameter tuning
- Model serving (TensorFlow Serving, TorchServe)
- MLflow experiment tracking
- Model monitoring

---

### 26. Data Scientist Agent

**Responsabilités**: Feature engineering, model selection, analysis

#### Capacités

- Exploratory Data Analysis (EDA)
- Feature engineering strategies
- Model selection & comparison
- Statistical analysis
- Experimentation design
- Result interpretation

---

### 27. AI Architect Agent

**Responsabilités**: AI system design, model orchestration, RAG

#### Capacités

- AI system architecture
- LLM integration patterns
- RAG (Retrieval Augmented Generation) setup
- Vector database selection
- Prompt engineering strategies
- Multi-model orchestration

---

## Documentation Squad

### 28. Technical Writer Agent

**Responsabilités**: Documentation technique, README, ADRs, guides

#### Capacités

- README generation (comprehensive)
- Architecture Decision Records (ADR)
- Installation guides (multi-platform)
- Architecture documentation
- API documentation
- Troubleshooting guides

#### Input Format

```python
{
    "doc_type": "readme" | "adr" | "installation" | "architecture" | "custom",
    "context": str,                  # Contexte du projet
    "project_name": str,
    "tech_stack": List[str],
    "audience": "developers" | "users" | "stakeholders",
    "include_diagrams": bool
}
```

#### Output Format

```python
{
    "status": "success" | "error",
    "output": {
        "content": str,              # Documentation en markdown
        "metadata": {
            "type": str,
            "project": str,
            "word_count": int,
            "generated_at": str
        }
    },
    "file_suggestions": {
        "primary": str,              # Ex: "README.md"
        "alternative": str           # Ex: "docs/readme.md"
    }
}
```

#### Exemples

**Générer un README Complet**:
```python
readme = await writer.generate_readme(
    project_name="TaskMaster Pro",
    context="Application de gestion de tâches collaborative avec temps réel",
    tech_stack=["React", "FastAPI", "PostgreSQL", "Redis", "WebSocket"]
)

# Génère README avec:
# - Badges/shields
# - Table of contents
# - Installation steps
# - Quick start
# - API documentation
# - Contributing guide
# - License
```

**Créer un ADR**:
```python
adr = await writer.generate_adr(
    project_name="TaskMaster",
    decision_context="""
    Décision: Utiliser PostgreSQL avec Supabase plutôt que MongoDB

    Contexte: Besoin de relations complexes entre users, projects, tasks
    avec requêtes relationnelles fréquentes et transactions ACID.

    Alternatives: MongoDB, Firebase, DynamoDB
    """,
    tech_stack=["PostgreSQL", "Supabase", "Prisma"]
)

# Génère ADR suivant template standard:
# - Status: Accepted
# - Context
# - Decision
# - Consequences (+/-)
# - Alternatives considered
# - Related decisions
```

**Guide d'Installation Multi-Plateforme**:
```python
install_guide = await writer.generate_installation_guide(
    project_name="TaskMaster Pro",
    context="Application FastAPI + React nécessitant Python 3.11, Node 18, PostgreSQL 15",
    tech_stack=["Python 3.11", "Node.js 18", "PostgreSQL 15", "Redis 7"]
)

# Génère guide avec:
# - Prerequisites détaillés
# - Steps macOS/Linux/Windows
# - Environment setup
# - Database initialization
# - Verification steps
# - Troubleshooting
```

**Documentation d'Architecture**:
```python
arch_docs = await writer.generate_architecture_docs(
    project_name="TaskMaster Pro",
    context="""
    Architecture microservices:
    - Frontend: React SPA
    - API Gateway: Kong
    - Services: User, Project, Task, Notification
    - Event Bus: RabbitMQ
    - Database: PostgreSQL (multi-tenant)
    - Cache: Redis
    - Storage: S3
    """,
    tech_stack=["React", "Kong", "FastAPI", "RabbitMQ", "PostgreSQL", "Redis", "S3"]
)

# Génère avec diagrams Mermaid:
# - System overview
# - Component diagrams
# - Data flow
# - Deployment architecture
# - Security architecture
```

#### Templates Disponibles

**README Template**:
```markdown
# Project Name
[Shields/Badges]

## Description
## Table of Contents
## Installation
## Quick Start
## Usage
## API Documentation
## Configuration
## Contributing
## License
## Contact
```

**ADR Template**:
```markdown
# ADR-XXXX: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
## Decision
## Consequences
### Positive
### Negative
## Alternatives Considered
## Related Decisions
## Notes
```

---

## Exemples d'Utilisation

### Workflow Multi-Agents Complet

```python
from orchestration.agents.business_squad.product_manager import ProductManagerAgent
from orchestration.agents.frontend_squad.ui_ux_designer import UIUXDesignerAgent
from orchestration.agents.backend_squad.api_architect import APIArchitect
from orchestration.agents.documentation_squad.technical_writer import TechnicalWriterAgent
from orchestration.core.base_agent import AgentConfig

# Configuration commune
api_key = "sk-or-v1-your-key"
model = "anthropic/claude-3.5-sonnet"

# 1. Product Manager - PRD
pm_config = AgentConfig(name="pm", api_key=api_key, model=model)
pm = ProductManagerAgent(pm_config)

prd_result = await pm.generate_prd(
    feature_description="Plateforme SaaS de gestion de projets pour équipes remote",
    target_audience="équipes de 5-50 personnes"
)

# 2. UI/UX Designer - Design System
designer_config = AgentConfig(name="designer", api_key=api_key)
designer = UIUXDesignerAgent(designer_config)

design_result = await designer.create_design_system(
    brand={
        "primary_color": "#6366F1",
        "font_family": "Inter",
        "brand_name": "ProjectFlow"
    },
    accessibility_level="WCAG AA"
)

# 3. API Architect - API Design
architect_config = AgentConfig(name="architect", api_key=api_key)
architect = APIArchitect(architect_config)

api_result = await architect.execute({
    "requirements": [
        "Authentication JWT",
        "CRUD projects & tasks",
        "Real-time collaboration",
        "File uploads",
        "Activity feed"
    ],
    "data_models": [
        {"name": "User", "fields": ["id", "email", "name", "avatar"]},
        {"name": "Project", "fields": ["id", "name", "description", "owner_id"]},
        {"name": "Task", "fields": ["id", "title", "status", "project_id", "assignee_id"]}
    ],
    "api_type": "rest",
    "auth_type": "jwt",
    "versioning": True
})

# 4. Technical Writer - Documentation
writer_config = AgentConfig(name="writer", api_key=api_key)
writer = TechnicalWriterAgent(writer_config)

readme_result = await writer.generate_readme(
    project_name="ProjectFlow",
    context=f"""
    {prd_result['output']}

    Design System: {design_result['result']}
    API Spec: {api_result['api_spec']}
    """,
    tech_stack=["React", "FastAPI", "PostgreSQL", "Redis", "WebSocket"]
)

# Sauvegarder les résultats
with open("PRD.md", "w") as f:
    f.write(prd_result['output'])

with open("DESIGN_SYSTEM.json", "w") as f:
    json.dump(design_result['result'], f, indent=2)

with open("openapi.json", "w") as f:
    json.dump(api_result['api_spec'], f, indent=2)

with open("README.md", "w") as f:
    f.write(readme_result['output']['content'])

print("✅ Workflow complet terminé!")
print(f"Total tokens: {sum([
    pm.metrics.total_tokens,
    designer.metrics.total_tokens,
    architect.metrics.total_tokens,
    writer.metrics.total_tokens
])}")
```

### Utilisation avec Callbacks Détaillés

```python
import time
from datetime import datetime

class ProgressTracker:
    def __init__(self):
        self.events = []
        self.start_time = None

    def callback(self, event: str, data: dict):
        timestamp = datetime.now().isoformat()

        if event == "agent_started":
            self.start_time = time.time()
            print(f"🚀 [{timestamp}] Started: {data['agent']}")

        elif event == "validation_complete":
            print(f"✅ [{timestamp}] Validation: {data['status']}")

        elif event == "execution_complete":
            duration = data['time']
            print(f"⚡ [{timestamp}] Execution: {duration:.2f}s")

        elif event == "agent_completed":
            total_time = time.time() - self.start_time
            metrics = data['metrics']
            print(f"✨ [{timestamp}] Completed: {data['agent']}")
            print(f"   └─ Tokens: {metrics['total_tokens']}")
            print(f"   └─ Time: {total_time:.2f}s")
            print(f"   └─ Retries: {metrics['retry_count']}")

        elif event == "agent_failed":
            print(f"❌ [{timestamp}] Failed: {data['agent']}")
            print(f"   └─ Error: {data['error']}")

        self.events.append({"event": event, "data": data, "timestamp": timestamp})

# Utilisation
tracker = ProgressTracker()

config = AgentConfig(name="pm", api_key="sk-or-v1-xxx")
pm = ProductManagerAgent(config)
pm.add_callback(tracker.callback)

result = await pm.generate_prd(
    feature_description="Application de livraison de repas",
    target_audience="urbains 18-45 ans"
)

# Affiche:
# 🚀 [2024-12-09T10:30:00] Started: product_manager
# ✅ [2024-12-09T10:30:00] Validation: success
# ⚡ [2024-12-09T10:30:15] Execution: 15.23s
# ✨ [2024-12-09T10:30:15] Completed: product_manager
#    └─ Tokens: 2847
#    └─ Time: 15.23s
#    └─ Retries: 0
```

### Gestion d'Erreurs et Retry

```python
from orchestration.core.base_agent import AgentConfig, BaseAgent

config = AgentConfig(
    name="test_agent",
    api_key="sk-or-v1-xxx",
    max_retries=5,           # Augmenter les retries
    timeout=120,             # Timeout plus long
    log_level="DEBUG"        # Logging détaillé
)

agent = SomeAgent(config)

try:
    result = agent.run(input_data)

    if result["status"] == "success":
        print("✅ Success:", result["output"])
        print("📊 Metrics:", result["metrics"])
    else:
        print("❌ Failed:", result["error"])
        print("🔄 Retries:", result["metrics"]["retry_count"])

except Exception as e:
    print(f"💥 Exception: {str(e)}")
    print(f"Metrics: {agent.get_metrics()}")
```

---

## Comparaison des Agents

### Par Complexité d'Output

| Agent | Complexité | Tokens Moyens | Temps Moyen |
|-------|-----------|---------------|-------------|
| Copywriter | Faible | 500-1000 | 5-10s |
| UI/UX Designer | Moyenne | 1500-3000 | 15-25s |
| Product Manager | Moyenne | 2000-4000 | 20-30s |
| API Architect | Élevée | 3000-6000 | 30-45s |
| Technical Writer | Élevée | 4000-8000 | 40-60s |

### Par Cas d'Usage

| Cas d'Usage | Agents Recommandés | Ordre |
|-------------|-------------------|-------|
| **Nouvelle Feature** | PM → Designer → Architect → Writer | 1-2-3-4 |
| **Refonte UI** | Designer → Frontend Dev → A11y Specialist | 1-2-3 |
| **API Backend** | PM → Architect → Backend Dev → Writer | 1-2-3-4 |
| **Documentation** | Writer | 1 |
| **Performance** | Performance Engineer → Load Tester | 1-2 |
| **Lancement Complet** | Tous les squads | Workflow orchestré |

---

## Bonnes Pratiques

### 1. Configuration

```python
# ✅ BON: Configuration par environnement
dev_config = AgentConfig(
    name="agent_dev",
    model="anthropic/claude-3-haiku",  # Modèle rapide/économique
    temperature=0.7,
    max_tokens=2048
)

prod_config = AgentConfig(
    name="agent_prod",
    model="anthropic/claude-3.5-sonnet",  # Modèle premium
    temperature=0.5,                       # Plus déterministe
    max_tokens=8192
)
```

### 2. Gestion des Métriques

```python
# Tracker les coûts
agent = SomeAgent(config)
results = []

for task in tasks:
    result = agent.run(task)
    results.append(result)

    # Log metrics
    print(f"Task: {task['id']}")
    print(f"Tokens: {result['metrics']['total_tokens']}")
    print(f"Time: {result['metrics']['execution_time']:.2f}s")

# Total
total_tokens = sum(r['metrics']['total_tokens'] for r in results)
total_time = sum(r['metrics']['execution_time'] for r in results)

print(f"\n📊 Summary:")
print(f"Total tokens: {total_tokens}")
print(f"Total time: {total_time:.2f}s")
print(f"Average tokens/task: {total_tokens/len(tasks):.0f}")
```

### 3. Callbacks pour Production

```python
import logging
from typing import Dict, Any

class ProductionCallback:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def __call__(self, event: str, data: Dict[str, Any]):
        if event == "agent_failed":
            self.logger.error(f"Agent failed: {data['agent']}", extra={
                "error": data['error'],
                "agent": data['agent']
            })
            # Envoyer alerte (Sentry, PagerDuty, etc.)

        elif event == "agent_completed":
            metrics = data['metrics']
            if metrics['total_tokens'] > 10000:
                self.logger.warning(f"High token usage: {metrics['total_tokens']}")

# Usage
logger = logging.getLogger("production")
callback = ProductionCallback(logger)
agent.add_callback(callback)
```

---

## Troubleshooting

### Erreur: "Invalid API Key"

```python
# Vérifier la clé
import os
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key or not api_key.startswith("sk-or-v1-"):
    raise ValueError("Invalid OpenRouter API key")

config = AgentConfig(name="test", api_key=api_key)
```

### Erreur: "Timeout"

```python
# Augmenter timeout
config = AgentConfig(
    name="agent",
    api_key="...",
    timeout=180,      # 3 minutes au lieu de 60s
    max_retries=5     # Plus de retries
)
```

### Erreur: "Token Limit Exceeded"

```python
# Utiliser modèle avec plus de tokens
config = AgentConfig(
    name="agent",
    model="google/gemini-pro-1.5",  # 1M tokens context
    max_tokens=16384                 # Augmenter limite
)
```

---

**Documentation maintenue par**: Documentation Squad
**Dernière mise à jour**: 2024-12-09
**Version**: 1.0
