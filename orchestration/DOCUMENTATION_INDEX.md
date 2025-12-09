# Documentation Index - Devora Orchestration

Guide de navigation pour toute la documentation du système d'orchestration.

---

## Documentation Principale

### [README.md](./README.md) - 25KB
**Vue d'ensemble complète du système**

Contenu:
- Introduction au système d'orchestration
- Architecture globale avec diagrammes
- Les 10 squads et 28 agents
- Les 10 workflows disponibles
- Guide d'utilisation rapide
- Installation et configuration
- Exemples d'utilisation
- Métriques et monitoring

**À lire en premier** pour comprendre le système.

---

### [AGENTS.md](./AGENTS.md) - 35KB
**Documentation détaillée de tous les agents**

Contenu:
- Architecture BaseAgent
- Documentation des 28 agents par squad:
  - Business Squad (3 agents)
  - Frontend Squad (3 agents)
  - Backend Squad (3 agents)
  - Data Squad (3 agents)
  - DevOps Squad (3 agents)
  - QA Squad (3 agents)
  - Performance Squad (3 agents)
  - Accessibility Squad (3 agents)
  - AI/ML Squad (3 agents)
  - Documentation Squad (1 agent)
- Input/Output formats pour chaque agent
- Exemples d'utilisation pratiques
- System prompts et capacités
- Bonnes pratiques
- Troubleshooting

**À lire** pour comprendre comment utiliser chaque agent.

---

### [WORKFLOWS.md](./WORKFLOWS.md) - 40KB
**Guide complet des workflows**

Contenu:
- Architecture des workflows
- Les 10 workflows en détail:
  1. Full Stack Development
  2. API Development
  3. Documentation Generation
  4. Performance Optimization
  5. CI/CD Setup
  6. Data Pipeline Setup
  7. ML Model Integration
  8. Security Audit
  9. Accessibility Compliance
  10. Complete Project Launch
- Workflow patterns (Sequential, Parallel, Conditional, Iterative)
- Création de workflows custom
- Exemples pratiques complets
- Best practices
- Performance et coûts

**À lire** pour orchestrer plusieurs agents ensemble.

---

### [API.md](./API.md) - 26KB
**Documentation API REST (Plannifiée)**

Contenu:
- Vue d'ensemble de l'API
- Architecture API
- Authentication (API keys, scopes)
- Endpoints complets:
  - Agents endpoints
  - Workflows endpoints
  - Jobs endpoints
  - Metrics endpoints
- WebSocket pour temps réel
- Rate limiting
- Exemples curl, Python, JavaScript, Go
- SDKs disponibles
- Gestion d'erreurs
- Webhooks

**Note**: API non encore implémentée - documentation d'architecture.

---

### [CONTRIBUTING.md](./CONTRIBUTING.md) - 22KB
**Guide pour contribuer au projet**

Contenu:
- Code of Conduct
- Comment contribuer
- Développement local (setup, structure)
- Créer un nouvel agent (template, checklist)
- Créer un workflow (template, checklist)
- Standards de code (PEP 8, type hints, docstrings)
- Tests (structure, exemples, coverage)
- Documentation (agents, workflows)
- Process de Pull Request
- Convention de commits

**À lire** avant de contribuer du code.

---

## Documentation Technique Existante

### [UTILS_GUIDE.md](./UTILS_GUIDE.md) - 25KB
**Guide des utilitaires et helpers** (fichier existant)

---

## Fichiers de Code

### Core
- `core/base_agent.py` - Classe de base pour tous les agents
- `core/__init__.py` - Exports du module core

### Agents Implémentés (7/28)
- `agents/business_squad/product_manager.py` - Product Manager
- `agents/business_squad/copywriter.py` - Copywriter
- `agents/frontend_squad/ui_ux_designer.py` - UI/UX Designer
- `agents/backend_squad/api_architect.py` - API Architect
- `agents/data_squad/database_architect.py` - Database Architect
- `agents/documentation_squad/technical_writer.py` - Technical Writer
- `agents/devops_squad/infrastructure_engineer.py` - Infrastructure Engineer (partiel)

### Utilities
- `utils/llm_client.py` - Client LLM (OpenRouter)
- `utils/logger.py` - Configuration logging

---

## Par Cas d'Usage

### Je débute avec le système
1. Lire [README.md](./README.md) - Vue d'ensemble
2. Suivre le guide d'installation
3. Tester les exemples d'utilisation rapide

### Je veux utiliser un agent spécifique
1. Consulter [AGENTS.md](./AGENTS.md)
2. Trouver l'agent dans sa squad
3. Lire input/output format
4. Copier l'exemple d'utilisation

### Je veux créer un workflow complet
1. Lire [WORKFLOWS.md](./WORKFLOWS.md)
2. Choisir un workflow existant ou créer un custom
3. Adapter les inputs à votre projet
4. Suivre les exemples pratiques

### Je veux utiliser l'API (futur)
1. Lire [API.md](./API.md)
2. Obtenir une API key
3. Choisir votre SDK (Python, JavaScript, Go)
4. Suivre les exemples

### Je veux contribuer
1. Lire [CONTRIBUTING.md](./CONTRIBUTING.md)
2. Setup environnement de développement
3. Choisir:
   - Créer un nouvel agent → Template agent
   - Créer un workflow → Template workflow
   - Fix un bug → Process PR
4. Suivre les standards de code
5. Écrire les tests
6. Soumettre une PR

---

## Par Squad

### Business Squad
**Agents**: Product Manager, Copywriter, Business Analyst

**Documentation**:
- [AGENTS.md - Business Squad](./AGENTS.md#business-squad)
- Exemples: PRD generation, User stories, Roadmap, RICE prioritization

### Frontend Squad
**Agents**: UI/UX Designer, Frontend Developer, CSS Specialist

**Documentation**:
- [AGENTS.md - Frontend Squad](./AGENTS.md#frontend-squad)
- Exemples: Design systems, Wireframes, User flows, Accessibility

### Backend Squad
**Agents**: API Architect, Backend Developer, Database Engineer

**Documentation**:
- [AGENTS.md - Backend Squad](./AGENTS.md#backend-squad)
- Exemples: OpenAPI specs, Validation schemas, API design

### Data Squad
**Agents**: Database Architect, Data Engineer, BI Analyst

**Documentation**:
- [AGENTS.md - Data Squad](./AGENTS.md#data-squad)
- Exemples: Schema design, ETL pipelines, Dashboards

### DevOps Squad
**Agents**: Infrastructure Engineer, CI/CD Specialist, Container Orchestrator

**Documentation**:
- [AGENTS.md - DevOps Squad](./AGENTS.md#devops-squad)
- Exemples: Terraform, GitHub Actions, Kubernetes

### QA Squad
**Agents**: Test Engineer, Automation Tester, QA Lead

**Documentation**:
- [AGENTS.md - QA Squad](./AGENTS.md#qa-squad)
- Exemples: Test plans, Playwright tests, Quality metrics

### Performance Squad
**Agents**: Performance Engineer, Load Tester, Monitoring Specialist

**Documentation**:
- [AGENTS.md - Performance Squad](./AGENTS.md#performance-squad)
- Exemples: Profiling, k6 tests, Grafana dashboards

### Accessibility Squad
**Agents**: Accessibility Specialist, WCAG Auditor, A11y Developer

**Documentation**:
- [AGENTS.md - Accessibility Squad](./AGENTS.md#accessibility-squad)
- Exemples: WCAG audits, ARIA implementation

### AI/ML Squad
**Agents**: ML Engineer, Data Scientist, AI Architect

**Documentation**:
- [AGENTS.md - AI/ML Squad](./AGENTS.md#aiml-squad)
- Exemples: Model training, MLOps, RAG systems

### Documentation Squad
**Agents**: Technical Writer

**Documentation**:
- [AGENTS.md - Documentation Squad](./AGENTS.md#documentation-squad)
- Exemples: README, ADRs, Installation guides, Architecture docs

---

## Par Workflow

### 1. Full Stack Development
**Fichier**: [WORKFLOWS.md - Full Stack](./WORKFLOWS.md#1-full-stack-development)

**Utilise**: Business, Frontend, Backend, Data, QA, DevOps Squads

**Input**: Project name, description, tech stack, requirements
**Output**: PRD, design system, API spec, database schema, tests, infra code, docs

**Complexité**: Élevée | **Durée**: 20-40 min | **Coût**: $1-2

### 2. API Development
**Fichier**: [WORKFLOWS.md - API Development](./WORKFLOWS.md#2-api-development)

**Utilise**: Business, Backend, Documentation, QA Squads

**Input**: API name, type (REST/GraphQL), requirements, data models
**Output**: OpenAPI spec, code endpoints, validation schemas, tests, docs

**Complexité**: Moyenne | **Durée**: 5-10 min | **Coût**: $0.25-0.50

### 3. Documentation Generation
**Fichier**: [WORKFLOWS.md - Documentation](./WORKFLOWS.md#3-documentation-generation)

**Utilise**: Documentation Squad

**Input**: Project info, doc types
**Output**: README, Architecture docs, Installation guide, ADRs

**Complexité**: Faible | **Durée**: 1-3 min | **Coût**: $0.10-0.20

### 4-10. Autres Workflows
Voir [WORKFLOWS.md](./WORKFLOWS.md) pour les 7 autres workflows.

---

## Métriques du Projet

### Documentation
- **Total**: 6 fichiers
- **Taille totale**: ~173 KB
- **Lignes de code**: ~4,689 lignes (docs markdown)
- **Agents documentés**: 28 agents (7 implémentés)
- **Workflows documentés**: 10 workflows

### Agents Implémentés
- **Total**: 7/28 (25%)
- **Business Squad**: 2/3
- **Frontend Squad**: 1/3
- **Backend Squad**: 1/3
- **Data Squad**: 1/3
- **Documentation Squad**: 1/1
- **DevOps Squad**: 1/3
- **Autres Squads**: 0/13

### Workflows Implémentés
- **Total**: 0/10 (architecture définie, implémentation à venir)

---

## Roadmap Documentation

### Phase 1 - Complétée ✅
- [x] README.md principal
- [x] Documentation des 28 agents (AGENTS.md)
- [x] Documentation des 10 workflows (WORKFLOWS.md)
- [x] Documentation API (API.md)
- [x] Guide de contribution (CONTRIBUTING.md)
- [x] Index de documentation (ce fichier)

### Phase 2 - À Venir
- [ ] Tutoriels vidéo
- [ ] Documentation interactive (Docusaurus)
- [ ] API Reference auto-générée (Swagger/OpenAPI)
- [ ] Exemples de projets complets
- [ ] FAQ détaillée
- [ ] Troubleshooting guide étendu

### Phase 3 - Futur
- [ ] Documentation multilingue (EN, FR, ES)
- [ ] Playground interactif
- [ ] Templates de projets
- [ ] Best practices par industrie
- [ ] Case studies

---

## Liens Utiles

### Documentation
- [README.md](./README.md) - Start here
- [AGENTS.md](./AGENTS.md) - Agent reference
- [WORKFLOWS.md](./WORKFLOWS.md) - Workflow guide
- [API.md](./API.md) - API reference
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guide

### Externe (À venir)
- Site web: https://devora.ai
- Documentation en ligne: https://docs.devora.ai
- API Reference: https://api.devora.ai/docs
- Blog: https://blog.devora.ai
- GitHub: https://github.com/devora-ai/orchestration

### Support
- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- Discord: Real-time chat
- Email: support@devora.ai

---

## Quick Links par Rôle

### Développeur Python
1. [Installation](./README.md#installation)
2. [Créer un agent](./CONTRIBUTING.md#créer-un-nouvel-agent)
3. [Standards de code](./CONTRIBUTING.md#standards-de-code)
4. [Tests](./CONTRIBUTING.md#tests)

### Product Manager
1. [Product Manager Agent](./AGENTS.md#1-product-manager-agent)
2. [Business Squad](./AGENTS.md#business-squad)
3. [Full Stack Workflow](./WORKFLOWS.md#1-full-stack-development)

### DevOps Engineer
1. [DevOps Squad](./AGENTS.md#devops-squad)
2. [CI/CD Setup Workflow](./WORKFLOWS.md#5-cicd-setup)
3. [Infrastructure Engineering](./AGENTS.md#13-infrastructure-engineer-agent)

### Frontend Developer
1. [UI/UX Designer](./AGENTS.md#4-uiux-designer-agent)
2. [Frontend Squad](./AGENTS.md#frontend-squad)
3. [Design Systems](./AGENTS.md#créer-un-design-system)

### API Developer
1. [API Architect](./AGENTS.md#7-api-architect-agent)
2. [API Development Workflow](./WORKFLOWS.md#2-api-development)
3. [Backend Squad](./AGENTS.md#backend-squad)

### Technical Writer
1. [Technical Writer Agent](./AGENTS.md#28-technical-writer-agent)
2. [Documentation Workflow](./WORKFLOWS.md#3-documentation-generation)
3. [Documentation Squad](./AGENTS.md#documentation-squad)

---

**Documentation Index maintenu par**: Documentation Squad
**Dernière mise à jour**: 2024-12-09
**Version**: 1.0

---

<div align="center">

**Devora Orchestration System**

[Accueil](./README.md) • [Agents](./AGENTS.md) • [Workflows](./WORKFLOWS.md) • [API](./API.md) • [Contribuer](./CONTRIBUTING.md)

</div>
