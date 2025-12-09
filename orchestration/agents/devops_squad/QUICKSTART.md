# DevOps Squad - Guide de Démarrage Rapide

Guide rapide pour utiliser les agents du DevOps Squad.

## Installation

```bash
# Depuis la racine du projet
cd devora-transformation

# Installer les dépendances Python
pip install httpx python-dotenv

# Configurer l'API key
export OPENROUTER_API_KEY="your-api-key-here"
```

## Test Rapide des Agents

```bash
cd orchestration/agents/devops_squad

# Test Infrastructure Engineer
python test_agents.py --agent infrastructure --task dockerfile
python test_agents.py --agent infrastructure --task ci_cd

# Test Security Engineer
python test_agents.py --agent security --task audit
python test_agents.py --agent security --task rate_limit

# Test Monitoring Engineer
python test_agents.py --agent monitoring --task sentry
python test_agents.py --agent monitoring --task slo_sla
```

## Exemples d'Utilisation

### 1. Infrastructure Engineer - Générer un Dockerfile

```python
import asyncio
from orchestration.agents.devops_squad import InfrastructureEngineerAgent

async def generate_dockerfile():
    agent = InfrastructureEngineerAgent(api_key="your-api-key")

    result = await agent.generate_dockerfile(
        stack="nextjs",
        requirements="Production build avec TypeScript, Tailwind, et optimisation d'images"
    )

    # Sauvegarder le Dockerfile
    for file in result["files"]:
        with open(file["path"], "w") as f:
            f.write(file["content"])

    print(f"✅ {len(result['files'])} fichiers créés")

asyncio.run(generate_dockerfile())
```

### 2. Security Engineer - Audit de Sécurité

```python
import asyncio
from orchestration.agents.devops_squad import SecurityEngineerAgent

async def audit_security():
    agent = SecurityEngineerAgent(api_key="your-api-key")

    # Lire le code à auditer
    with open("src/api/routes.ts", "r") as f:
        code = f.read()

    result = await agent.audit_code(code, stack="nodejs")

    # Analyser les résultats
    print(f"Sévérité: {result['severity']}")
    print(f"Vulnérabilités trouvées: {len(result['vulnerabilities'])}")

    for vuln in result["vulnerabilities"]:
        print(f"  [{vuln['severity']}] {vuln['name']}")

    # Sauvegarder le rapport
    with open("security-audit-report.md", "w") as f:
        f.write(result["output"])

asyncio.run(audit_security())
```

### 3. Monitoring Engineer - Setup Complet

```python
import asyncio
from orchestration.agents.devops_squad import MonitoringEngineerAgent

async def setup_monitoring():
    agent = MonitoringEngineerAgent(api_key="your-api-key")

    service_name = "my-api"

    # 1. Configurer Sentry
    print("Setting up Sentry...")
    sentry = await agent.setup_sentry(
        stack="nextjs",
        service_name=service_name,
        requirements="Error tracking + performance monitoring"
    )

    # 2. Définir SLO/SLA
    print("Defining SLO/SLA...")
    slo = await agent.define_slo_sla(
        service_name=service_name,
        requirements="99.9% uptime, p95 < 500ms"
    )

    # 3. Créer dashboards
    print("Creating dashboards...")
    dashboards = await agent.create_dashboards(
        service_name=service_name,
        requirements="Golden Signals + business metrics"
    )

    # 4. Configurer alertes
    print("Configuring alerts...")
    alerts = await agent.configure_alerts(
        service_name=service_name,
        requirements="P0: Service down, P1: High error rate"
    )

    print("✅ Monitoring setup complete!")

asyncio.run(setup_monitoring())
```

## Workflows Complets

### Setup d'une Nouvelle Application

```python
import asyncio
from orchestration.agents.devops_squad import (
    InfrastructureEngineerAgent,
    SecurityEngineerAgent,
    MonitoringEngineerAgent
)

async def setup_new_app():
    api_key = "your-api-key"

    # Initialiser les agents
    infra = InfrastructureEngineerAgent(api_key)
    security = SecurityEngineerAgent(api_key)
    monitoring = MonitoringEngineerAgent(api_key)

    # 1. INFRASTRUCTURE
    print("\n📦 Setting up infrastructure...")

    # Dockerfile
    dockerfile = await infra.generate_dockerfile(stack="nextjs")
    save_files(dockerfile["files"])

    # Docker Compose
    compose = await infra.generate_docker_compose(stack="nextjs")
    save_files(compose["files"])

    # CI/CD
    cicd = await infra.setup_ci_cd(
        stack="nextjs",
        platform="vercel",
        requirements="Tests + preview deployments"
    )
    save_files(cicd["files"])

    # 2. SECURITY
    print("\n🔒 Configuring security...")

    # Security headers
    headers = await security.configure_security_headers(stack="nextjs")

    # Rate limiting
    rate_limit = await security.setup_rate_limiting(stack="nextjs")

    # Secret management
    secrets = await security.configure_secrets_management(stack="nextjs")

    # 3. MONITORING
    print("\n📊 Setting up monitoring...")

    # Sentry
    sentry = await monitoring.setup_sentry(
        stack="nextjs",
        service_name="app"
    )
    save_files(sentry["config_files"])

    # Health checks
    health = await monitoring.implement_health_checks(
        stack="nextjs",
        service_name="app"
    )

    # SLO/SLA
    slo = await monitoring.define_slo_sla(service_name="app")

    # Dashboards
    dashboards = await monitoring.create_dashboards(service_name="app")

    print("\n✅ Application setup complete!")
    print("\nNext steps:")
    print("1. Review generated files")
    print("2. Update environment variables")
    print("3. Test locally: docker-compose up")
    print("4. Deploy: git push")

def save_files(files):
    """Helper to save generated files."""
    for file in files:
        path = file["path"]
        content = file["content"]

        # Create directories if needed
        import os
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        with open(path, "w") as f:
            f.write(content)

        print(f"  ✓ Created {path}")

asyncio.run(setup_new_app())
```

### Audit de Sécurité Complet

```python
import asyncio
from orchestration.agents.devops_squad import SecurityEngineerAgent

async def security_audit_pipeline():
    agent = SecurityEngineerAgent(api_key="your-api-key")

    print("\n🔍 Starting security audit...\n")

    # 1. Audit du code
    print("1. Auditing code...")
    code_files = ["src/api/routes.ts", "src/lib/auth.ts"]
    for file_path in code_files:
        with open(file_path) as f:
            code = f.read()

        audit = await agent.audit_code(code, stack="nodejs")

        if audit["severity"] in ["critical", "high"]:
            print(f"   ⚠️  {file_path}: {audit['severity']} issues found")
        else:
            print(f"   ✓ {file_path}: OK")

    # 2. Scan des dépendances
    print("\n2. Scanning dependencies...")
    with open("package.json") as f:
        package_json = f.read()

    deps = await agent.scan_dependencies(package_json, stack="nodejs")

    if deps["vulnerabilities"]:
        print(f"   ⚠️  {len(deps['vulnerabilities'])} CVEs found")
    else:
        print("   ✓ No known vulnerabilities")

    # 3. Vérification des headers
    print("\n3. Checking security headers...")
    headers = await agent.configure_security_headers(stack="nodejs")
    print("   ✓ Headers configuration generated")

    # 4. Génération du rapport
    print("\n4. Generating report...")
    report = f"""
# Security Audit Report

Date: {datetime.now().isoformat()}

## Code Audit
{audit['output']}

## Dependencies Scan
{deps['output']}

## Security Headers
{headers['output']}
"""

    with open("security-audit-report.md", "w") as f:
        f.write(report)

    print("\n✅ Audit complete! Report saved to security-audit-report.md")

from datetime import datetime
asyncio.run(security_audit_pipeline())
```

## Tâches Disponibles par Agent

### Infrastructure Engineer
- `dockerfile` - Générer Dockerfile optimisé
- `docker_compose` - Créer docker-compose.yml
- `ci_cd` - Setup pipeline CI/CD
- `terraform` - Configuration Terraform
- `deployment` - Config déploiement (Vercel, Cloudflare, etc.)

### Security Engineer
- `audit` - Audit de sécurité OWASP
- `secrets` - Gestion des secrets
- `rate_limit` - Rate limiting
- `headers` - Headers de sécurité
- `dependencies` - Scan CVEs
- `auth` - Système d'authentification

### Monitoring Engineer
- `sentry` - Configuration Sentry
- `dashboards` - Dashboards Grafana
- `slo_sla` - Définition SLO/SLA
- `health_checks` - Health checks
- `logging` - Logging structuré
- `alerts` - Alertes intelligentes

## Configuration Avancée

### Utiliser un modèle différent

```python
agent = InfrastructureEngineerAgent(
    api_key="your-api-key",
    model="anthropic/claude-3.5-sonnet"  # ou "openai/gpt-4o-mini"
)
```

### Accéder à la mémoire de l'agent

```python
# L'agent conserve l'historique des conversations
result1 = await agent.generate_dockerfile(stack="nextjs")
result2 = await agent.generate_docker_compose(stack="nextjs")

# Récupérer la mémoire
memory = agent.get_memory()
print(f"Conversations: {len(memory)}")

# Effacer la mémoire
agent.clear_memory()
```

### Personnaliser le system prompt

```python
agent = SecurityEngineerAgent(
    api_key="your-api-key",
    system_prompt="""Tu es un expert en sécurité web.
    Focus sur les vulnérabilités critiques OWASP Top 10.
    Fournis toujours des exemples de code corrigé."""
)
```

## Troubleshooting

### Erreur d'import
```bash
# Vérifier le PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/devora-transformation"

# Ou utiliser le chemin absolu
import sys
sys.path.insert(0, "/path/to/devora-transformation")
```

### Timeout API
```python
# Le timeout par défaut est 120s
# Pour des tâches complexes, augmenter le timeout dans call_llm:
result = await agent.call_llm(
    messages=[...],
    timeout=300.0  # 5 minutes
)
```

### Rate limiting OpenRouter
```python
import asyncio

# Ajouter un délai entre les requêtes
await agent.generate_dockerfile(...)
await asyncio.sleep(2)  # 2 secondes de pause
await agent.generate_docker_compose(...)
```

## Ressources

- [README complet](./README.md)
- [Documentation BaseAgent](../core/base_agent.py)
- [Exemples de workflows](../../workflows/)
- [Tests unitaires](../../../tests/agents/devops_squad/)

## Support

Questions? Ouvrez une issue sur GitHub ou contactez l'équipe Devora.

---

**Happy DevOpsing! 🚀**
