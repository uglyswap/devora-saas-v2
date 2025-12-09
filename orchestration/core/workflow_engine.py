"""
Workflow Engine - Predefined Workflow Execution for Devora

This module manages and executes predefined workflows for common tasks:
1. Full Stack Feature - Complete feature implementation
2. API Development - Backend API creation
3. Frontend Component - React component development
4. Database Migration - Database schema changes
5. Security Audit - Comprehensive security review
6. Performance Optimization - System performance improvements
7. AI Integration - LLM/AI feature integration
8. Mobile App Development - Cross-platform mobile development
9. Data Pipeline - ETL and analytics pipeline
10. Design System - Design system creation and maintenance

Each workflow defines:
- Required squads and their execution order
- Parallel vs sequential execution
- Quality gates and checkpoints
- Expected outputs
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import json


class WorkflowStepType(Enum):
    """Types of workflow steps."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    CHECKPOINT = "checkpoint"


@dataclass
class WorkflowStep:
    """Represents a step in a workflow.

    Attributes:
        name: Step name
        type: Step type
        squads: List of squads to execute
        condition: Optional condition for conditional steps
        timeout: Step timeout in seconds
        required: Whether step is required
    """
    name: str
    type: WorkflowStepType
    squads: List[str]
    condition: Optional[str] = None
    timeout: int = 300
    required: bool = True


@dataclass
class Workflow:
    """Represents a complete workflow.

    Attributes:
        name: Workflow name
        description: Workflow description
        steps: List of workflow steps
        quality_gate: Whether to run quality gate
        expected_duration: Expected duration in minutes
        tags: Workflow tags for categorization
    """
    name: str
    description: str
    steps: List[WorkflowStep]
    quality_gate: bool = True
    expected_duration: int = 30
    tags: List[str] = field(default_factory=list)


class WorkflowEngine:
    """Engine for executing predefined workflows.

    This engine manages the execution of complex multi-step workflows,
    coordinating multiple squads and handling dependencies, conditions,
    and quality gates.
    """

    def __init__(
        self,
        squad_manager: Any,
        callbacks: Optional[List[Callable]] = None
    ):
        """Initialize workflow engine.

        Args:
            squad_manager: SquadManager instance
            callbacks: List of callback functions
        """
        self.squad_manager = squad_manager
        self.callbacks = callbacks or []

        # Setup logging
        self.logger = logging.getLogger("devora.workflow_engine")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Initialize workflows
        self.workflows: Dict[str, Workflow] = {}
        self._register_workflows()

        self.logger.info(f"WorkflowEngine initialized with {len(self.workflows)} workflows")

    def _register_workflows(self) -> None:
        """Register all predefined workflows."""

        # Workflow 1: Full Stack Feature
        self.workflows["full_stack_feature"] = Workflow(
            name="full_stack_feature",
            description="Complete full-stack feature implementation",
            steps=[
                WorkflowStep(
                    name="planning",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["business", "architecture"]
                ),
                WorkflowStep(
                    name="design",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["design"]
                ),
                WorkflowStep(
                    name="development",
                    type=WorkflowStepType.PARALLEL,
                    squads=["frontend", "backend", "data"]
                ),
                WorkflowStep(
                    name="quality_check",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality"]
                ),
                WorkflowStep(
                    name="deployment",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["infrastructure"]
                )
            ],
            quality_gate=True,
            expected_duration=45,
            tags=["feature", "full-stack", "complete"]
        )

        # Workflow 2: API Development
        self.workflows["api_development"] = Workflow(
            name="api_development",
            description="Backend API development and integration",
            steps=[
                WorkflowStep(
                    name="architecture",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["architecture"]
                ),
                WorkflowStep(
                    name="development",
                    type=WorkflowStepType.PARALLEL,
                    squads=["backend", "data"]
                ),
                WorkflowStep(
                    name="testing",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality"]
                )
            ],
            quality_gate=True,
            expected_duration=30,
            tags=["backend", "api", "development"]
        )

        # Workflow 3: Frontend Component
        self.workflows["frontend_component"] = Workflow(
            name="frontend_component",
            description="React component development with design",
            steps=[
                WorkflowStep(
                    name="design",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["design"]
                ),
                WorkflowStep(
                    name="development",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["frontend"]
                ),
                WorkflowStep(
                    name="review",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality"]
                )
            ],
            quality_gate=True,
            expected_duration=20,
            tags=["frontend", "component", "react"]
        )

        # Workflow 4: Database Migration
        self.workflows["database_migration"] = Workflow(
            name="database_migration",
            description="Database schema migration and data pipeline",
            steps=[
                WorkflowStep(
                    name="planning",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["architecture", "data"]
                ),
                WorkflowStep(
                    name="implementation",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["backend"]
                ),
                WorkflowStep(
                    name="validation",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality", "data"]
                )
            ],
            quality_gate=True,
            expected_duration=35,
            tags=["database", "migration", "data"]
        )

        # Workflow 5: Security Audit
        self.workflows["security_audit"] = Workflow(
            name="security_audit",
            description="Comprehensive security audit and fixes",
            steps=[
                WorkflowStep(
                    name="audit",
                    type=WorkflowStepType.PARALLEL,
                    squads=["architecture", "backend", "frontend", "infrastructure"]
                ),
                WorkflowStep(
                    name="fixes",
                    type=WorkflowStepType.PARALLEL,
                    squads=["backend", "frontend"]
                ),
                WorkflowStep(
                    name="validation",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality"]
                )
            ],
            quality_gate=True,
            expected_duration=40,
            tags=["security", "audit", "compliance"]
        )

        # Workflow 6: Performance Optimization
        self.workflows["performance_optimization"] = Workflow(
            name="performance_optimization",
            description="System-wide performance improvements",
            steps=[
                WorkflowStep(
                    name="analysis",
                    type=WorkflowStepType.PARALLEL,
                    squads=["frontend", "backend", "data", "infrastructure"]
                ),
                WorkflowStep(
                    name="optimization",
                    type=WorkflowStepType.PARALLEL,
                    squads=["frontend", "backend", "data"]
                ),
                WorkflowStep(
                    name="validation",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality"]
                )
            ],
            quality_gate=True,
            expected_duration=50,
            tags=["performance", "optimization", "scaling"]
        )

        # Workflow 7: AI Integration
        self.workflows["ai_integration"] = Workflow(
            name="ai_integration",
            description="AI/ML feature integration with LLMs",
            steps=[
                WorkflowStep(
                    name="planning",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["business", "ai"]
                ),
                WorkflowStep(
                    name="development",
                    type=WorkflowStepType.PARALLEL,
                    squads=["ai", "backend", "frontend"]
                ),
                WorkflowStep(
                    name="testing",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality", "ai"]
                )
            ],
            quality_gate=True,
            expected_duration=40,
            tags=["ai", "ml", "llm", "integration"]
        )

        # Workflow 8: Mobile App Development
        self.workflows["mobile_app"] = Workflow(
            name="mobile_app",
            description="Cross-platform mobile app development",
            steps=[
                WorkflowStep(
                    name="design",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["design", "business"]
                ),
                WorkflowStep(
                    name="backend_prep",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["backend"]
                ),
                WorkflowStep(
                    name="development",
                    type=WorkflowStepType.PARALLEL,
                    squads=["mobile", "backend"]
                ),
                WorkflowStep(
                    name="testing",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality"]
                )
            ],
            quality_gate=True,
            expected_duration=60,
            tags=["mobile", "ios", "android", "react-native"]
        )

        # Workflow 9: Data Pipeline
        self.workflows["data_pipeline"] = Workflow(
            name="data_pipeline",
            description="ETL and analytics pipeline creation",
            steps=[
                WorkflowStep(
                    name="planning",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["business", "data"]
                ),
                WorkflowStep(
                    name="infrastructure",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["infrastructure"]
                ),
                WorkflowStep(
                    name="development",
                    type=WorkflowStepType.PARALLEL,
                    squads=["data", "backend"]
                ),
                WorkflowStep(
                    name="validation",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality", "data"]
                )
            ],
            quality_gate=True,
            expected_duration=45,
            tags=["data", "etl", "analytics", "pipeline"]
        )

        # Workflow 10: Design System
        self.workflows["design_system"] = Workflow(
            name="design_system",
            description="Design system creation and maintenance",
            steps=[
                WorkflowStep(
                    name="foundation",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["design"]
                ),
                WorkflowStep(
                    name="implementation",
                    type=WorkflowStepType.PARALLEL,
                    squads=["frontend", "design"]
                ),
                WorkflowStep(
                    name="documentation",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["design", "frontend"]
                ),
                WorkflowStep(
                    name="review",
                    type=WorkflowStepType.SEQUENTIAL,
                    squads=["quality"]
                )
            ],
            quality_gate=True,
            expected_duration=50,
            tags=["design", "design-system", "components", "ui"]
        )

        self.logger.info("All 10 workflows registered successfully")

    def get_available_workflows(self) -> List[str]:
        """Get list of available workflow names.

        Returns:
            List of workflow names
        """
        return list(self.workflows.keys())

    def get_workflow_info(self, workflow_name: str) -> Dict[str, Any]:
        """Get detailed information about a workflow.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Dictionary with workflow information
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {"error": f"Workflow '{workflow_name}' not found"}

        return {
            "name": workflow.name,
            "description": workflow.description,
            "steps": [
                {
                    "name": step.name,
                    "type": step.type.value,
                    "squads": step.squads,
                    "required": step.required
                }
                for step in workflow.steps
            ],
            "quality_gate": workflow.quality_gate,
            "expected_duration": workflow.expected_duration,
            "tags": workflow.tags
        }

    async def execute_workflow(
        self,
        workflow_name: str,
        context: Dict[str, Any]
    ) -> Any:
        """Execute a workflow.

        Args:
            workflow_name: Name of workflow to execute
            context: Execution context

        Returns:
            WorkflowResult with execution details
        """
        try:
            from .orchestrator_ultimate import OrchestratorResult
        except ImportError:
            from orchestrator_ultimate import OrchestratorResult

        workflow = self.workflows.get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        self.logger.info(f"Executing workflow: {workflow_name}")

        start_time = datetime.now()

        self._emit_callback("workflow_started", {
            "workflow": workflow_name,
            "steps": len(workflow.steps)
        })

        outputs = {}
        errors = []

        # Execute each step
        for step_index, step in enumerate(workflow.steps):
            try:
                self._emit_callback("workflow_step_started", {
                    "workflow": workflow_name,
                    "step": step.name,
                    "step_index": step_index + 1,
                    "total_steps": len(workflow.steps)
                })

                step_result = await self._execute_step(step, context, outputs)
                outputs[step.name] = step_result

                self._emit_callback("workflow_step_completed", {
                    "workflow": workflow_name,
                    "step": step.name,
                    "status": "success"
                })

            except Exception as e:
                error = {
                    "step": step.name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                errors.append(error)

                self.logger.error(f"Workflow step failed: {step.name}: {str(e)}")

                if step.required:
                    self._emit_callback("workflow_failed", {
                        "workflow": workflow_name,
                        "step": step.name,
                        "error": str(e)
                    })

                    return OrchestratorResult(
                        status="failed",
                        outputs=outputs,
                        errors=errors,
                        execution_plan={
                            "workflow": workflow_name,
                            "completed_steps": step_index,
                            "total_steps": len(workflow.steps)
                        }
                    )

        execution_time = (datetime.now() - start_time).total_seconds()

        self._emit_callback("workflow_completed", {
            "workflow": workflow_name,
            "execution_time": execution_time
        })

        # Calculate metrics
        total_tokens = 0
        agents_executed = 0

        for step_output in outputs.values():
            if isinstance(step_output, dict):
                for squad_output in step_output.values():
                    if isinstance(squad_output, dict):
                        metrics = squad_output.get("metrics", {})
                        total_tokens += metrics.get("total_tokens", 0)
                        agents_executed += metrics.get("agents_executed", 0)

        return OrchestratorResult(
            status="success",
            outputs=outputs,
            metrics={
                "execution_time": execution_time,
                "total_tokens": total_tokens,
                "agents_executed": agents_executed
            },
            errors=errors,
            execution_plan={
                "workflow": workflow_name,
                "completed_steps": len(workflow.steps),
                "total_steps": len(workflow.steps)
            }
        )

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
        previous_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow step.

        Args:
            step: Workflow step to execute
            context: Execution context
            previous_outputs: Outputs from previous steps

        Returns:
            Step execution results
        """
        self.logger.info(f"Executing step: {step.name} ({step.type.value})")

        # Add previous outputs to context
        step_context = {
            **context,
            "previous_outputs": previous_outputs
        }

        # Execute based on step type
        if step.type == WorkflowStepType.SEQUENTIAL:
            return await self._execute_sequential_step(step, step_context)
        elif step.type == WorkflowStepType.PARALLEL:
            return await self._execute_parallel_step(step, step_context)
        elif step.type == WorkflowStepType.CONDITIONAL:
            return await self._execute_conditional_step(step, step_context)
        elif step.type == WorkflowStepType.CHECKPOINT:
            return await self._execute_checkpoint_step(step, step_context)
        else:
            raise ValueError(f"Unknown step type: {step.type}")

    async def _execute_sequential_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute squads sequentially.

        Args:
            step: Workflow step
            context: Execution context

        Returns:
            Combined results
        """
        results = {}
        step_context = context.copy()

        for squad_name in step.squads:
            result = await self.squad_manager.execute_squad(squad_name, step_context)
            results[squad_name] = result

            # Add result to context for next squad
            step_context[f"{squad_name}_output"] = result

        return results

    async def _execute_parallel_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute squads in parallel.

        Args:
            step: Workflow step
            context: Execution context

        Returns:
            Combined results
        """
        tasks = [
            self.squad_manager.execute_squad(squad_name, context)
            for squad_name in step.squads
        ]

        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        results = {}
        for squad_name, result in zip(step.squads, results_list):
            if isinstance(result, Exception):
                self.logger.error(f"Squad {squad_name} failed: {str(result)}")
                results[squad_name] = {"status": "failed", "error": str(result)}
            else:
                results[squad_name] = result

        return results

    async def _execute_conditional_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute step conditionally.

        Args:
            step: Workflow step
            context: Execution context

        Returns:
            Conditional execution results
        """
        # Evaluate condition
        condition_met = self._evaluate_condition(step.condition, context)

        if condition_met:
            return await self._execute_parallel_step(step, context)
        else:
            return {"status": "skipped", "reason": "Condition not met"}

    async def _execute_checkpoint_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute checkpoint step for validation.

        Args:
            step: Workflow step
            context: Execution context

        Returns:
            Checkpoint results
        """
        # Run quality checks at checkpoint
        return {
            "status": "checkpoint",
            "timestamp": datetime.now().isoformat(),
            "context_snapshot": context
        }

    def _evaluate_condition(
        self,
        condition: Optional[str],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a condition string.

        Args:
            condition: Condition expression
            context: Execution context

        Returns:
            True if condition is met
        """
        if not condition:
            return True

        # Simple condition evaluation
        # In production, use safer expression evaluator
        try:
            return eval(condition, {"context": context})
        except Exception as e:
            self.logger.error(f"Condition evaluation failed: {str(e)}")
            return False

    def _emit_callback(self, event: str, data: Dict[str, Any]) -> None:
        """Emit event to callbacks.

        Args:
            event: Event type
            data: Event data
        """
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                self.logger.error(f"Callback error: {str(e)}")
