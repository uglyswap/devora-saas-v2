"""
Refactoring Workflow

Workflow systématique pour le refactoring de code:
Analyze → Plan → Refactor → Test → Review

Squads impliqués: QA, relevant dev squad (Frontend/Backend)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class RefactoringWorkflow:
    """
    Workflow pour le refactoring systématique de code.

    Étapes:
    1. Analyze - Analyse du code à refactorer
    2. Plan - Planification du refactoring
    3. Refactor - Exécution du refactoring
    4. Test - Tests de non-régression
    5. Review - Code review du refactoring

    Types de refactoring:
    - Code cleanup (dead code, duplication)
    - Performance optimization
    - Architecture improvement
    - Modernization (new patterns, libraries)
    """

    def __init__(self):
        self.name = "refactoring"
        self.description = "Workflow systématique de refactoring"
        self.steps = [
            "analyze",
            "plan",
            "refactor",
            "test",
            "review"
        ]
        self.required_squads = [
            "qa_squad",        # QA Engineer
            "backend_squad",   # Backend Developer (si backend)
            "frontend_squad"   # Frontend Developer (si frontend)
        ]
        self.logger = logging.getLogger(f"devora.workflow.{self.name}")

    async def execute(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """
        Exécute le workflow de refactoring.

        Args:
            context: Contexte du workflow avec:
                - refactoring_type: "cleanup" | "performance" | "architecture" | "modernization"
                - target_path: Chemin du code à refactorer
                - scope: Scope du refactoring (file/module/codebase)
                - reason: Raison du refactoring
                - constraints: Contraintes (no breaking changes, etc.)
                - component_type: Type de composant (frontend/backend)
            orchestrator: Instance de l'orchestrateur

        Returns:
            Résultat du workflow avec outputs de chaque étape
        """
        self.logger.info(f"Starting refactoring workflow: {context.get('refactoring_type', 'N/A')}")

        results = {
            "workflow": self.name,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "steps": {},
            "context": context
        }

        try:
            # Step 1: Analyze
            analyze_result = await self._run_step(
                "analyze",
                context,
                orchestrator
            )
            results["steps"]["analyze"] = analyze_result

            # Step 2: Plan
            plan_result = await self._run_step(
                "plan",
                {**context, "analysis": analyze_result},
                orchestrator
            )
            results["steps"]["plan"] = plan_result

            # Step 3: Refactor
            refactor_result = await self._run_step(
                "refactor",
                {
                    **context,
                    "analysis": analyze_result,
                    "plan": plan_result
                },
                orchestrator
            )
            results["steps"]["refactor"] = refactor_result

            # Step 4: Test
            test_result = await self._run_step(
                "test",
                {
                    **context,
                    "refactoring": refactor_result
                },
                orchestrator
            )
            results["steps"]["test"] = test_result

            # Step 5: Review
            review_result = await self._run_step(
                "review",
                {
                    **context,
                    "refactoring": refactor_result,
                    "test_results": test_result
                },
                orchestrator
            )
            results["steps"]["review"] = review_result

            results["status"] = "completed"
            results["completed_at"] = datetime.utcnow().isoformat()

            self.logger.info(f"Refactoring workflow completed successfully")

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = datetime.utcnow().isoformat()
            self.logger.error(f"Refactoring workflow failed: {str(e)}")

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
            "analyze": self._analyze_step,
            "plan": self._plan_step,
            "refactor": self._refactor_step,
            "test": self._test_step,
            "review": self._review_step
        }

        handler = step_handlers.get(step_name)
        if not handler:
            raise ValueError(f"Unknown step: {step_name}")

        return await handler(context, orchestrator)

    async def _analyze_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape analyze: Analyse du code à refactorer."""
        component_type = context.get("component_type", "backend")

        # Déterminer la squad appropriée
        squad = "backend_squad" if component_type == "backend" else "frontend_squad"
        agent = "backend_developer" if component_type == "backend" else "frontend_developer"

        task = {
            "type": "analyze_code",
            "squad": squad,
            "agent": agent,
            "data": {
                "target_path": context.get("target_path"),
                "refactoring_type": context.get("refactoring_type"),
                "scope": context.get("scope"),
                "reason": context.get("reason")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "code_smells": result.get("code_smells"),
            "duplication": result.get("duplication"),
            "complexity": result.get("complexity"),
            "dependencies": result.get("dependencies"),
            "refactoring_opportunities": result.get("refactoring_opportunities"),
            "estimated_impact": result.get("estimated_impact")
        }

    async def _plan_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape plan: Planification du refactoring."""
        component_type = context.get("component_type", "backend")

        # Déterminer la squad appropriée
        squad = "backend_squad" if component_type == "backend" else "frontend_squad"
        agent = "backend_developer" if component_type == "backend" else "frontend_developer"

        task = {
            "type": "plan_refactoring",
            "squad": squad,
            "agent": agent,
            "data": {
                "analysis": context["analysis"],
                "refactoring_type": context.get("refactoring_type"),
                "constraints": context.get("constraints")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "refactoring_steps": result.get("refactoring_steps"),
            "affected_files": result.get("affected_files"),
            "breaking_changes": result.get("breaking_changes", False),
            "estimated_time": result.get("estimated_time"),
            "risk_level": result.get("risk_level")  # low/medium/high
        }

    async def _refactor_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape refactor: Exécution du refactoring."""
        component_type = context.get("component_type", "backend")

        # Déterminer la squad appropriée
        squad = "backend_squad" if component_type == "backend" else "frontend_squad"
        agent = "backend_developer" if component_type == "backend" else "frontend_developer"

        task = {
            "type": "execute_refactoring",
            "squad": squad,
            "agent": agent,
            "data": {
                "plan": context["plan"],
                "target_path": context.get("target_path"),
                "refactoring_type": context.get("refactoring_type")
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "files_changed": result.get("files_changed"),
            "lines_added": result.get("lines_added"),
            "lines_removed": result.get("lines_removed"),
            "code_diff": result.get("code_diff"),
            "improvements": result.get("improvements"),
            "breaking_changes": result.get("breaking_changes", [])
        }

    async def _test_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape test: Tests de non-régression."""
        task = {
            "type": "test_refactoring",
            "squad": "qa_squad",
            "agent": "qa_engineer",
            "data": {
                "files_changed": context["refactoring"]["files_changed"],
                "test_types": ["unit", "integration", "regression"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "all_tests_passed": result.get("all_tests_passed", False),
            "test_results": result.get("test_results"),
            "coverage_before": result.get("coverage_before"),
            "coverage_after": result.get("coverage_after"),
            "performance_before": result.get("performance_before"),
            "performance_after": result.get("performance_after")
        }

    async def _review_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape review: Code review du refactoring."""
        task = {
            "type": "review_refactoring",
            "squad": "qa_squad",
            "agent": "code_reviewer",
            "data": {
                "files_changed": context["refactoring"]["files_changed"],
                "code_diff": context["refactoring"]["code_diff"],
                "test_results": context["test_results"],
                "improvements": context["refactoring"]["improvements"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "approved": result.get("approved", False),
            "review_comments": result.get("comments"),
            "quality_improvements": result.get("quality_improvements"),
            "maintainability_score": result.get("maintainability_score"),
            "ready_for_merge": result.get("ready_for_merge", False)
        }
