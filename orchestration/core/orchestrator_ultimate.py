"""
Orchestrator Ultimate - Main Orchestration Engine for Devora

This module provides the ultimate orchestrator that coordinates all 28 agents
across 10 specialized squads. It handles:
- Intelligent request analysis and agent selection
- Parallel and sequential execution with asyncio
- Progress tracking via SSE events
- Quality gate integration
- Workflow management
- Token and cost optimization
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import json

try:
    from .base_agent import BaseAgent, AgentConfig, AgentStatus
    from .squad_manager import SquadManager
    from .workflow_engine import WorkflowEngine
    from .quality_gate_engine import QualityGateEngine
except ImportError:
    from base_agent import BaseAgent, AgentConfig, AgentStatus
    from squad_manager import SquadManager
    from workflow_engine import WorkflowEngine
    from quality_gate_engine import QualityGateEngine


class ExecutionMode(Enum):
    """Execution modes for orchestrator."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    WORKFLOW = "workflow"


@dataclass
class OrchestratorRequest:
    """Request structure for orchestration.

    Attributes:
        task: Main task description
        context: Additional context and requirements
        workflow: Optional workflow name to execute
        mode: Execution mode (sequential, parallel, hybrid, workflow)
        quality_gate: Whether to run quality gate checks
        max_parallel: Maximum number of parallel agents
        priority: Request priority (0-10)
        metadata: Additional metadata
    """
    task: str
    context: Dict[str, Any] = field(default_factory=dict)
    workflow: Optional[str] = None
    mode: ExecutionMode = ExecutionMode.HYBRID
    quality_gate: bool = True
    max_parallel: int = 5
    priority: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestratorResult:
    """Result structure from orchestration.

    Attributes:
        status: Overall execution status
        outputs: Outputs from all executed agents
        metrics: Aggregated metrics
        quality_report: Quality gate report (if enabled)
        execution_plan: Executed plan details
        errors: List of errors encountered
        timestamp: Execution timestamp
    """
    status: str
    outputs: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    quality_report: Optional[Dict[str, Any]] = None
    execution_plan: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class OrchestratorUltimate:
    """Ultimate orchestrator for Devora transformation system.

    This orchestrator coordinates 28 specialized agents across 10 squads:
    - Squad Architecture (Architect, Tech Lead, Security Architect)
    - Squad Frontend (React Dev, UI/UX Designer, Performance Expert)
    - Squad Backend (API Dev, Database Expert, Integration Specialist)
    - Squad Quality (Tester, Code Reviewer, DevOps Engineer)
    - Squad AI (AI/ML Engineer, Prompt Engineer, Data Scientist)
    - Squad Design (Product Designer, UX Researcher, Design System Lead)
    - Squad Business (Product Manager, Business Analyst, Strategy Consultant)
    - Squad Infrastructure (Cloud Architect, SRE, Platform Engineer)
    - Squad Data (Data Engineer, Analytics Engineer, BI Developer)
    - Squad Mobile (iOS Developer, Android Developer, React Native Expert)

    Features:
    - Intelligent agent selection based on task analysis
    - Parallel and sequential execution with dependency management
    - Real-time progress tracking via callbacks (SSE compatible)
    - Automatic quality gate validation
    - Cost and token optimization
    - Workflow-based execution for common patterns
    """

    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
        callbacks: Optional[List[Callable]] = None,
        enable_quality_gate: bool = True,
        log_level: str = "INFO"
    ):
        """Initialize the orchestrator.

        Args:
            api_key: OpenRouter API key
            model: Default LLM model to use
            callbacks: List of callback functions for progress events
            enable_quality_gate: Whether to enable quality gate by default
            log_level: Logging level
        """
        self.api_key = api_key
        self.model = model
        self.callbacks = callbacks or []
        self.enable_quality_gate = enable_quality_gate

        # Setup logging
        self.logger = self._setup_logger(log_level)

        # Initialize managers
        self.squad_manager = SquadManager(api_key, model, callbacks)
        self.workflow_engine = WorkflowEngine(self.squad_manager, callbacks)
        self.quality_gate = QualityGateEngine(callbacks) if enable_quality_gate else None

        # Execution state
        self.active_agents: Set[str] = set()
        self.execution_history: List[Dict[str, Any]] = []

        # Metrics
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_executions = 0

        self.logger.info("OrchestratorUltimate initialized with 10 squads (28 agents)")

    def _setup_logger(self, log_level: str) -> logging.Logger:
        """Setup orchestrator logger.

        Args:
            log_level: Logging level

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("devora.orchestrator.ultimate")
        logger.setLevel(getattr(logging, log_level.upper()))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _emit_progress(self, event: str, data: Dict[str, Any]) -> None:
        """Emit progress event to all callbacks (SSE compatible).

        Args:
            event: Event type
            data: Event data
        """
        event_data = {
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                self.logger.error(f"Callback error: {str(e)}")

        self.logger.debug(f"Event emitted: {event}")

    async def execute(
        self,
        request: OrchestratorRequest,
        workflow: Optional[str] = None
    ) -> OrchestratorResult:
        """Execute orchestration request.

        This is the main entry point for the orchestrator. It:
        1. Analyzes the request to determine required agents
        2. Creates an execution plan (parallel/sequential)
        3. Executes agents according to plan
        4. Runs quality gate if enabled
        5. Returns aggregated results

        Args:
            request: Orchestration request
            workflow: Optional workflow name (overrides request.workflow)

        Returns:
            OrchestratorResult with execution details
        """
        start_time = datetime.now()
        self.total_executions += 1

        self._emit_progress("orchestration_started", {
            "task": request.task,
            "mode": request.mode.value,
            "workflow": workflow or request.workflow
        })

        try:
            # Use workflow if specified
            if workflow or request.workflow:
                workflow_name = workflow or request.workflow
                self.logger.info(f"Executing workflow: {workflow_name}")

                result = await self.workflow_engine.execute_workflow(
                    workflow_name,
                    request.context
                )

                # Run quality gate if enabled
                if request.quality_gate and self.quality_gate:
                    self._emit_progress("quality_gate_started", {})
                    quality_report = await self._run_quality_gate(result.outputs)
                    result.quality_report = quality_report

                return result

            # Standard execution: analyze and plan
            self.logger.info("Analyzing request to determine required agents")
            execution_plan = await self._analyze_request(request)

            self._emit_progress("execution_plan_created", {
                "agents": execution_plan["agents"],
                "squads": execution_plan["squads"],
                "mode": execution_plan["mode"]
            })

            # Execute according to plan
            self.logger.info(f"Executing with mode: {execution_plan['mode']}")
            outputs = await self._execute_plan(execution_plan, request)

            # Run quality gate if enabled
            quality_report = None
            if request.quality_gate and self.quality_gate:
                self._emit_progress("quality_gate_started", {})
                quality_report = await self._run_quality_gate(outputs)

            # Calculate metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            metrics = self._calculate_metrics(outputs, execution_time)

            self._emit_progress("orchestration_completed", {
                "status": "success",
                "metrics": metrics
            })

            return OrchestratorResult(
                status="success",
                outputs=outputs,
                metrics=metrics,
                quality_report=quality_report,
                execution_plan=execution_plan
            )

        except Exception as e:
            self.logger.error(f"Orchestration failed: {str(e)}", exc_info=True)

            execution_time = (datetime.now() - start_time).total_seconds()

            self._emit_progress("orchestration_failed", {
                "error": str(e),
                "execution_time": execution_time
            })

            return OrchestratorResult(
                status="failed",
                errors=[{
                    "type": "orchestration_error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }],
                metrics={"execution_time": execution_time}
            )

    async def _analyze_request(
        self,
        request: OrchestratorRequest
    ) -> Dict[str, Any]:
        """Analyze request to determine which agents to activate.

        Uses LLM-based analysis to intelligently select agents and squads
        based on the task description and context.

        Args:
            request: Orchestration request

        Returns:
            Execution plan with selected agents and mode
        """
        self.logger.debug("Analyzing request with LLM")

        # Build analysis prompt
        analysis_prompt = f"""Analyze this software development task and determine which agents and squads should be involved.

TASK: {request.task}

CONTEXT: {json.dumps(request.context, indent=2)}

AVAILABLE SQUADS AND AGENTS:
1. Squad Architecture: Architect, Tech Lead, Security Architect
2. Squad Frontend: React Developer, UI/UX Designer, Performance Expert
3. Squad Backend: API Developer, Database Expert, Integration Specialist
4. Squad Quality: Tester, Code Reviewer, DevOps Engineer
5. Squad AI: AI/ML Engineer, Prompt Engineer, Data Scientist
6. Squad Design: Product Designer, UX Researcher, Design System Lead
7. Squad Business: Product Manager, Business Analyst, Strategy Consultant
8. Squad Infrastructure: Cloud Architect, SRE, Platform Engineer
9. Squad Data: Data Engineer, Analytics Engineer, BI Developer
10. Squad Mobile: iOS Developer, Android Developer, React Native Expert

Respond in JSON format with:
{{
  "squads": ["squad1", "squad2"],
  "agents": ["agent1", "agent2"],
  "execution_mode": "parallel|sequential|hybrid",
  "reasoning": "explanation of selections"
}}"""

        # Call LLM for analysis
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at analyzing software development tasks and selecting the right specialized agents."
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse JSON response
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)

            self.logger.info(f"Analysis complete. Selected: {len(analysis['agents'])} agents, {len(analysis['squads'])} squads")

            return {
                "agents": analysis["agents"],
                "squads": analysis["squads"],
                "mode": analysis.get("execution_mode", request.mode.value),
                "reasoning": analysis.get("reasoning", "")
            }

        except Exception as e:
            self.logger.warning(f"LLM analysis failed, using fallback: {str(e)}")

            # Fallback: use all squads for complex tasks
            return {
                "agents": [],
                "squads": ["architecture", "frontend", "backend", "quality"],
                "mode": request.mode.value,
                "reasoning": "Fallback selection due to analysis error"
            }

    async def _execute_plan(
        self,
        plan: Dict[str, Any],
        request: OrchestratorRequest
    ) -> Dict[str, Any]:
        """Execute the planned agent activations.

        Args:
            plan: Execution plan from analysis
            request: Original request

        Returns:
            Dictionary of outputs from all executed agents
        """
        outputs = {}

        mode = plan.get("mode", request.mode.value)

        if mode == "parallel":
            outputs = await self._execute_parallel(plan["squads"], request)
        elif mode == "sequential":
            outputs = await self._execute_sequential(plan["squads"], request)
        else:  # hybrid
            outputs = await self._execute_hybrid(plan["squads"], request)

        return outputs

    async def _execute_parallel(
        self,
        squads: List[str],
        request: OrchestratorRequest
    ) -> Dict[str, Any]:
        """Execute squads in parallel.

        Args:
            squads: List of squad names to execute
            request: Original request

        Returns:
            Combined outputs from all squads
        """
        self.logger.info(f"Executing {len(squads)} squads in parallel")

        tasks = []
        for squad_name in squads:
            task = self._execute_squad(squad_name, request.context)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        outputs = {}
        for squad_name, result in zip(squads, results):
            if isinstance(result, Exception):
                self.logger.error(f"Squad {squad_name} failed: {str(result)}")
                outputs[squad_name] = {"status": "failed", "error": str(result)}
            else:
                outputs[squad_name] = result

        return outputs

    async def _execute_sequential(
        self,
        squads: List[str],
        request: OrchestratorRequest
    ) -> Dict[str, Any]:
        """Execute squads sequentially, passing context forward.

        Args:
            squads: List of squad names to execute
            request: Original request

        Returns:
            Combined outputs from all squads
        """
        self.logger.info(f"Executing {len(squads)} squads sequentially")

        outputs = {}
        context = request.context.copy()

        for squad_name in squads:
            self._emit_progress("squad_started", {"squad": squad_name})

            result = await self._execute_squad(squad_name, context)
            outputs[squad_name] = result

            # Add result to context for next squad
            context[f"{squad_name}_output"] = result

            self._emit_progress("squad_completed", {
                "squad": squad_name,
                "status": result.get("status", "completed")
            })

        return outputs

    async def _execute_hybrid(
        self,
        squads: List[str],
        request: OrchestratorRequest
    ) -> Dict[str, Any]:
        """Execute squads in hybrid mode (intelligent parallel/sequential).

        This mode executes independent squads in parallel, but respects
        dependencies between squads.

        Args:
            squads: List of squad names to execute
            request: Original request

        Returns:
            Combined outputs from all squads
        """
        self.logger.info(f"Executing {len(squads)} squads in hybrid mode")

        # Get dependencies
        dependencies = self.squad_manager.get_squad_dependencies()

        # Build execution graph
        executed = set()
        outputs = {}
        context = request.context.copy()

        while len(executed) < len(squads):
            # Find squads that can execute now (dependencies met)
            ready = [
                s for s in squads
                if s not in executed and all(
                    dep in executed for dep in dependencies.get(s, [])
                )
            ]

            if not ready:
                # Circular dependency or error
                remaining = set(squads) - executed
                self.logger.error(f"Cannot execute remaining squads (circular deps?): {remaining}")
                break

            # Execute ready squads in parallel
            tasks = [self._execute_squad(squad, context) for squad in ready]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for squad_name, result in zip(ready, results):
                executed.add(squad_name)
                if isinstance(result, Exception):
                    outputs[squad_name] = {"status": "failed", "error": str(result)}
                else:
                    outputs[squad_name] = result
                    context[f"{squad_name}_output"] = result

        return outputs

    async def _execute_squad(
        self,
        squad_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific squad.

        Args:
            squad_name: Name of squad to execute
            context: Execution context

        Returns:
            Squad execution result
        """
        try:
            result = await self.squad_manager.execute_squad(squad_name, context)
            return result
        except Exception as e:
            self.logger.error(f"Squad execution failed: {squad_name}: {str(e)}")
            raise

    async def _run_quality_gate(
        self,
        outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run quality gate checks on outputs.

        Args:
            outputs: Outputs from agent execution

        Returns:
            Quality gate report
        """
        if not self.quality_gate:
            return {"status": "skipped", "reason": "Quality gate disabled"}

        try:
            report = await self.quality_gate.run_checks(outputs)

            self._emit_progress("quality_gate_completed", {
                "status": report["status"],
                "passed": report.get("passed", False)
            })

            return report

        except Exception as e:
            self.logger.error(f"Quality gate failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _calculate_metrics(
        self,
        outputs: Dict[str, Any],
        execution_time: float
    ) -> Dict[str, Any]:
        """Calculate aggregated metrics from all executions.

        Args:
            outputs: Outputs from all agents
            execution_time: Total execution time

        Returns:
            Aggregated metrics
        """
        total_tokens = 0
        total_cost = 0.0
        agents_executed = 0

        for squad_name, squad_output in outputs.items():
            if isinstance(squad_output, dict):
                metrics = squad_output.get("metrics", {})
                total_tokens += metrics.get("total_tokens", 0)
                total_cost += metrics.get("total_cost", 0.0)
                agents_executed += metrics.get("agents_executed", 0)

        self.total_tokens += total_tokens
        self.total_cost += total_cost

        return {
            "execution_time": execution_time,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "agents_executed": agents_executed,
            "squads_executed": len(outputs),
            "lifetime_tokens": self.total_tokens,
            "lifetime_cost": self.total_cost,
            "lifetime_executions": self.total_executions
        }

    def get_available_workflows(self) -> List[str]:
        """Get list of available workflow names.

        Returns:
            List of workflow names
        """
        return self.workflow_engine.get_available_workflows()

    def get_available_squads(self) -> List[str]:
        """Get list of available squad names.

        Returns:
            List of squad names
        """
        return self.squad_manager.get_available_squads()

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics.

        Returns:
            Current metrics
        """
        return {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "total_executions": self.total_executions,
            "active_agents": len(self.active_agents)
        }
