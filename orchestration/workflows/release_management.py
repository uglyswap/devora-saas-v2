"""
Release Management Workflow

Workflow complet de gestion des releases:
Changelog → Version → QA → Stage → Prod → Monitor

Squads impliqués: DevOps, Documentation, QA
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class ReleaseManagementWorkflow:
    """
    Workflow pour gérer les releases de bout en bout.

    Étapes:
    1. Changelog - Génération du changelog
    2. Version - Bump de version et tagging
    3. QA - Tests de validation de la release
    4. Stage - Déploiement en staging
    5. Prod - Déploiement en production
    6. Monitor - Monitoring post-deployment

    Types de releases:
    - major: Breaking changes (1.0.0 → 2.0.0)
    - minor: Nouvelles features (1.0.0 → 1.1.0)
    - patch: Bug fixes (1.0.0 → 1.0.1)
    - hotfix: Fix urgent en production
    """

    def __init__(self):
        self.name = "release_management"
        self.description = "Workflow de gestion des releases"
        self.steps = [
            "changelog",
            "version",
            "qa",
            "stage",
            "prod",
            "monitor"
        ]
        self.required_squads = [
            "devops_squad",          # DevOps Engineer
            "documentation_squad",   # Technical Writer
            "qa_squad"               # QA Engineer
        ]
        self.logger = logging.getLogger(f"devora.workflow.{self.name}")

    async def execute(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """
        Exécute le workflow de release management.

        Args:
            context: Contexte du workflow avec:
                - release_type: "major" | "minor" | "patch" | "hotfix"
                - current_version: Version actuelle (ex: "1.2.3")
                - release_branch: Branche de release
                - features: Liste des features incluses
                - fixes: Liste des fixes inclus
                - breaking_changes: Breaking changes (pour major)
                - release_notes: Notes de release supplémentaires
            orchestrator: Instance de l'orchestrateur

        Returns:
            Résultat du workflow avec outputs de chaque étape
        """
        self.logger.info(f"Starting release management workflow: {context.get('release_type', 'N/A')}")

        results = {
            "workflow": self.name,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "steps": {},
            "context": context
        }

        try:
            # Step 1: Changelog
            changelog_result = await self._run_step(
                "changelog",
                context,
                orchestrator
            )
            results["steps"]["changelog"] = changelog_result

            # Step 2: Version
            version_result = await self._run_step(
                "version",
                {**context, "changelog": changelog_result},
                orchestrator
            )
            results["steps"]["version"] = version_result
            results["new_version"] = version_result.get("new_version")

            # Step 3: QA
            qa_result = await self._run_step(
                "qa",
                {
                    **context,
                    "version": version_result
                },
                orchestrator
            )
            results["steps"]["qa"] = qa_result

            if not qa_result.get("qa_passed"):
                results["status"] = "qa_failed"
                results["completed_at"] = datetime.utcnow().isoformat()
                self.logger.warning("Release failed QA validation")
                return results

            # Step 4: Stage
            stage_result = await self._run_step(
                "stage",
                {
                    **context,
                    "version": version_result,
                    "qa": qa_result
                },
                orchestrator
            )
            results["steps"]["stage"] = stage_result

            # Step 5: Prod (skip if context says dry_run or manual approval needed)
            if context.get("auto_deploy", False):
                prod_result = await self._run_step(
                    "prod",
                    {
                        **context,
                        "version": version_result,
                        "stage": stage_result
                    },
                    orchestrator
                )
                results["steps"]["prod"] = prod_result

                # Step 6: Monitor
                monitor_result = await self._run_step(
                    "monitor",
                    {
                        **context,
                        "version": version_result,
                        "prod": prod_result
                    },
                    orchestrator
                )
                results["steps"]["monitor"] = monitor_result
            else:
                results["steps"]["prod"] = {
                    "status": "pending_approval",
                    "message": "Waiting for manual approval to deploy to production"
                }
                results["steps"]["monitor"] = {"status": "skipped"}

            results["status"] = "completed"
            results["completed_at"] = datetime.utcnow().isoformat()

            self.logger.info(f"Release management workflow completed. Version: {results['new_version']}")

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = datetime.utcnow().isoformat()
            self.logger.error(f"Release management workflow failed: {str(e)}")

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
            "changelog": self._changelog_step,
            "version": self._version_step,
            "qa": self._qa_step,
            "stage": self._stage_step,
            "prod": self._prod_step,
            "monitor": self._monitor_step
        }

        handler = step_handlers.get(step_name)
        if not handler:
            raise ValueError(f"Unknown step: {step_name}")

        return await handler(context, orchestrator)

    async def _changelog_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape changelog: Génération du changelog."""
        task = {
            "type": "generate_changelog",
            "squad": "documentation_squad",
            "agent": "technical_writer",
            "data": {
                "release_type": context.get("release_type"),
                "current_version": context.get("current_version"),
                "features": context.get("features", []),
                "fixes": context.get("fixes", []),
                "breaking_changes": context.get("breaking_changes", []),
                "release_notes": context.get("release_notes", "")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "changelog": result.get("changelog"),
            "formatted_changelog": result.get("formatted_changelog"),
            "release_highlights": result.get("release_highlights")
        }

    async def _version_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape version: Bump de version et tagging."""
        task = {
            "type": "bump_version",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "release_type": context.get("release_type"),
                "current_version": context.get("current_version"),
                "release_branch": context.get("release_branch"),
                "changelog": context["changelog"]["changelog"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "new_version": result.get("new_version"),
            "git_tag": result.get("git_tag"),
            "commit_sha": result.get("commit_sha"),
            "release_branch": result.get("release_branch")
        }

    async def _qa_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape QA: Tests de validation de la release."""
        task = {
            "type": "validate_release",
            "squad": "qa_squad",
            "agent": "qa_engineer",
            "data": {
                "version": context["version"]["new_version"],
                "release_branch": context["version"]["release_branch"],
                "test_suites": [
                    "smoke_tests",
                    "regression_tests",
                    "integration_tests",
                    "e2e_tests"
                ]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "qa_passed": result.get("qa_passed", False),
            "test_results": result.get("test_results"),
            "smoke_tests": result.get("smoke_tests"),
            "regression_tests": result.get("regression_tests"),
            "integration_tests": result.get("integration_tests"),
            "e2e_tests": result.get("e2e_tests"),
            "blockers": result.get("blockers", [])
        }

    async def _stage_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape stage: Déploiement en staging."""
        task = {
            "type": "deploy_to_staging",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "version": context["version"]["new_version"],
                "git_tag": context["version"]["git_tag"],
                "environment": "staging"
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "staging_url": result.get("staging_url"),
            "deployment_time": result.get("deployment_time"),
            "deployment_successful": result.get("deployment_successful", False),
            "smoke_test_passed": result.get("smoke_test_passed", False)
        }

    async def _prod_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape prod: Déploiement en production."""
        task = {
            "type": "deploy_to_production",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "version": context["version"]["new_version"],
                "git_tag": context["version"]["git_tag"],
                "staging_url": context["stage"]["staging_url"],
                "environment": "production",
                "deployment_strategy": context.get("deployment_strategy", "rolling")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "production_url": result.get("production_url"),
            "deployment_time": result.get("deployment_time"),
            "deployment_successful": result.get("deployment_successful", False),
            "rollback_plan": result.get("rollback_plan"),
            "canary_percentage": result.get("canary_percentage", 100)
        }

    async def _monitor_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape monitor: Monitoring post-deployment."""
        task = {
            "type": "monitor_release",
            "squad": "devops_squad",
            "agent": "devops_engineer",
            "data": {
                "version": context["version"]["new_version"],
                "production_url": context["prod"]["production_url"],
                "monitoring_duration": context.get("monitoring_duration", 60),  # minutes
                "metrics_to_monitor": [
                    "error_rate",
                    "response_time",
                    "cpu_usage",
                    "memory_usage",
                    "user_activity"
                ]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "monitoring_healthy": result.get("monitoring_healthy", False),
            "error_rate": result.get("error_rate"),
            "response_time": result.get("response_time"),
            "alerts_triggered": result.get("alerts_triggered", []),
            "rollback_needed": result.get("rollback_needed", False),
            "release_stable": result.get("release_stable", False)
        }
