"""
Script de test pour les agents du DevOps Squad.

Ce script permet de tester rapidement les 3 agents du DevOps Squad
sans avoir besoin d'une suite de tests complète.

Usage:
    python test_agents.py --agent infrastructure --task dockerfile
    python test_agents.py --agent security --task audit
    python test_agents.py --agent monitoring --task sentry
"""

import asyncio
import os
import sys
import argparse
from typing import Dict, Any

# Ajouter le chemin pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from orchestration.agents.devops_squad import (
    InfrastructureEngineerAgent,
    SecurityEngineerAgent,
    MonitoringEngineerAgent
)


# ============================================================================
# Test Data
# ============================================================================

VULNERABLE_CODE = """
// Vulnerable Node.js code for testing
app.get('/user/:id', async (req, res) => {
    // SQL Injection vulnerability
    const user = await db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);

    // XSS vulnerability
    res.send(`<h1>Welcome ${req.query.name}</h1>`);

    // Hardcoded secrets
    const apiKey = "sk_live_123456789";
    const dbPassword = "admin123";

    // No rate limiting
    // No authentication check
    // No input validation
});

app.post('/login', async (req, res) => {
    const { email, password } = req.body;

    // Password stored in plain text
    const user = await db.query(`SELECT * FROM users WHERE email = '${email}' AND password = '${password}'`);

    if (user) {
        // No session management
        res.json({ success: true, user });
    }
});
"""

PACKAGE_JSON = """
{
  "name": "test-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "4.17.1",
    "lodash": "4.17.19",
    "axios": "0.21.1",
    "mongoose": "5.9.10"
  }
}
"""


# ============================================================================
# Test Functions
# ============================================================================

async def test_infrastructure_engineer(task: str, api_key: str):
    """Test InfrastructureEngineerAgent."""
    print("\n" + "="*80)
    print("Testing InfrastructureEngineerAgent")
    print("="*80 + "\n")

    agent = InfrastructureEngineerAgent(api_key=api_key)

    if task == "dockerfile":
        print("Task: Generate Dockerfile for Next.js\n")
        result = await agent.generate_dockerfile(
            stack="nextjs",
            requirements="Production build with TypeScript and Tailwind CSS"
        )

    elif task == "docker_compose":
        print("Task: Generate docker-compose.yml\n")
        result = await agent.generate_docker_compose(
            stack="nodejs",
            requirements="Include PostgreSQL and Redis"
        )

    elif task == "ci_cd":
        print("Task: Setup CI/CD pipeline\n")
        result = await agent.setup_ci_cd(
            stack="nextjs",
            platform="vercel",
            requirements="E2E tests with Playwright + preview deployments"
        )

    elif task == "terraform":
        print("Task: Generate Terraform configuration\n")
        result = await agent.provision_infrastructure(
            stack="nodejs",
            platform="aws",
            requirements="Production setup with RDS and ElastiCache"
        )

    elif task == "deployment":
        print("Task: Configure deployment\n")
        result = await agent.configure_deployment(
            stack="nextjs",
            platform="vercel",
            environment="production",
            requirements="Environment variables and build settings"
        )

    else:
        print(f"Unknown task: {task}")
        return

    print_result(result)


async def test_security_engineer(task: str, api_key: str):
    """Test SecurityEngineerAgent."""
    print("\n" + "="*80)
    print("Testing SecurityEngineerAgent")
    print("="*80 + "\n")

    agent = SecurityEngineerAgent(api_key=api_key)

    if task == "audit":
        print("Task: Security audit of vulnerable code\n")
        result = await agent.audit_code(
            code=VULNERABLE_CODE,
            stack="nodejs"
        )

    elif task == "secrets":
        print("Task: Configure secret management\n")
        result = await agent.configure_secrets_management(
            stack="nodejs",
            requirements="HashiCorp Vault with auto-rotation"
        )

    elif task == "rate_limit":
        print("Task: Setup rate limiting\n")
        result = await agent.setup_rate_limiting(
            stack="nodejs",
            requirements="API protection + login endpoint hardening"
        )

    elif task == "headers":
        print("Task: Configure security headers\n")
        result = await agent.configure_security_headers(stack="nextjs")

    elif task == "dependencies":
        print("Task: Scan dependencies for CVEs\n")
        result = await agent.scan_dependencies(
            package_file=PACKAGE_JSON,
            stack="nodejs"
        )

    elif task == "auth":
        print("Task: Implement authentication\n")
        result = await agent.implement_authentication(
            stack="nodejs",
            requirements="JWT + OAuth2 + MFA"
        )

    else:
        print(f"Unknown task: {task}")
        return

    print_result(result)

    # Print vulnerabilities if found
    if "vulnerabilities" in result and result["vulnerabilities"]:
        print("\n" + "-"*80)
        print(f"⚠️  VULNERABILITIES FOUND: {len(result['vulnerabilities'])}")
        print(f"Severity: {result['severity'].upper()}")
        print("-"*80)
        for vuln in result["vulnerabilities"][:5]:  # Show first 5
            print(f"  [{vuln['severity']}] {vuln['name']}")


async def test_monitoring_engineer(task: str, api_key: str):
    """Test MonitoringEngineerAgent."""
    print("\n" + "="*80)
    print("Testing MonitoringEngineerAgent")
    print("="*80 + "\n")

    agent = MonitoringEngineerAgent(api_key=api_key)

    if task == "sentry":
        print("Task: Configure Sentry\n")
        result = await agent.setup_sentry(
            stack="nextjs",
            service_name="web-app",
            requirements="Error tracking + performance + session replay"
        )

    elif task == "dashboards":
        print("Task: Create monitoring dashboards\n")
        result = await agent.create_dashboards(
            service_name="api",
            requirements="Golden Signals + business metrics + SLO compliance"
        )

    elif task == "slo_sla":
        print("Task: Define SLO/SLA\n")
        result = await agent.define_slo_sla(
            service_name="api",
            requirements="99.9% uptime, p95 < 500ms, error rate < 0.1%"
        )

    elif task == "health_checks":
        print("Task: Implement health checks\n")
        result = await agent.implement_health_checks(
            stack="nodejs",
            service_name="api"
        )

    elif task == "logging":
        print("Task: Setup structured logging\n")
        result = await agent.setup_logging(
            stack="nodejs",
            requirements="JSON logging with Loki aggregation"
        )

    elif task == "alerts":
        print("Task: Configure alerts\n")
        result = await agent.configure_alerts(
            service_name="api",
            requirements="P0: Service down. P1: High error rate, SLO burn rate"
        )

    else:
        print(f"Unknown task: {task}")
        return

    print_result(result)


def print_result(result: Dict[str, Any]):
    """Pretty print agent result."""
    print("\n" + "-"*80)
    print("RESULT")
    print("-"*80)

    print(f"\nStatus: {result['status']}")

    if result.get('metadata'):
        print(f"\nMetadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")

    if result.get('files'):
        print(f"\nFiles generated: {len(result['files'])}")
        for file in result['files']:
            print(f"  - {file['path']}")

    if result.get('config_files'):
        print(f"\nConfig files: {len(result['config_files'])}")
        for file in result['config_files']:
            print(f"  - {file['path']}")

    print(f"\n{'-'*80}")
    print("OUTPUT")
    print("-"*80)
    print(result['output'][:2000])  # Print first 2000 chars
    if len(result['output']) > 2000:
        print(f"\n... (truncated, total {len(result['output'])} chars)")

    print("\n" + "="*80 + "\n")


# ============================================================================
# Main
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Test DevOps Squad agents")
    parser.add_argument(
        "--agent",
        choices=["infrastructure", "security", "monitoring"],
        required=True,
        help="Agent to test"
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Task to execute (varies by agent)"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENROUTER_API_KEY"),
        help="OpenRouter API key (or set OPENROUTER_API_KEY env var)"
    )

    args = parser.parse_args()

    if not args.api_key:
        print("❌ Error: API key required. Set OPENROUTER_API_KEY or use --api-key")
        sys.exit(1)

    try:
        if args.agent == "infrastructure":
            await test_infrastructure_engineer(args.task, args.api_key)
        elif args.agent == "security":
            await test_security_engineer(args.task, args.api_key)
        elif args.agent == "monitoring":
            await test_monitoring_engineer(args.task, args.api_key)

        print("✅ Test completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
