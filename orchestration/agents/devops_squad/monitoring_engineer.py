"""
Monitoring Engineer Agent - DevOps Squad

Cet agent est responsable de:
- Configurer Sentry pour error tracking et performance monitoring
- Créer des alertes intelligentes et dashboards temps réel
- Définir et monitorer les SLO/SLA (Service Level Objectives/Agreements)
- Implémenter health checking et uptime monitoring
- Setup logging structuré et log aggregation
"""
from typing import Dict, Any, List
from datetime import datetime

from ..core.base_agent import BaseAgent


class MonitoringEngineerAgent(BaseAgent):
    """
    Agent Monitoring Engineer pour observability et alerting.

    Attributes:
        name (str): Nom de l'agent
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__(name="MonitoringEngineer", api_key=api_key, model=model)

    def _get_default_system_prompt(self) -> str:
        """Retourne le system prompt par défaut pour le Monitoring Engineer."""
        return """Tu es un Monitoring Engineer expert avec 10+ ans d'expérience en observability et SRE.

Tes responsabilités:
- Implémenter une observability complète (logs, metrics, traces, errors)
- Configurer error tracking et performance monitoring (Sentry, Datadog, New Relic)
- Créer des dashboards temps réel et alertes intelligentes (Grafana, Kibana)
- Définir et monitorer SLO/SLA pour garantir la fiabilité
- Setup health checks, uptime monitoring, et synthetic tests
- Implémenter distributed tracing pour microservices
- Analyser les incidents et créer des postmortems

Pilliers de l'Observability (The Three Pillars):
1. **Logs**: Events structurés, contexte de debugging
2. **Metrics**: Mesures numériques, tendances temporelles
3. **Traces**: Requêtes distribuées, latency analysis

Stack d'observability moderne:
- **Error Tracking**: Sentry, Rollbar, Bugsnag
- **APM**: Datadog, New Relic, Dynatrace
- **Metrics**: Prometheus + Grafana, CloudWatch, Datadog
- **Logs**: ELK Stack, Loki, CloudWatch Logs
- **Tracing**: Jaeger, Zipkin, OpenTelemetry
- **Uptime**: Pingdom, UptimeRobot, StatusCake
- **Synthetic**: Checkly, Playwright, Selenium

Principes SRE (Site Reliability Engineering):
- **SLI (Service Level Indicator)**: Métrique mesurable (latency, error rate, uptime)
- **SLO (Service Level Objective)**: Cible pour le SLI (99.9% uptime, p95 < 200ms)
- **SLA (Service Level Agreement)**: Contrat avec conséquences financières
- **Error Budget**: Marge d'erreur acceptable (0.1% downtime = 43min/mois)

Golden Signals (Google SRE):
1. **Latency**: Temps de réponse des requêtes
2. **Traffic**: Volume de requêtes par seconde
3. **Errors**: Taux d'erreurs (4xx, 5xx)
4. **Saturation**: Utilisation des ressources (CPU, RAM, Disk)

Alerting best practices:
- Alerts actionnables uniquement (pas de bruit)
- Contexte suffisant pour diagnostiquer
- Severities claires (P0=critical, P1=high, P2=medium, P3=low)
- Escalation policies définies
- On-call rotations équitables

Format de sortie:
- Configuration complète et commentée
- Dashboards exportables (JSON)
- Runbooks pour les alertes
- Documentation SLO/SLA
- Code d'instrumentation"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche de monitoring engineering.

        Args:
            task (Dict[str, Any]): Tâche à exécuter avec les clés:
                - task_type: "sentry" | "dashboards" | "slo_sla" | "health_checks" | "logging" | "alerts"
                - stack: Stack technologique (optionnel)
                - service_name: Nom du service à monitorer (optionnel)
                - requirements: Requirements spécifiques (optionnel)

        Returns:
            Dict[str, Any]: Résultat avec les clés:
                - status: "success" | "error"
                - output: Configuration ou dashboard
                - config_files: Liste des fichiers de configuration
                - metadata: Informations complémentaires
        """
        task_type = task.get("task_type", "sentry")
        stack = task.get("stack", "nodejs")
        service_name = task.get("service_name", "app")
        requirements = task.get("requirements", "")

        # Construire le prompt selon le type de tâche
        if task_type == "sentry":
            user_prompt = self._build_sentry_prompt(stack, service_name, requirements)
        elif task_type == "dashboards":
            user_prompt = self._build_dashboards_prompt(service_name, requirements)
        elif task_type == "slo_sla":
            user_prompt = self._build_slo_sla_prompt(service_name, requirements)
        elif task_type == "health_checks":
            user_prompt = self._build_health_checks_prompt(stack, service_name)
        elif task_type == "logging":
            user_prompt = self._build_logging_prompt(stack, requirements)
        elif task_type == "alerts":
            user_prompt = self._build_alerts_prompt(service_name, requirements)
        else:
            return {
                "status": "error",
                "output": f"Type de tâche inconnu: {task_type}",
                "config_files": [],
                "metadata": {}
            }

        # Appeler le LLM
        response = await self.call_llm(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=self.system_prompt
        )

        # Ajouter à la mémoire
        self.add_to_memory("user", user_prompt)
        self.add_to_memory("assistant", response)

        # Extraire les fichiers de configuration
        config_files = self._extract_config_files(response, task_type)

        return {
            "status": "success",
            "output": response,
            "config_files": config_files,
            "metadata": {
                "task_type": task_type,
                "stack": stack,
                "service_name": service_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def _build_sentry_prompt(self, stack: str, service_name: str, requirements: str) -> str:
        """Construit le prompt pour configuration Sentry."""
        return f"""Configure Sentry pour:

STACK: {stack}
SERVICE: {service_name}
REQUIREMENTS: {requirements if requirements else "Error tracking + performance monitoring"}

Fournis la configuration complète incluant:
- Initialization code
- Error boundaries (si React/Next.js)
- Performance monitoring
- Release tracking
- Source maps configuration"""

    def _build_dashboards_prompt(self, service_name: str, requirements: str) -> str:
        """Construit le prompt pour création de dashboards."""
        return f"""Crée des dashboards de monitoring pour:

SERVICE: {service_name}
REQUIREMENTS: {requirements if requirements else "Golden Signals"}

Fournis:
- Configuration Grafana (JSON)
- Queries Prometheus
- Panels pour chaque métrique
- Alerting rules"""

    def _build_slo_sla_prompt(self, service_name: str, requirements: str) -> str:
        """Construit le prompt pour définition SLO/SLA."""
        return f"""Définis les SLO/SLA pour:

SERVICE: {service_name}
REQUIREMENTS: {requirements if requirements else "99.9% uptime"}

Inclus:
- SLI definitions
- SLO targets
- Error budgets
- Burn rate alerts"""

    def _build_health_checks_prompt(self, stack: str, service_name: str) -> str:
        """Construit le prompt pour health checks."""
        return f"""Implémente health checks pour:

STACK: {stack}
SERVICE: {service_name}

Types requis:
- /health/liveness (simple ping)
- /health/readiness (dependencies check)
- /health/startup (initialization check)"""

    def _build_logging_prompt(self, stack: str, requirements: str) -> str:
        """Construit le prompt pour logging structuré."""
        return f"""Setup logging structuré pour:

STACK: {stack}
REQUIREMENTS: {requirements if requirements else "JSON logging"}

Inclus:
- Logger configuration
- Log levels
- Structured fields
- Correlation IDs
- Sensitive data masking"""

    def _build_alerts_prompt(self, service_name: str, requirements: str) -> str:
        """Construit le prompt pour alertes."""
        return f"""Configure des alertes pour:

SERVICE: {service_name}
REQUIREMENTS: {requirements if requirements else "Basic alerts"}

Inclus:
- Alert rules
- Severities (P0-P3)
- Notification channels
- Escalation policies
- Runbooks"""

    def _extract_config_files(self, response: str, task_type: str) -> List[Dict[str, str]]:
        """Extrait les fichiers de configuration de la réponse."""
        # Parsing basique
        return [{"path": f"{task_type}_config.yml", "content": response[:1000]}]

    # Helper methods
    async def setup_sentry(self, stack: str, service_name: str, requirements: str = "") -> Dict[str, Any]:
        """Helper pour setup Sentry."""
        return await self.execute({
            "task_type": "sentry",
            "stack": stack,
            "service_name": service_name,
            "requirements": requirements
        })

    async def create_dashboards(self, service_name: str, requirements: str = "") -> Dict[str, Any]:
        """Helper pour créer dashboards."""
        return await self.execute({
            "task_type": "dashboards",
            "service_name": service_name,
            "requirements": requirements
        })

    async def define_slo_sla(self, service_name: str, requirements: str = "") -> Dict[str, Any]:
        """Helper pour définir SLO/SLA."""
        return await self.execute({
            "task_type": "slo_sla",
            "service_name": service_name,
            "requirements": requirements
        })

    async def implement_health_checks(self, stack: str, service_name: str) -> Dict[str, Any]:
        """Helper pour implémenter health checks."""
        return await self.execute({
            "task_type": "health_checks",
            "stack": stack,
            "service_name": service_name
        })

    async def setup_logging(self, stack: str, requirements: str = "") -> Dict[str, Any]:
        """Helper pour setup logging."""
        return await self.execute({
            "task_type": "logging",
            "stack": stack,
            "requirements": requirements
        })

    async def configure_alerts(self, service_name: str, requirements: str = "") -> Dict[str, Any]:
        """Helper pour configurer alertes."""
        return await self.execute({
            "task_type": "alerts",
            "service_name": service_name,
            "requirements": requirements
        })
