# DevOps Squad - Agents d'Orchestration Devora

Le DevOps Squad comprend 3 agents experts spécialisés dans l'infrastructure, la sécurité et le monitoring.

## Agents

### 1. InfrastructureEngineerAgent
**Responsabilités:**
- Configuration des déploiements (Vercel, Cloudflare, AWS, GCP)
- Génération de Dockerfiles et docker-compose.yml optimisés
- Création de pipelines CI/CD (GitHub Actions, GitLab CI)
- Gestion des environnements multi-stage (dev, staging, prod)
- Provisioning d'infrastructure as code (Terraform, Pulumi)

**Tâches supportées:**
- `dockerfile`: Génère un Dockerfile multi-stage optimisé
- `docker_compose`: Crée docker-compose.yml avec services (DB, cache, etc.)
- `ci_cd`: Configure pipeline CI/CD complet
- `terraform`: Génère infrastructure as code
- `deployment`: Configure le déploiement sur plateforme cible

**Exemple d'utilisation:**
```python
from orchestration.agents.devops_squad import InfrastructureEngineerAgent

agent = InfrastructureEngineerAgent(api_key="your-api-key")

# Générer un Dockerfile pour Next.js
result = await agent.generate_dockerfile(
    stack="nextjs",
    requirements="Production build avec Tailwind et TypeScript"
)

# Setup CI/CD pour déploiement Vercel
result = await agent.setup_ci_cd(
    stack="nextjs",
    platform="vercel",
    requirements="Tests E2E avec Playwright + déploiement preview"
)
```

---

### 2. SecurityEngineerAgent
**Responsabilités:**
- Audit de sécurité (OWASP Top 10, CVEs)
- Configuration de la gestion des secrets (Vault, AWS Secrets Manager)
- Implémentation du rate limiting et protection DDoS
- Configuration des headers de sécurité HTTP
- Scan des dépendances pour vulnérabilités
- Setup authentification et autorisation robustes

**Tâches supportées:**
- `audit`: Audit de sécurité complet du code
- `secrets`: Configuration du secret management
- `rate_limit`: Implémentation rate limiting multi-niveaux
- `headers`: Configuration headers de sécurité (CSP, HSTS, etc.)
- `dependencies`: Scan des CVEs dans les dépendances
- `auth`: Système d'authentification sécurisé (JWT, OAuth2, MFA)

**Exemple d'utilisation:**
```python
from orchestration.agents.devops_squad import SecurityEngineerAgent

agent = SecurityEngineerAgent(api_key="your-api-key")

# Auditer du code pour vulnérabilités
result = await agent.audit_code(
    code="""
    app.get('/user/:id', async (req, res) => {
        const user = await db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);
        res.json(user);
    });
    """,
    stack="nodejs"
)

# Configurer rate limiting
result = await agent.setup_rate_limiting(
    stack="nodejs",
    requirements="Protection API publique + login endpoint"
)

# Scanner les dépendances
result = await agent.scan_dependencies(
    package_file=open("package.json").read(),
    stack="nodejs"
)
```

---

### 3. MonitoringEngineerAgent
**Responsabilités:**
- Configuration Sentry (error tracking, performance, session replay)
- Création de dashboards temps réel (Grafana, Datadog)
- Définition et monitoring des SLO/SLA
- Implémentation des health checks (liveness, readiness, startup)
- Setup logging structuré et log aggregation
- Configuration d'alertes intelligentes avec escalation

**Tâches supportées:**
- `sentry`: Configuration complète Sentry
- `dashboards`: Dashboards Grafana pour Golden Signals
- `slo_sla`: Définition SLO/SLA et error budgets
- `health_checks`: Health checks multi-niveaux
- `logging`: Logging structuré JSON avec contexte
- `alerts`: Alertes intelligentes multi-canal

**Exemple d'utilisation:**
```python
from orchestration.agents.devops_squad import MonitoringEngineerAgent

agent = MonitoringEngineerAgent(api_key="your-api-key")

# Configurer Sentry
result = await agent.setup_sentry(
    stack="nextjs",
    service_name="web-app",
    requirements="Error tracking + performance + session replay"
)

# Créer des dashboards
result = await agent.create_dashboards(
    service_name="api",
    requirements="Golden Signals + business metrics"
)

# Définir SLO/SLA
result = await agent.define_slo_sla(
    service_name="api",
    requirements="99.9% uptime, p95 < 500ms"
)

# Setup health checks
result = await agent.implement_health_checks(
    stack="nodejs",
    service_name="api"
)
```

---

## Architecture du DevOps Squad

```
DevOps Squad
├── InfrastructureEngineerAgent
│   ├── Dockerfile generation
│   ├── Docker Compose orchestration
│   ├── CI/CD pipelines (GitHub Actions)
│   ├── Terraform IaC
│   └── Deployment configs (Vercel, Cloudflare)
│
├── SecurityEngineerAgent
│   ├── OWASP Top 10 auditing
│   ├── Secret management (Vault, AWS)
│   ├── Rate limiting + DDoS protection
│   ├── Security headers (CSP, HSTS)
│   ├── Dependency scanning (CVEs)
│   └── Auth implementation (JWT, OAuth2, MFA)
│
└── MonitoringEngineerAgent
    ├── Error tracking (Sentry)
    ├── Dashboards (Grafana)
    ├── SLO/SLA management
    ├── Health checks (K8s probes)
    ├── Structured logging (Pino, Loki)
    └── Intelligent alerting (Prometheus, PagerDuty)
```

---

## Workflows Typiques

### 1. Setup complet d'une nouvelle app
```python
import asyncio
from orchestration.agents.devops_squad import (
    InfrastructureEngineerAgent,
    SecurityEngineerAgent,
    MonitoringEngineerAgent
)

async def setup_new_app(api_key: str, stack: str, platform: str):
    # Initialiser les agents
    infra = InfrastructureEngineerAgent(api_key)
    security = SecurityEngineerAgent(api_key)
    monitoring = MonitoringEngineerAgent(api_key)

    # 1. Infrastructure
    print("Setting up infrastructure...")
    dockerfile = await infra.generate_dockerfile(stack=stack)
    docker_compose = await infra.generate_docker_compose(stack=stack)
    ci_cd = await infra.setup_ci_cd(stack=stack, platform=platform)

    # 2. Security
    print("Configuring security...")
    headers = await security.configure_security_headers(stack=stack)
    rate_limit = await security.setup_rate_limiting(stack=stack)
    secrets = await security.configure_secrets_management(stack=stack)

    # 3. Monitoring
    print("Setting up monitoring...")
    sentry = await monitoring.setup_sentry(stack=stack, service_name="app")
    health = await monitoring.implement_health_checks(stack=stack, service_name="app")
    logging = await monitoring.setup_logging(stack=stack)
    dashboards = await monitoring.create_dashboards(service_name="app")
    slo = await monitoring.define_slo_sla(service_name="app")

    print("✅ App setup complete!")

# Exécution
asyncio.run(setup_new_app(
    api_key="your-api-key",
    stack="nextjs",
    platform="vercel"
))
```

### 2. Audit de sécurité et correction
```python
async def security_audit_and_fix(api_key: str, codebase_path: str):
    security = SecurityEngineerAgent(api_key)

    # 1. Audit du code
    code = open(f"{codebase_path}/api/routes.ts").read()
    audit = await security.audit_code(code, stack="nodejs")

    # 2. Scan des dépendances
    package_json = open(f"{codebase_path}/package.json").read()
    deps_scan = await security.scan_dependencies(package_json, stack="nodejs")

    # 3. Vérifier headers
    headers = await security.configure_security_headers(stack="nodejs")

    # Analyser les résultats
    vulnerabilities = audit["vulnerabilities"]
    severity = audit["severity"]

    if severity in ["critical", "high"]:
        print(f"⚠️ {len(vulnerabilities)} vulnérabilités trouvées!")
        print("Vulnérabilités:", vulnerabilities)
    else:
        print("✅ Aucune vulnérabilité critique")

    return audit
```

### 3. Monitoring et SLO tracking
```python
async def setup_production_monitoring(api_key: str, service: str):
    monitoring = MonitoringEngineerAgent(api_key)

    # 1. Définir SLO/SLA
    slo = await monitoring.define_slo_sla(
        service_name=service,
        requirements="99.9% uptime, p95 < 500ms, < 0.1% error rate"
    )

    # 2. Créer dashboards
    dashboards = await monitoring.create_dashboards(
        service_name=service,
        requirements="Golden Signals + SLO compliance + business metrics"
    )

    # 3. Configurer alertes
    alerts = await monitoring.configure_alerts(
        service_name=service,
        requirements="P0: Service down, High error rate. P1: SLO burn rate"
    )

    # 4. Setup Sentry
    sentry = await monitoring.setup_sentry(
        stack="nodejs",
        service_name=service,
        requirements="Error tracking + performance + release tracking"
    )

    print("✅ Production monitoring configured!")
    print("SLO Target:", slo["metadata"])
```

---

## Best Practices

### Infrastructure
- Utiliser multi-stage builds pour Docker
- Versionner strictement les base images
- Cacher les dépendances dans CI/CD
- Séparer les environnements (dev/staging/prod)
- Automatiser 100% du déploiement

### Sécurité
- JAMAIS de secrets hardcodés
- Appliquer le principe du moindre privilège
- Auditer régulièrement les dépendances
- Configurer tous les headers de sécurité
- Implémenter rate limiting sur tous les endpoints publics

### Monitoring
- Logger en JSON structuré
- Définir des SLO mesurables
- Créer des alertes actionnables uniquement
- Inclure des runbooks dans chaque alerte
- Faire des postmortems blameless

---

## Intégration avec Orchestration

Les agents du DevOps Squad s'intègrent dans le workflow d'orchestration Devora:

```python
from orchestration.workflows import DevOpsWorkflow

workflow = DevOpsWorkflow(api_key="your-api-key")

result = await workflow.execute({
    "task": "deploy_new_feature",
    "stack": "nextjs",
    "platform": "vercel",
    "security_level": "high",
    "monitoring": "full"
})

# Le workflow orchestre automatiquement:
# 1. InfrastructureEngineer: Setup CI/CD
# 2. SecurityEngineer: Audit avant déploiement
# 3. MonitoringEngineer: Configure observability
```

---

## Configuration

### Variables d'environnement requises:
```bash
# API Keys
OPENROUTER_API_KEY=your-api-key

# Sentry (optionnel, pour monitoring)
SENTRY_DSN=your-sentry-dsn
SENTRY_AUTH_TOKEN=your-auth-token

# PagerDuty (optionnel, pour alerting)
PAGERDUTY_API_KEY=your-pagerduty-key

# Slack (optionnel, pour notifications)
SLACK_WEBHOOK_URL=your-slack-webhook
```

---

## Tests

```bash
# Installer les dépendances
pip install -r requirements.txt

# Tester les agents
pytest tests/agents/devops_squad/

# Tests spécifiques
pytest tests/agents/devops_squad/test_infrastructure_engineer.py
pytest tests/agents/devops_squad/test_security_engineer.py
pytest tests/agents/devops_squad/test_monitoring_engineer.py
```

---

## Documentation Additionnelle

- [Infrastructure Engineer Guide](./docs/infrastructure-guide.md)
- [Security Best Practices](./docs/security-best-practices.md)
- [Monitoring & Alerting Guide](./docs/monitoring-guide.md)
- [SLO/SLA Templates](./docs/slo-sla-templates.md)

---

## Support et Contribution

Pour toute question ou contribution:
- Ouvrir une issue sur GitHub
- Consulter la documentation Devora
- Rejoindre le canal #devops-squad sur Slack

---

**Dernière mise à jour:** 2025-12-09
**Version:** 1.0.0
**Auteur:** Devora Orchestration Team
