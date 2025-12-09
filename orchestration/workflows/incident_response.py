"""
Incident Response Workflow

Workflow de réponse aux incidents critiques:
Detect → Assess → Mitigate → Resolve → Postmortem

Squads impliqués: DevOps, QA
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class IncidentResponseWorkflow:
    """
    Workflow pour gérer les incidents de production.

    Étapes:
    1. Detect - Détection et alerte de l'incident
    2. Assess - Évaluation de la sévérité et de l'impact
    3. Mitigate - Mitigation immédiate (workaround)
    4. Resolve - Résolution définitive du problème
    5. Postmortem - Analyse post-mortem et prévention

    Sévérités:
    - SEV1: Critique - Service down, impact massif
    - SEV2: Élevée - Fonctionnalité majeure impactée
    - SEV3: Moyenne - Fonctionnalité mineure impactée
    - SEV4: Faible - Impact mineur
    """

    def __init__(self):
        self.name = "incident_response"
        self.description = "Workflow de réponse aux incidents"
        self.steps = [
            "detect",
            "assess",
            "mitigate",
            "resolve",
            "postmortem"
        ]
        self.required_squads = [
            "devops_squad",  # DevOps Engineer
            "qa_squad"       # QA Engineer
        ]
        self.logger = logging.getLogger(f"devora.workflow.{self.name}")

    async def execute(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """
        Exécute le workflow de réponse à incident.

        Args:
            context: Contexte du workflow avec:
                - incident_description: Description de l'incident
                - alert_source: Source de l'alerte (monitoring/user/internal)
                - affected_service: Service affecté
                - environment: Environnement (production/staging)
                - initial_severity: Sévérité initiale (SEV1/SEV2/SEV3/SEV4)
            orchestrator: Instance de l'orchestrateur

        Returns:
            Résultat du workflow avec outputs de chaque étape
        """
        self.logger.critical(f"Starting incident response workflow: {context.get('incident_description', 'N/A')}")

        results = {
            "workflow": self.name,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "steps": {},
            "context": context,
            "incident_id": self._generate_incident_id()
        }

        try:
            # Step 1: Detect
            detect_result = await self._run_step(
                "detect",
                {**context, "incident_id": results["incident_id"]},
                orchestrator
            )
            results["steps"]["detect"] = detect_result

            # Step 2: Assess
            assess_result = await self._run_step(
                "assess",
                {**context, "detection": detect_result},
                orchestrator
            )
            results["steps"]["assess"] = assess_result

            # Update severity if changed
            results["severity"] = assess_result.get("severity", context.get("initial_severity"))

            # Step 3: Mitigate (immediate action)
            mitigate_result = await self._run_step(
                "mitigate",
                {
                    **context,
                    "detection": detect_result,
                    "assessment": assess_result
                },
                orchestrator
            )
            results["steps"]["mitigate"] = mitigate_result

            # Step 4: Resolve (permanent fix)
            resolve_result = await self._run_step(
                "resolve",
                {
                    **context,
                    "detection": detect_result,
                    "assessment": assess_result,
                    "mitigation": mitigate_result
                },
                orchestrator
            )
            results["steps"]["resolve"] = resolve_result

            # Step 5: Postmortem
            postmortem_result = await self._run_step(
                "postmortem",
                {
                    **context,
                    "detection": detect_result,
                    "assessment": assess_result,
                    "mitigation": mitigate_result,
                    "resolution": resolve_result
                },
                orchestrator
            )
            results["steps"]["postmortem"] = postmortem_result

            results["status"] = "completed"
            results["completed_at"] = datetime.utcnow().isoformat()
            results["total_downtime"] = self._calculate_downtime(
                results["started_at"],
                mitigate_result.get("mitigated_at")
            )

            self.logger.info(f"Incident response workflow completed. Incident ID: {results['incident_id']}")

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = datetime.utcnow().isoformat()
            self.logger.error(f"Incident response workflow failed: {str(e)}")

        return results

    async def _run_step(
        self,
        step_name: str,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """
        Exécute une étape spécifique du workflow.

        Args:
            step_name: Nom de l'étape
            context: Contexte de l'étape
            orchestrator: Instance de l'orchestrateur

        Returns:
            Résultat de l'étape
        """
        self.logger.info(f"Executing step: {step_name}")

        step_handlers = {
            "detect": self._detect_step,
            "assess": self._assess_step,
            "mitigate": self._mitigate_step,
            "resolve": self._resolve_step,
            "postmortem": self._postmortem_step
        }

        handler = step_handlers.get(step_name)
        if not handler:
            raise ValueError(f"Unknown step: {step_name}")

        return await handler(context, orchestrator)

    async def _detect_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape detect: Détection et documentation de l'incident."""
        task = {
            "type": "detect_incident",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "incident_id": context.get("incident_id"),
                "incident_description": context.get("incident_description"),
                "alert_source": context.get("alert_source"),
                "affected_service": context.get("affected_service"),
                "environment": context.get("environment")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "detected_at": result.get("detected_at", datetime.utcnow().isoformat()),
            "symptoms": result.get("symptoms"),
            "affected_users": result.get("affected_users"),
            "error_rate": result.get("error_rate"),
            "metrics": result.get("metrics"),
            "logs": result.get("logs")
        }

    async def _assess_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape assess: Évaluation de la sévérité et de l'impact."""
        task = {
            "type": "assess_incident",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "detection": context["detection"],
                "initial_severity": context.get("initial_severity"),
                "affected_service": context.get("affected_service")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "severity": result.get("severity"),
            "impact_assessment": result.get("impact_assessment"),
            "affected_components": result.get("affected_components"),
            "root_cause_hypothesis": result.get("root_cause_hypothesis"),
            "estimated_recovery_time": result.get("estimated_recovery_time")
        }

    async def _mitigate_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape mitigate: Mitigation immédiate de l'incident."""
        task = {
            "type": "mitigate_incident",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "assessment": context["assessment"],
                "affected_service": context.get("affected_service"),
                "environment": context.get("environment")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "mitigation_action": result.get("mitigation_action"),
            "mitigated_at": result.get("mitigated_at", datetime.utcnow().isoformat()),
            "service_restored": result.get("service_restored", False),
            "workaround_applied": result.get("workaround_applied"),
            "rollback_performed": result.get("rollback_performed", False)
        }

    async def _resolve_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape resolve: Résolution définitive de l'incident."""
        task = {
            "type": "resolve_incident",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "assessment": context["assessment"],
                "mitigation": context["mitigation"],
                "affected_service": context.get("affected_service")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "root_cause": result.get("root_cause"),
            "permanent_fix": result.get("permanent_fix"),
            "resolved_at": result.get("resolved_at", datetime.utcnow().isoformat()),
            "fix_verified": result.get("fix_verified", False),
            "monitoring_updated": result.get("monitoring_updated", False)
        }

    async def _postmortem_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape postmortem: Analyse post-mortem et actions préventives."""
        task = {
            "type": "create_postmortem",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "incident_id": context.get("incident_id"),
                "detection": context["detection"],
                "assessment": context["assessment"],
                "mitigation": context["mitigation"],
                "resolution": context["resolution"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "postmortem_document": result.get("postmortem_document"),
            "timeline": result.get("timeline"),
            "lessons_learned": result.get("lessons_learned"),
            "action_items": result.get("action_items"),
            "prevention_measures": result.get("prevention_measures"),
            "monitoring_improvements": result.get("monitoring_improvements")
        }

    def _generate_incident_id(self) -> str:
        """Génère un ID unique pour l'incident."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"INC-{timestamp}"

    def _calculate_downtime(self, started_at: str, mitigated_at: Optional[str]) -> Optional[float]:
        """
        Calcule le temps d'arrêt en minutes.

        Args:
            started_at: Timestamp de début
            mitigated_at: Timestamp de mitigation

        Returns:
            Durée en minutes ou None
        """
        if not mitigated_at:
            return None

        try:
            start = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(mitigated_at.replace('Z', '+00:00'))
            downtime = (end - start).total_seconds() / 60
            return round(downtime, 2)
        except Exception:
            return None
