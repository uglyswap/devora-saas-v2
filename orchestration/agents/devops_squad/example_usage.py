"""
DevOps Squad - Exemples d'utilisation pratiques

Ce fichier contient des exemples concrets d'utilisation des 3 agents du DevOps Squad
dans différents scénarios réels.

Usage:
    python example_usage.py --scenario setup_new_app
    python example_usage.py --scenario security_audit
    python example_usage.py --scenario production_monitoring
    python example_usage.py --scenario full_devops_pipeline
"""

import asyncio
import os
import sys
import argparse
from typing import Dict, Any

# Imports des agents
from orchestration.agents.devops_squad import (
    InfrastructureEngineerAgent,
    SecurityEngineerAgent,
    MonitoringEngineerAgent
)


# ============================================================================
# Scenario 1: Setup complet d'une nouvelle application
# ============================================================================

async def scenario_setup_new_app(api_key: str):
    """
    Setup complet d'une nouvelle application Next.js avec:
    - Infrastructure (Docker, CI/CD, déploiement)
    - Sécurité (headers, rate limiting, secrets)
    - Monitoring (Sentry, dashboards, SLO)
    """
    print("\n" + "="*80)
    print("SCENARIO 1: Setup d'une nouvelle application Next.js")
    print("="*80 + "\n")

    # Initialiser les agents
    infra = InfrastructureEngineerAgent(api_key=api_key)
    security = SecurityEngineerAgent(api_key=api_key)
    monitoring = MonitoringEngineerAgent(api_key=api_key)

    # ========== PHASE 1: INFRASTRUCTURE ==========
    print("\n[1/3] 🏗️  Configuration de l'infrastructure...\n")

    # Générer Dockerfile
    print("  → Génération du Dockerfile...")
    dockerfile = await infra.execute({
        "task_type": "dockerfile",
        "stack": "nextjs",
        "requirements": "Production build avec TypeScript, Tailwind CSS, optimisé pour Vercel"
    })
    print(f"    ✓ Dockerfile généré ({len(dockerfile['files'])} fichiers)")

    # Générer docker-compose pour dev local
    print("  → Génération de docker-compose.yml...")
    compose = await infra.execute({
        "task_type": "docker_compose",
        "stack": "nextjs",
        "requirements": "PostgreSQL 15, Redis pour cache, volumes persistants"
    })
    print(f"    ✓ Docker Compose configuré")

    # Setup CI/CD
    print("  → Configuration du pipeline CI/CD...")
    cicd = await infra.execute({
        "task_type": "ci_cd",
        "stack": "nextjs",
        "platform": "vercel",
        "requirements": "Tests E2E avec Playwright, preview deployments, auto-deploy production"
    })
    print(f"    ✓ Pipeline CI/CD créé")

    # ========== PHASE 2: SÉCURITÉ ==========
    print("\n[2/3] 🔒 Configuration de la sécurité...\n")

    # Headers de sécurité
    print("  → Configuration des headers de sécurité...")
    headers = await security.execute({
        "task_type": "headers",
        "stack": "nextjs"
    })
    print(f"    ✓ Headers sécurisés (CSP, HSTS, etc.)")

    # Rate limiting
    print("  → Setup du rate limiting...")
    rate_limit = await security.execute({
        "task_type": "rate_limit",
        "stack": "nodejs",
        "requirements": "Protection API /api/*, login endpoint avec captcha après 5 tentatives"
    })
    print(f"    ✓ Rate limiting configuré")

    # Gestion des secrets
    print("  → Configuration du secret management...")
    secrets = await security.execute({
        "task_type": "secrets",
        "stack": "nodejs",
        "requirements": "Vercel Environment Variables + dotenv pour dev local"
    })
    print(f"    ✓ Secrets management configuré")

    # ========== PHASE 3: MONITORING ==========
    print("\n[3/3] 📊 Configuration du monitoring...\n")

    # Sentry
    print("  → Setup de Sentry...")
    sentry = await monitoring.execute({
        "task_type": "sentry",
        "stack": "nextjs",
        "service_name": "webapp",
        "requirements": "Error tracking, performance monitoring, session replay"
    })
    print(f"    ✓ Sentry configuré")

    # Health checks
    print("  → Implémentation des health checks...")
    health = await monitoring.execute({
        "task_type": "health_checks",
        "stack": "nodejs",
        "service_name": "webapp"
    })
    print(f"    ✓ Health checks implémentés")

    # Dashboards
    print("  → Création des dashboards...")
    dashboards = await monitoring.execute({
        "task_type": "dashboards",
        "service_name": "webapp",
        "requirements": "Golden Signals (latency, traffic, errors, saturation) + business metrics"
    })
    print(f"    ✓ Dashboards créés")

    # SLO/SLA
    print("  → Définition des SLO/SLA...")
    slo = await monitoring.execute({
        "task_type": "slo_sla",
        "service_name": "webapp",
        "requirements": "99.9% uptime, p95 latency < 500ms, error rate < 0.1%"
    })
    print(f"    ✓ SLO/SLA définis")

    print("\n" + "="*80)
    print("✅ APPLICATION SETUP COMPLETE!")
    print("="*80)
    print("\nFichiers générés:")
    print(f"  - Infrastructure: {len(dockerfile['files']) + len(compose['files']) + len(cicd['files'])} fichiers")
    print(f"  - Sécurité: {len(headers.get('config_files', [])) + len(rate_limit.get('config_files', [])) + len(secrets.get('config_files', []))} fichiers")
    print(f"  - Monitoring: {len(sentry.get('config_files', [])) + len(health.get('config_files', [])) + len(dashboards.get('config_files', []))} fichiers")


# ============================================================================
# Scenario 2: Audit de sécurité complet
# ============================================================================

async def scenario_security_audit(api_key: str):
    """
    Audit de sécurité complet d'une application existante:
    - Analyse du code pour OWASP Top 10
    - Scan des dépendances (CVEs)
    - Vérification des headers
    - Recommandations de correction
    """
    print("\n" + "="*80)
    print("SCENARIO 2: Audit de sécurité complet")
    print("="*80 + "\n")

    security = SecurityEngineerAgent(api_key=api_key)

    # Code vulnérable pour démonstration
    vulnerable_code = """
    // API endpoint vulnérable
    app.post('/api/users', async (req, res) => {
        const { email, password, role } = req.body;

        // SQL Injection vulnerability
        const query = `INSERT INTO users (email, password, role) VALUES ('${email}', '${password}', '${role}')`;
        await db.query(query);

        // XSS vulnerability
        res.send(`<h1>Welcome ${req.body.name}!</h1>`);

        // Hardcoded secrets
        const apiKey = "sk_live_1234567890abcdef";
        const stripeKey = "rk_live_abcdefghijklmnop";
    });

    app.get('/api/admin/users', async (req, res) => {
        // No authentication check
        // No authorization check
        const users = await db.query('SELECT * FROM users');
        res.json(users);
    });
    """

    package_json = """{
        "name": "vulnerable-app",
        "dependencies": {
            "express": "4.16.0",
            "lodash": "4.17.15",
            "axios": "0.21.1",
            "mongoose": "5.7.5"
        }
    }"""

    # ========== AUDIT DU CODE ==========
    print("[1/4] 🔍 Audit du code source...\n")
    audit = await security.execute({
        "task_type": "audit",
        "code": vulnerable_code,
        "stack": "nodejs"
    })

    print(f"  Statut: {audit['status']}")
    print(f"  Sévérité globale: {audit['severity'].upper()}")
    print(f"  Vulnérabilités trouvées: {len(audit.get('vulnerabilities', []))}\n")

    if audit.get('vulnerabilities'):
        print("  Top vulnerabilities:")
        for vuln in audit['vulnerabilities'][:5]:
            print(f"    [{vuln['severity'].upper()}] {vuln['name']}")
            print(f"      → {vuln.get('description', 'No description')[:80]}...")

    # ========== SCAN DES DÉPENDANCES ==========
    print("\n[2/4] 📦 Scan des dépendances...\n")
    deps_scan = await security.execute({
        "task_type": "dependencies",
        "package_file": package_json,
        "stack": "nodejs"
    })

    print(f"  CVEs trouvées: {len(deps_scan.get('vulnerabilities', []))}")
    if deps_scan.get('vulnerabilities'):
        critical = [v for v in deps_scan['vulnerabilities'] if v['severity'] == 'critical']
        high = [v for v in deps_scan['vulnerabilities'] if v['severity'] == 'high']
        print(f"    - Critical: {len(critical)}")
        print(f"    - High: {len(high)}")

    # ========== HEADERS DE SÉCURITÉ ==========
    print("\n[3/4] 🛡️  Vérification des headers de sécurité...\n")
    headers = await security.execute({
        "task_type": "headers",
        "stack": "nodejs"
    })

    print(f"  Configuration générée pour:")
    print(f"    - Content Security Policy (CSP)")
    print(f"    - HSTS (HTTP Strict Transport Security)")
    print(f"    - X-Frame-Options, X-Content-Type-Options")
    print(f"    - Referrer-Policy, Permissions-Policy")

    # ========== RECOMMANDATIONS ==========
    print("\n[4/4] 💡 Recommandations...\n")
    print(f"  Actions prioritaires:")
    print(f"    1. Corriger les vulnérabilités CRITICAL immédiatement")
    print(f"    2. Mettre à jour les dépendances vulnérables")
    print(f"    3. Implémenter les headers de sécurité manquants")
    print(f"    4. Ajouter authentication/authorization sur les endpoints sensibles")
    print(f"    5. Setup rate limiting sur les endpoints publics")

    print("\n" + "="*80)
    print("✅ AUDIT COMPLETE!")
    print("="*80)


# ============================================================================
# Scenario 3: Setup monitoring production
# ============================================================================

async def scenario_production_monitoring(api_key: str):
    """
    Setup complet du monitoring pour une app en production:
    - Sentry (errors + performance)
    - Dashboards temps réel
    - SLO/SLA tracking
    - Alertes intelligentes
    """
    print("\n" + "="*80)
    print("SCENARIO 3: Setup monitoring production")
    print("="*80 + "\n")

    monitoring = MonitoringEngineerAgent(api_key=api_key)

    # ========== SENTRY ==========
    print("[1/5] 🐛 Configuration de Sentry...\n")
    sentry = await monitoring.execute({
        "task_type": "sentry",
        "stack": "nextjs",
        "service_name": "production-api",
        "requirements": "Error tracking + performance monitoring + session replay + release tracking"
    })

    print(f"  ✓ Sentry configuré")
    print(f"    - Error tracking avec source maps")
    print(f"    - Performance monitoring (p95, p99)")
    print(f"    - Session replay pour debug")
    print(f"    - Release tracking avec Git SHA")

    # ========== DASHBOARDS ==========
    print("\n[2/5] 📊 Création des dashboards...\n")
    dashboards = await monitoring.execute({
        "task_type": "dashboards",
        "service_name": "production-api",
        "requirements": "Golden Signals + SLO compliance + business metrics (signups, conversions, revenue)"
    })

    print(f"  ✓ Dashboards créés:")
    print(f"    - Golden Signals (latency, traffic, errors, saturation)")
    print(f"    - SLO compliance tracking")
    print(f"    - Business metrics (KPIs)")
    print(f"    - Infrastructure metrics (CPU, RAM, Disk)")

    # ========== SLO/SLA ==========
    print("\n[3/5] 🎯 Définition des SLO/SLA...\n")
    slo = await monitoring.execute({
        "task_type": "slo_sla",
        "service_name": "production-api",
        "requirements": "99.95% uptime (21.6min downtime/month), p95 < 300ms, p99 < 1s, error rate < 0.05%"
    })

    print(f"  ✓ SLO/SLA définis:")
    print(f"    - Uptime: 99.95% (error budget: 21.6min/month)")
    print(f"    - Latency: p95 < 300ms, p99 < 1s")
    print(f"    - Error rate: < 0.05%")
    print(f"    - Burn rate alerts configurées")

    # ========== HEALTH CHECKS ==========
    print("\n[4/5] 🏥 Implémentation des health checks...\n")
    health = await monitoring.execute({
        "task_type": "health_checks",
        "stack": "nodejs",
        "service_name": "production-api"
    })

    print(f"  ✓ Health checks implémentés:")
    print(f"    - /health/liveness (simple ping)")
    print(f"    - /health/readiness (DB + Redis check)")
    print(f"    - /health/startup (warmup check)")

    # ========== ALERTES ==========
    print("\n[5/5] 🚨 Configuration des alertes...\n")
    alerts = await monitoring.execute({
        "task_type": "alerts",
        "service_name": "production-api",
        "requirements": "P0: Service down, P1: High error rate + SLO burn rate, P2: Latency degradation"
    })

    print(f"  ✓ Alertes configurées:")
    print(f"    - P0 (Critical): Service down → PagerDuty + SMS")
    print(f"    - P1 (High): Error rate > 1% → PagerDuty")
    print(f"    - P1 (High): SLO burn rate too fast → PagerDuty")
    print(f"    - P2 (Medium): Latency p95 > 500ms → Slack")
    print(f"    - P2 (Medium): Memory > 80% → Slack")

    print("\n" + "="*80)
    print("✅ PRODUCTION MONITORING CONFIGURED!")
    print("="*80)
    print("\nNext steps:")
    print("  1. Deploy les config files générés")
    print("  2. Configurer les credentials (SENTRY_DSN, PAGERDUTY_KEY, etc.)")
    print("  3. Tester les alertes en staging")
    print("  4. Créer le runbook pour on-call engineers")


# ============================================================================
# Scenario 4: Pipeline DevOps complet
# ============================================================================

async def scenario_full_devops_pipeline(api_key: str):
    """
    Pipeline DevOps complet de A à Z:
    - Infrastructure as Code (Terraform)
    - CI/CD multi-environnements
    - Security hardening
    - Monitoring & observability
    """
    print("\n" + "="*80)
    print("SCENARIO 4: Pipeline DevOps complet")
    print("="*80 + "\n")

    infra = InfrastructureEngineerAgent(api_key=api_key)
    security = SecurityEngineerAgent(api_key=api_key)
    monitoring = MonitoringEngineerAgent(api_key=api_key)

    # ========== TERRAFORM ==========
    print("[1/6] 🏗️  Infrastructure as Code (Terraform)...\n")
    terraform = await infra.execute({
        "task_type": "terraform",
        "stack": "nodejs",
        "platform": "aws",
        "requirements": "ECS Fargate + RDS PostgreSQL + ElastiCache Redis + S3 + CloudFront"
    })
    print(f"  ✓ Terraform configuration générée")

    # ========== CI/CD ==========
    print("\n[2/6] 🔄 Pipeline CI/CD multi-environnements...\n")
    cicd = await infra.execute({
        "task_type": "ci_cd",
        "stack": "nodejs",
        "platform": "aws",
        "requirements": "Deploy vers dev/staging/prod, E2E tests, security scanning, auto-rollback"
    })
    print(f"  ✓ Pipeline CI/CD configuré (dev → staging → prod)")

    # ========== SECURITY HARDENING ==========
    print("\n[3/6] 🔒 Security hardening...\n")

    # Authentication
    auth = await security.execute({
        "task_type": "auth",
        "stack": "nodejs",
        "requirements": "JWT + OAuth2 + MFA + refresh tokens"
    })
    print(f"  ✓ Authentication robuste implémentée")

    # Rate limiting
    rate_limit = await security.execute({
        "task_type": "rate_limit",
        "stack": "nodejs",
        "requirements": "API-level + User-level + IP-level rate limiting"
    })
    print(f"  ✓ Rate limiting multi-niveaux configuré")

    # ========== LOGGING ==========
    print("\n[4/6] 📝 Logging structuré...\n")
    logging = await monitoring.execute({
        "task_type": "logging",
        "stack": "nodejs",
        "requirements": "JSON logging + Loki aggregation + correlation IDs + sensitive data masking"
    })
    print(f"  ✓ Logging structuré implémenté")

    # ========== DASHBOARDS ==========
    print("\n[5/6] 📊 Observability dashboards...\n")
    dashboards = await monitoring.execute({
        "task_type": "dashboards",
        "service_name": "full-stack-app",
        "requirements": "Complete observability: infrastructure + application + business metrics"
    })
    print(f"  ✓ Dashboards complets créés")

    # ========== DEPLOYMENT ==========
    print("\n[6/6] 🚀 Configuration du déploiement...\n")
    deployment = await infra.execute({
        "task_type": "deployment",
        "stack": "nodejs",
        "platform": "aws",
        "environment": "production",
        "requirements": "Blue-green deployment + health checks + auto-scaling + CDN"
    })
    print(f"  ✓ Déploiement production configuré")

    print("\n" + "="*80)
    print("✅ FULL DEVOPS PIPELINE READY!")
    print("="*80)
    print("\nPipeline summary:")
    print("  ✓ Infrastructure: Terraform IaC sur AWS")
    print("  ✓ CI/CD: Multi-env avec tests automatisés")
    print("  ✓ Security: Auth + rate limiting + secrets management")
    print("  ✓ Monitoring: Sentry + dashboards + alertes")
    print("  ✓ Deployment: Blue-green avec auto-rollback")
    print("\nTotal fichiers générés: ~50+")


# ============================================================================
# Main
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Exemples d'utilisation du DevOps Squad",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scénarios disponibles:
  setup_new_app          - Setup complet d'une nouvelle app Next.js
  security_audit         - Audit de sécurité complet avec recommandations
  production_monitoring  - Configuration monitoring pour production
  full_devops_pipeline   - Pipeline DevOps complet de A à Z

Exemples:
  python example_usage.py --scenario setup_new_app
  python example_usage.py --scenario security_audit --api-key YOUR_KEY
  python example_usage.py --scenario production_monitoring
  python example_usage.py --scenario full_devops_pipeline
        """
    )
    parser.add_argument(
        "--scenario",
        choices=["setup_new_app", "security_audit", "production_monitoring", "full_devops_pipeline"],
        required=True,
        help="Scénario à exécuter"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENROUTER_API_KEY"),
        help="OpenRouter API key (ou set OPENROUTER_API_KEY env var)"
    )

    args = parser.parse_args()

    if not args.api_key:
        print("❌ Error: API key required. Set OPENROUTER_API_KEY or use --api-key")
        sys.exit(1)

    try:
        if args.scenario == "setup_new_app":
            await scenario_setup_new_app(args.api_key)
        elif args.scenario == "security_audit":
            await scenario_security_audit(args.api_key)
        elif args.scenario == "production_monitoring":
            await scenario_production_monitoring(args.api_key)
        elif args.scenario == "full_devops_pipeline":
            await scenario_full_devops_pipeline(args.api_key)

        print("\n✅ Scenario completed successfully!\n")

    except Exception as e:
        print(f"\n❌ Error during scenario execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
