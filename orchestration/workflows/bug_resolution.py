"""
Bug Resolution Workflow

Workflow systématique pour la résolution de bugs:
Reproduce → Diagnose → Fix → Test → Review

Squads impliqués: QA, relevant dev squad (Frontend/Backend)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class BugResolutionWorkflow:
    """
    Workflow pour la résolution systématique de bugs.

    Étapes:
    1. Reproduce - Reproduction fiable du bug
    2. Diagnose - Diagnostic de la cause racine
    3. Fix - Correction du bug
    4. Test - Tests de non-régression
    5. Review - Code review et validation
    """

    def __init__(self):
        self.name = "bug_resolution"
        self.description = "Workflow systématique de résolution de bugs"
        self.steps = [
            "reproduce",
            "diagnose",
            "fix",
            "test",
            "review"
        ]
        self.required_squads = [
            "qa_squad",        # QA Engineer
            "backend_squad",   # Backend Developer (si backend bug)
            "frontend_squad"   # Frontend Developer (si frontend bug)
        ]
        self.logger = logging.getLogger(f"devora.workflow.{self.name}")

    async def execute(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """
        Exécute le workflow de résolution de bug.

        Args:
            context: Contexte du workflow avec:
                - bug_description: Description du bug
                - severity: Critique/Élevée/Moyenne/Faible
                - steps_to_reproduce: Étapes de reproduction
                - expected_behavior: Comportement attendu
                - actual_behavior: Comportement observé
                - environment: Environnement (prod/staging/dev)
                - affected_component: Composant affecté (frontend/backend/database)
            orchestrator: Instance de l'orchestrateur

        Returns:
            Résultat du workflow avec outputs de chaque étape
        """
        self.logger.info(f"Starting bug resolution workflow: {context.get('bug_description', 'N/A')}")

        results = {
            "workflow": self.name,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "steps": {},
            "context": context
        }

        try:
            # Step 1: Reproduce
            reproduce_result = await self._run_step(
                "reproduce",
                context,
                orchestrator
            )
            results["steps"]["reproduce"] = reproduce_result

            if not reproduce_result.get("reproducible"):
                results["status"] = "cannot_reproduce"
                results["completed_at"] = datetime.utcnow().isoformat()
                self.logger.warning("Bug could not be reproduced")
                return results

            # Step 2: Diagnose
            diagnose_result = await self._run_step(
                "diagnose",
                {**context, "reproduction": reproduce_result},
                orchestrator
            )
            results["steps"]["diagnose"] = diagnose_result

            # Step 3: Fix
            fix_result = await self._run_step(
                "fix",
                {
                    **context,
                    "reproduction": reproduce_result,
                    "diagnosis": diagnose_result
                },
                orchestrator
            )
            results["steps"]["fix"] = fix_result

            # Step 4: Test
            test_result = await self._run_step(
                "test",
                {
                    **context,
                    "reproduction": reproduce_result,
                    "fix": fix_result
                },
                orchestrator
            )
            results["steps"]["test"] = test_result

            # Step 5: Review
            review_result = await self._run_step(
                "review",
                {
                    **context,
                    "fix": fix_result,
                    "test_results": test_result
                },
                orchestrator
            )
            results["steps"]["review"] = review_result

            results["status"] = "completed"
            results["completed_at"] = datetime.utcnow().isoformat()

            self.logger.info(f"Bug resolution workflow completed successfully")

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = datetime.utcnow().isoformat()
            self.logger.error(f"Bug resolution workflow failed: {str(e)}")

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
            "reproduce": self._reproduce_step,
            "diagnose": self._diagnose_step,
            "fix": self._fix_step,
            "test": self._test_step,
            "review": self._review_step
        }

        handler = step_handlers.get(step_name)
        if not handler:
            raise ValueError(f"Unknown step: {step_name}")

        return await handler(context, orchestrator)

    async def _reproduce_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape de reproduction: QA reproduit le bug de manière fiable."""
        task = {
            "type": "reproduce_bug",
            "squad": "qa_squad",
            "agent": "qa_engineer",
            "data": {
                "bug_description": context.get("bug_description"),
                "steps_to_reproduce": context.get("steps_to_reproduce"),
                "environment": context.get("environment"),
                "expected_behavior": context.get("expected_behavior"),
                "actual_behavior": context.get("actual_behavior")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "reproducible": result.get("reproducible", False),
            "reproduction_steps": result.get("reproduction_steps"),
            "screenshots": result.get("screenshots"),
            "logs": result.get("logs"),
            "frequency": result.get("frequency")  # always/sometimes/rare
        }

    async def _diagnose_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape de diagnostic: Identifie la cause racine du bug."""
        affected_component = context.get("affected_component", "backend")

        # Déterminer la squad appropriée
        squad = "backend_squad" if affected_component == "backend" else "frontend_squad"
        agent = "backend_developer" if affected_component == "backend" else "frontend_developer"

        task = {
            "type": "diagnose_bug",
            "squad": squad,
            "agent": agent,
            "data": {
                "bug_description": context.get("bug_description"),
                "reproduction_steps": context["reproduction"]["reproduction_steps"],
                "logs": context["reproduction"]["logs"],
                "affected_component": affected_component
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "root_cause": result.get("root_cause"),
            "affected_files": result.get("affected_files"),
            "complexity": result.get("complexity"),  # simple/medium/complex
            "estimated_fix_time": result.get("estimated_fix_time")
        }

    async def _fix_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape de correction: Implémente le fix."""
        affected_component = context.get("affected_component", "backend")

        # Déterminer la squad appropriée
        squad = "backend_squad" if affected_component == "backend" else "frontend_squad"
        agent = "backend_developer" if affected_component == "backend" else "frontend_developer"

        task = {
            "type": "implement_fix",
            "squad": squad,
            "agent": agent,
            "data": {
                "root_cause": context["diagnosis"]["root_cause"],
                "affected_files": context["diagnosis"]["affected_files"],
                "bug_description": context.get("bug_description")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "fix_description": result.get("fix_description"),
            "files_changed": result.get("files_changed"),
            "code_diff": result.get("code_diff"),
            "breaking_changes": result.get("breaking_changes", False)
        }

    async def _test_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape de test: Vérifie que le bug est corrigé et teste la non-régression."""
        task = {
            "type": "test_bug_fix",
            "squad": "qa_squad",
            "agent": "qa_engineer",
            "data": {
                "bug_description": context.get("bug_description"),
                "fix": context["fix"],
                "reproduction_steps": context["reproduction"]["reproduction_steps"],
                "test_types": ["regression", "unit", "integration"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "bug_fixed": result.get("bug_fixed", False),
            "test_results": result.get("test_results"),
            "regression_tests_passed": result.get("regression_tests_passed", False),
            "coverage": result.get("coverage")
        }

    async def _review_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape de review: Code review du fix."""
        task = {
            "type": "review_bug_fix",
            "squad": "qa_squad",
            "agent": "code_reviewer",
            "data": {
                "files_changed": context["fix"]["files_changed"],
                "code_diff": context["fix"]["code_diff"],
                "test_results": context["test_results"],
                "root_cause": context["diagnosis"]["root_cause"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "approved": result.get("approved", False),
            "review_comments": result.get("comments"),
            "quality_score": result.get("quality_score"),
            "ready_for_deploy": result.get("ready_for_deploy", False)
        }
