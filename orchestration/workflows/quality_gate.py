"""
Quality Gate Workflow

Workflow automatique de vérification qualité avec auto-fix:
TypeCheck → Lint → Test → Security → Performance

Peut être déclenché automatiquement avant chaque commit/PR.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class QualityGateWorkflow:
    """
    Workflow de vérification qualité automatique.

    Étapes:
    1. TypeCheck - Vérification des types TypeScript
    2. Lint - Linting et formatage du code
    3. Test - Exécution des tests (unit/integration/e2e)
    4. Security - Scan de sécurité (vulnérabilités, secrets)
    5. Performance - Analyse de performance et bundle size

    Features:
    - Auto-fix activé par défaut
    - Rapport détaillé des problèmes
    - Score qualité global
    """

    def __init__(self):
        self.name = "quality_gate"
        self.description = "Workflow de vérification qualité automatique"
        self.steps = [
            "typecheck",
            "lint",
            "test",
            "security",
            "performance"
        ]
        self.required_squads = [
            "qa_squad"  # QA Engineer
        ]
        self.auto_fix_enabled = True
        self.logger = logging.getLogger(f"devora.workflow.{self.name}")

    async def execute(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """
        Exécute le workflow de quality gate.

        Args:
            context: Contexte du workflow avec:
                - target_path: Chemin du code à vérifier (défaut: ".")
                - auto_fix: Activer l'auto-fix (défaut: True)
                - skip_tests: Skip les tests (défaut: False)
                - test_types: Types de tests à exécuter (défaut: ["unit", "integration"])
                - fail_threshold: Score minimum pour passer (défaut: 80)
            orchestrator: Instance de l'orchestrateur

        Returns:
            Résultat du workflow avec outputs de chaque étape
        """
        self.logger.info(f"Starting quality gate workflow")

        results = {
            "workflow": self.name,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "steps": {},
            "context": context,
            "quality_score": 0
        }

        try:
            auto_fix = context.get("auto_fix", True)

            # Step 1: TypeCheck
            typecheck_result = await self._run_step(
                "typecheck",
                {**context, "auto_fix": auto_fix},
                orchestrator
            )
            results["steps"]["typecheck"] = typecheck_result

            # Step 2: Lint
            lint_result = await self._run_step(
                "lint",
                {**context, "auto_fix": auto_fix},
                orchestrator
            )
            results["steps"]["lint"] = lint_result

            # Step 3: Test
            if not context.get("skip_tests", False):
                test_result = await self._run_step(
                    "test",
                    context,
                    orchestrator
                )
                results["steps"]["test"] = test_result
            else:
                results["steps"]["test"] = {"status": "skipped"}

            # Step 4: Security
            security_result = await self._run_step(
                "security",
                context,
                orchestrator
            )
            results["steps"]["security"] = security_result

            # Step 5: Performance
            performance_result = await self._run_step(
                "performance",
                context,
                orchestrator
            )
            results["steps"]["performance"] = performance_result

            # Calculate overall quality score
            quality_score = self._calculate_quality_score(results["steps"])
            results["quality_score"] = quality_score

            # Determine if quality gate passed
            fail_threshold = context.get("fail_threshold", 80)
            results["passed"] = quality_score >= fail_threshold

            results["status"] = "completed"
            results["completed_at"] = datetime.utcnow().isoformat()

            self.logger.info(
                f"Quality gate workflow completed. Score: {quality_score}/100. "
                f"Passed: {results['passed']}"
            )

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = datetime.utcnow().isoformat()
            self.logger.error(f"Quality gate workflow failed: {str(e)}")

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
            "typecheck": self._typecheck_step,
            "lint": self._lint_step,
            "test": self._test_step,
            "security": self._security_step,
            "performance": self._performance_step
        }

        handler = step_handlers.get(step_name)
        if not handler:
            raise ValueError(f"Unknown step: {step_name}")

        return await handler(context, orchestrator)

    async def _typecheck_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape typecheck: Vérification des types TypeScript."""
        task = {
            "type": "typecheck",
            "squad": "qa_squad",
            "agent": "qa_engineer",
            "data": {
                "target_path": context.get("target_path", "."),
                "auto_fix": context.get("auto_fix", True)
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "passed": result.get("passed", False),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "files_checked": result.get("files_checked", 0),
            "auto_fixed": result.get("auto_fixed", 0)
        }

    async def _lint_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape lint: Linting et formatage du code."""
        task = {
            "type": "lint",
            "squad": "qa_squad",
            "agent": "qa_engineer",
            "data": {
                "target_path": context.get("target_path", "."),
                "auto_fix": context.get("auto_fix", True),
                "rules": ["eslint", "prettier"]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "passed": result.get("passed", False),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "files_checked": result.get("files_checked", 0),
            "auto_fixed": result.get("auto_fixed", 0)
        }

    async def _test_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape test: Exécution des tests."""
        test_types = context.get("test_types", ["unit", "integration"])

        task = {
            "type": "run_tests",
            "squad": "qa_squad",
            "agent": "qa_engineer",
            "data": {
                "test_types": test_types,
                "coverage_threshold": context.get("coverage_threshold", 80)
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "passed": result.get("passed", False),
            "total_tests": result.get("total_tests", 0),
            "passed_tests": result.get("passed_tests", 0),
            "failed_tests": result.get("failed_tests", 0),
            "coverage": result.get("coverage", 0),
            "failures": result.get("failures", [])
        }

    async def _security_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape security: Scan de sécurité."""
        task = {
            "type": "security_scan",
            "squad": "qa_squad",
            "agent": "security_engineer",
            "data": {
                "target_path": context.get("target_path", "."),
                "scan_types": [
                    "dependencies",    # npm audit
                    "secrets",         # gitguardian
                    "sast",           # static analysis
                    "license"         # license compliance
                ]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "passed": result.get("passed", False),
            "vulnerabilities": {
                "critical": result.get("critical", 0),
                "high": result.get("high", 0),
                "medium": result.get("medium", 0),
                "low": result.get("low", 0)
            },
            "secrets_found": result.get("secrets_found", []),
            "license_issues": result.get("license_issues", []),
            "recommendations": result.get("recommendations", [])
        }

    async def _performance_step(
        self,
        context: Dict[str, Any],
        orchestrator: Any
    ) -> Dict[str, Any]:
        """Étape performance: Analyse de performance."""
        task = {
            "type": "performance_analysis",
            "squad": "qa_squad",
            "agent": "performance_engineer",
            "data": {
                "target_path": context.get("target_path", "."),
                "metrics": [
                    "bundle_size",
                    "lighthouse",
                    "memory_usage",
                    "render_time"
                ]
            }
        }

        result = await orchestrator.delegate_task(task)

        return {
            "status": "completed",
            "passed": result.get("passed", False),
            "bundle_size": result.get("bundle_size"),
            "lighthouse_score": result.get("lighthouse_score", 0),
            "memory_usage": result.get("memory_usage"),
            "render_time": result.get("render_time"),
            "bottlenecks": result.get("bottlenecks", []),
            "recommendations": result.get("recommendations", [])
        }

    def _calculate_quality_score(self, steps: Dict[str, Any]) -> int:
        """
        Calcule le score qualité global basé sur les résultats de chaque étape.

        Args:
            steps: Résultats de toutes les étapes

        Returns:
            Score qualité sur 100
        """
        scores = []

        # TypeCheck (20 points)
        typecheck = steps.get("typecheck", {})
        if typecheck.get("passed"):
            scores.append(20)
        elif typecheck.get("warnings"):
            scores.append(10)
        else:
            scores.append(0)

        # Lint (20 points)
        lint = steps.get("lint", {})
        if lint.get("passed"):
            scores.append(20)
        elif lint.get("warnings"):
            scores.append(10)
        else:
            scores.append(0)

        # Test (30 points)
        test = steps.get("test", {})
        if test.get("status") == "skipped":
            scores.append(15)  # Partial score if skipped
        elif test.get("passed"):
            coverage = test.get("coverage", 0)
            scores.append(int(30 * (coverage / 100)))
        else:
            scores.append(0)

        # Security (20 points)
        security = steps.get("security", {})
        vulnerabilities = security.get("vulnerabilities", {})
        critical = vulnerabilities.get("critical", 0)
        high = vulnerabilities.get("high", 0)

        if critical > 0:
            scores.append(0)
        elif high > 0:
            scores.append(10)
        else:
            scores.append(20)

        # Performance (10 points)
        performance = steps.get("performance", {})
        lighthouse = performance.get("lighthouse_score", 0)
        scores.append(int(10 * (lighthouse / 100)))

        return sum(scores)
