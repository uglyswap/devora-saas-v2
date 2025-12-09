"""
Performance Audit Workflow

Workflow complet d'audit de performance:
Profile → Analyze → Optimize → Verify

Squads impliqués: Performance Squad
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class PerformanceAuditWorkflow:
    """
    Workflow pour auditer et optimiser les performances.

    Étapes:
    1. Profile - Profiling de l'application (CPU, mémoire, réseau)
    2. Analyze - Analyse des résultats de profiling
    3. Optimize - Optimisation des bottlenecks identifiés
    4. Verify - Vérification des améliorations

    Métriques analysées:
    - Core Web Vitals (LCP, FID, CLS)
    - Bundle size
    - Time to Interactive (TTI)
    - Memory usage
    - API response times
    """

    def __init__(self):
        self.name = "performance_audit"
        self.description = "Workflow d'audit de performance complet"
        self.steps = [
            "profile",
            "analyze",
            "optimize",
            "verify"
        ]
        self.required_squads = [
            "performance_squad"  # Performance Engineer
        ]
        self.logger = logging.getLogger(f"devora.workflow.{self.name}")

    async def execute(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """
        Exécute le workflow d'audit de performance.

        Args:
            context: Contexte du workflow avec:
                - target_url: URL de l'application à auditer
                - audit_type: "frontend" | "backend" | "full"
                - baseline_metrics: Métriques de référence (optionnel)
                - target_metrics: Objectifs de performance
                - environment: Environnement (staging/production)
            orchestrator: Instance de l'orchestrateur

        Returns:
            Résultat du workflow avec outputs de chaque étape
        """
        self.logger.info(f"Starting performance audit workflow: {context.get('target_url', 'N/A')}")

        results = {
            "workflow": self.name,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "steps": {},
            "context": context
        }

        try:
            # Step 1: Profile
            profile_result = await self._run_step(
                "profile",
                context,
                orchestrator
            )
            results["steps"]["profile"] = profile_result

            # Step 2: Analyze
            analyze_result = await self._run_step(
                "analyze",
                {**context, "profile": profile_result},
                orchestrator
            )
            results["steps"]["analyze"] = analyze_result

            # Step 3: Optimize
            optimize_result = await self._run_step(
                "optimize",
                {
                    **context,
                    "profile": profile_result,
                    "analysis": analyze_result
                },
                orchestrator
            )
            results["steps"]["optimize"] = optimize_result

            # Step 4: Verify
            verify_result = await self._run_step(
                "verify",
                {
                    **context,
                    "baseline": profile_result,
                    "optimizations": optimize_result
                },
                orchestrator
            )
            results["steps"]["verify"] = verify_result

            # Calculate improvement percentage
            improvement = self._calculate_improvement(
                profile_result,
                verify_result
            )
            results["improvement"] = improvement

            results["status"] = "completed"
            results["completed_at"] = datetime.utcnow().isoformat()

            self.logger.info(f"Performance audit workflow completed successfully")

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = datetime.utcnow().isoformat()
            self.logger.error(f"Performance audit workflow failed: {str(e)}")

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
            "profile": self._profile_step,
            "analyze": self._analyze_step,
            "optimize": self._optimize_step,
            "verify": self._verify_step
        }

        handler = step_handlers.get(step_name)
        if not handler:
            raise ValueError(f"Unknown step: {step_name}")

        return await handler(context, orchestrator)

    async def _profile_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape profile: Profiling de l'application."""
        task = {
            "type": "profile_application",
            "squad": "performance_squad",
            "agent": "performance_engineer",
            "data": {
                "target_url": context.get("target_url"),
                "audit_type": context.get("audit_type", "full"),
                "environment": context.get("environment"),
                "metrics": [
                    "lighthouse",
                    "web_vitals",
                    "bundle_size",
                    "memory",
                    "network",
                    "cpu"
                ]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "lighthouse_scores": result.get("lighthouse_scores"),
            "web_vitals": {
                "lcp": result.get("lcp"),  # Largest Contentful Paint
                "fid": result.get("fid"),  # First Input Delay
                "cls": result.get("cls")   # Cumulative Layout Shift
            },
            "bundle_size": result.get("bundle_size"),
            "memory_usage": result.get("memory_usage"),
            "network_requests": result.get("network_requests"),
            "cpu_time": result.get("cpu_time")
        }

    async def _analyze_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape analyze: Analyse des résultats de profiling."""
        task = {
            "type": "analyze_performance",
            "squad": "performance_squad",
            "agent": "performance_engineer",
            "data": {
                "profile": context["profile"],
                "baseline_metrics": context.get("baseline_metrics"),
                "target_metrics": context.get("target_metrics")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "bottlenecks": result.get("bottlenecks"),
            "recommendations": result.get("recommendations"),
            "priority_issues": result.get("priority_issues"),
            "quick_wins": result.get("quick_wins"),
            "estimated_impact": result.get("estimated_impact")
        }

    async def _optimize_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape optimize: Optimisation des bottlenecks."""
        task = {
            "type": "optimize_performance",
            "squad": "performance_squad",
            "agent": "performance_engineer",
            "data": {
                "bottlenecks": context["analysis"]["bottlenecks"],
                "recommendations": context["analysis"]["recommendations"],
                "priority_issues": context["analysis"]["priority_issues"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "optimizations_applied": result.get("optimizations_applied"),
            "files_changed": result.get("files_changed"),
            "code_changes": result.get("code_changes"),
            "configuration_changes": result.get("configuration_changes"),
            "infrastructure_changes": result.get("infrastructure_changes")
        }

    async def _verify_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape verify: Vérification des améliorations."""
        task = {
            "type": "verify_optimizations",
            "squad": "performance_squad",
            "agent": "performance_engineer",
            "data": {
                "target_url": context.get("target_url"),
                "baseline": context["baseline"],
                "optimizations": context["optimizations"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "new_metrics": result.get("new_metrics"),
            "improvements": result.get("improvements"),
            "regressions": result.get("regressions", []),
            "target_achieved": result.get("target_achieved", False)
        }

    def _calculate_improvement(
        self,
        baseline: Dict[str, Any],
        optimized: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calcule le pourcentage d'amélioration pour chaque métrique.

        Args:
            baseline: Métriques de base
            optimized: Métriques après optimisation

        Returns:
            Dictionnaire des améliorations en pourcentage
        """
        improvements = {}

        # Lighthouse scores
        baseline_lighthouse = baseline.get("lighthouse_scores", {})
        optimized_lighthouse = optimized.get("new_metrics", {}).get("lighthouse_scores", {})

        for key in baseline_lighthouse:
            if key in optimized_lighthouse:
                baseline_val = baseline_lighthouse[key]
                optimized_val = optimized_lighthouse[key]
                if baseline_val > 0:
                    improvement = ((optimized_val - baseline_val) / baseline_val) * 100
                    improvements[f"lighthouse_{key}"] = round(improvement, 2)

        # Web Vitals
        baseline_vitals = baseline.get("web_vitals", {})
        optimized_vitals = optimized.get("new_metrics", {}).get("web_vitals", {})

        for key in ["lcp", "fid", "cls"]:
            if key in baseline_vitals and key in optimized_vitals:
                baseline_val = baseline_vitals[key]
                optimized_val = optimized_vitals[key]
                if baseline_val > 0:
                    # Pour web vitals, une diminution est une amélioration
                    improvement = ((baseline_val - optimized_val) / baseline_val) * 100
                    improvements[f"web_vital_{key}"] = round(improvement, 2)

        # Bundle size
        baseline_bundle = baseline.get("bundle_size", {}).get("total", 0)
        optimized_bundle = optimized.get("new_metrics", {}).get("bundle_size", {}).get("total", 0)

        if baseline_bundle > 0:
            improvement = ((baseline_bundle - optimized_bundle) / baseline_bundle) * 100
            improvements["bundle_size"] = round(improvement, 2)

        return improvements
