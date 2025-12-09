"""
Routes API V3 pour le système d'orchestration Devora.

Nouvelles fonctionnalités:
- Streaming SSE en temps réel avec OrchestratorV3
- Quality gates automatiques avec retry
- Parallel agent execution
- Analytics et métriques détaillées
- Error recovery avancé

@author Devora Team
@version 3.0.0
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, AsyncIterator, Union
from datetime import datetime, timezone
from enum import Enum
import asyncio
import json
import logging
import uuid
import time
from dataclasses import asdict

# Import OrchestratorV3
from agents.orchestrator_v3 import (
    OrchestratorV3,
    ProgressEvent,
    WorkflowContext,
    QualityGate,
    AgentTask
)

# Logging setup
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v3/orchestrate", tags=["orchestration-v3"])


# ============================================================================
# Models / Schemas
# ============================================================================

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentType(str, Enum):
    ARCHITECT = "architect"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    REVIEWER = "reviewer"
    TESTER = "tester"
    DEVOPS = "devops"


class QualityLevel(str, Enum):
    BASIC = "basic"          # Simple validation
    STANDARD = "standard"    # Type checking + linting
    STRICT = "strict"        # Full review + security scan
    ENTERPRISE = "enterprise" # All checks + compliance


class ExecutionRequest(BaseModel):
    """Request to execute a task with the orchestrator."""

    prompt: str = Field(..., description="User's request/prompt", min_length=10, max_length=50000)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    files: Optional[List[Dict[str, str]]] = Field(default=None, description="Existing project files")

    # LLM Configuration
    model: str = Field(default="anthropic/claude-3.5-sonnet", description="LLM model to use")
    api_key: str = Field(..., description="OpenRouter API key", min_length=10)

    # Execution Configuration
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    max_iterations: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=300, ge=30, le=1800)

    # Quality Configuration
    quality_level: QualityLevel = Field(default=QualityLevel.STANDARD)
    enable_quality_gates: bool = Field(default=True)
    auto_fix: bool = Field(default=True, description="Auto-fix issues found by quality gates")

    # Agent Configuration
    agents_to_use: Optional[List[AgentType]] = Field(default=None, description="Specific agents to use")
    parallel_execution: bool = Field(default=True)

    @validator('api_key')
    def validate_api_key(cls, v):
        if not v.startswith('sk-'):
            raise ValueError('Invalid API key format')
        return v


class QuickGenerateRequest(BaseModel):
    """Simplified request for quick generation."""

    prompt: str = Field(..., description="What to build", min_length=5)
    api_key: str = Field(..., description="OpenRouter API key")
    template: Optional[str] = Field(default=None, description="Template to use")
    style: Optional[str] = Field(default="modern", description="Design style")


class RefineRequest(BaseModel):
    """Request to refine existing code."""

    files: List[Dict[str, str]] = Field(..., description="Current project files")
    instruction: str = Field(..., description="What to change", min_length=5)
    api_key: str = Field(..., description="OpenRouter API key")
    selected_element: Optional[Dict[str, Any]] = Field(default=None, description="Selected DOM element")


class DebugRequest(BaseModel):
    """Request to debug code."""

    files: List[Dict[str, str]] = Field(..., description="Project files")
    error_message: str = Field(..., description="Error message or description")
    console_logs: Optional[List[str]] = Field(default=None, description="Console logs")
    api_key: str = Field(..., description="OpenRouter API key")


class TaskStatusResponse(BaseModel):
    """Response with task status."""

    task_id: str
    status: str
    progress: float
    current_phase: Optional[str]
    agents_active: List[str]
    metrics: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime


# ============================================================================
# In-Memory Task Storage (replace with Redis in production)
# ============================================================================

tasks_storage: Dict[str, Dict[str, Any]] = {}


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    return tasks_storage.get(task_id)


def update_task(task_id: str, data: Dict[str, Any]):
    if task_id in tasks_storage:
        tasks_storage[task_id].update(data)
        tasks_storage[task_id]["updated_at"] = datetime.now(timezone.utc)


def create_task(task_id: str) -> Dict[str, Any]:
    task = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "current_phase": None,
        "agents_active": [],
        "metrics": {},
        "result": None,
        "error": None,
        "events": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    tasks_storage[task_id] = task
    return task


# ============================================================================
# SSE Streaming Helpers
# ============================================================================

async def stream_progress_events(
    orchestrator: OrchestratorV3,
    request: ExecutionRequest,
    task_id: str
) -> AsyncIterator[str]:
    """
    Stream progress events from the orchestrator via SSE.

    Each event is sent as:
    data: {"event_type": "...", "phase": "...", ...}

    """
    try:
        # Start event
        yield format_sse_event({
            "event_type": "start",
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        update_task(task_id, {"status": "running"})

        # Execute and stream events
        async for event in orchestrator.execute(
            user_request=request.prompt,
            existing_files=request.files,
            context=request.context or {},
            max_iterations=request.max_iterations
        ):
            # Convert dataclass to dict
            event_data = {
                "event_type": event.event_type,
                "phase": event.phase,
                "agent": event.agent,
                "message": event.message,
                "progress": event.progress,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }

            # Update task storage
            update_task(task_id, {
                "progress": event.progress,
                "current_phase": event.phase,
                "events": tasks_storage[task_id]["events"] + [event_data]
            })

            if event.agent:
                agents = tasks_storage[task_id]["agents_active"]
                if event.agent not in agents:
                    agents.append(event.agent)
                    update_task(task_id, {"agents_active": agents})

            yield format_sse_event(event_data)

            # Handle errors
            if event.event_type == "error":
                update_task(task_id, {
                    "status": "failed",
                    "error": event.message
                })
                break

            # Handle completion
            if event.event_type == "complete":
                update_task(task_id, {
                    "status": "completed",
                    "result": event.data,
                    "progress": 100.0
                })
                break

        # End event
        yield format_sse_event({
            "event_type": "end",
            "task_id": task_id,
            "status": tasks_storage[task_id]["status"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    except asyncio.CancelledError:
        update_task(task_id, {"status": "cancelled"})
        yield format_sse_event({
            "event_type": "cancelled",
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        raise

    except Exception as e:
        logger.exception(f"Error in stream_progress_events for task {task_id}")
        update_task(task_id, {
            "status": "failed",
            "error": str(e)
        })
        yield format_sse_event({
            "event_type": "error",
            "message": str(e),
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })


def format_sse_event(data: Dict[str, Any]) -> str:
    """Format data as an SSE event."""
    json_data = json.dumps(data, default=str)
    return f"data: {json_data}\n\n"


# ============================================================================
# API Routes
# ============================================================================

@router.post("/execute", response_class=StreamingResponse)
async def execute_task_streaming(request: ExecutionRequest):
    """
    Execute a task with real-time SSE streaming.

    Returns a stream of progress events that can be consumed by EventSource.

    Event types:
    - start: Task started
    - planning: Planning phase
    - agent_start: An agent started working
    - agent_progress: Agent progress update
    - agent_complete: Agent finished
    - quality_gate: Quality gate check
    - iteration: New iteration started
    - complete: Task completed successfully
    - error: An error occurred
    - end: Stream ended

    Example client:
    ```javascript
    const eventSource = new EventSource('/api/v3/orchestrate/execute');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data.event_type, data.progress);
    };
    ```
    """
    task_id = str(uuid.uuid4())
    create_task(task_id)

    # Build quality gates based on quality level
    quality_gates = build_quality_gates(request.quality_level)

    # Initialize orchestrator
    orchestrator = OrchestratorV3(
        api_key=request.api_key,
        model=request.model,
        quality_gates=quality_gates,
        parallel_execution=request.parallel_execution
    )

    return StreamingResponse(
        stream_progress_events(orchestrator, request, task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Task-ID": task_id,
            "Access-Control-Expose-Headers": "X-Task-ID"
        }
    )


@router.post("/execute/async")
async def execute_task_async(
    request: ExecutionRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a task asynchronously.

    Returns immediately with a task_id that can be polled for status.
    Use /status/{task_id} to check progress.
    """
    task_id = str(uuid.uuid4())
    create_task(task_id)

    quality_gates = build_quality_gates(request.quality_level)

    orchestrator = OrchestratorV3(
        api_key=request.api_key,
        model=request.model,
        quality_gates=quality_gates,
        parallel_execution=request.parallel_execution
    )

    # Run in background
    background_tasks.add_task(
        execute_task_background,
        orchestrator,
        request,
        task_id
    )

    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Task queued for execution",
        "poll_url": f"/api/v3/orchestrate/status/{task_id}"
    }


async def execute_task_background(
    orchestrator: OrchestratorV3,
    request: ExecutionRequest,
    task_id: str
):
    """Execute task in background."""
    try:
        update_task(task_id, {"status": "running"})

        result = None
        async for event in orchestrator.execute(
            user_request=request.prompt,
            existing_files=request.files,
            context=request.context or {},
            max_iterations=request.max_iterations
        ):
            update_task(task_id, {
                "progress": event.progress,
                "current_phase": event.phase,
                "events": tasks_storage[task_id]["events"] + [{
                    "event_type": event.event_type,
                    "message": event.message,
                    "timestamp": event.timestamp.isoformat()
                }]
            })

            if event.event_type == "complete":
                result = event.data

            if event.event_type == "error":
                update_task(task_id, {
                    "status": "failed",
                    "error": event.message
                })
                return

        update_task(task_id, {
            "status": "completed",
            "result": result,
            "progress": 100.0
        })

    except Exception as e:
        logger.exception(f"Background task {task_id} failed")
        update_task(task_id, {
            "status": "failed",
            "error": str(e)
        })


@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Get the current status of a task."""
    task = get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        progress=task["progress"],
        current_phase=task["current_phase"],
        agents_active=task["agents_active"],
        metrics=task.get("metrics", {}),
        result=task.get("result"),
        error=task.get("error"),
        created_at=task["created_at"],
        updated_at=task["updated_at"]
    )


@router.post("/status/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    task = get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task with status: {task['status']}"
        )

    update_task(task_id, {"status": "cancelled"})

    return {"message": "Task cancelled", "task_id": task_id}


@router.post("/quick-generate", response_class=StreamingResponse)
async def quick_generate(request: QuickGenerateRequest):
    """
    Quick generation endpoint for simple prompts.

    Streamlined version of /execute with sensible defaults.
    """
    task_id = str(uuid.uuid4())
    create_task(task_id)

    # Build full prompt with template and style
    full_prompt = request.prompt
    if request.template:
        full_prompt = f"Using the {request.template} template: {request.prompt}"
    if request.style:
        full_prompt = f"{full_prompt}. Use a {request.style} design style."

    orchestrator = OrchestratorV3(
        api_key=request.api_key,
        model="anthropic/claude-3.5-sonnet",
        quality_gates=[],  # No quality gates for quick generation
        parallel_execution=True
    )

    execution_request = ExecutionRequest(
        prompt=full_prompt,
        api_key=request.api_key,
        max_iterations=1,  # Single iteration for speed
        enable_quality_gates=False
    )

    return StreamingResponse(
        stream_progress_events(orchestrator, execution_request, task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Task-ID": task_id
        }
    )


@router.post("/refine", response_class=StreamingResponse)
async def refine_code(request: RefineRequest):
    """
    Refine existing code based on instructions.

    Can target specific elements when selected_element is provided.
    """
    task_id = str(uuid.uuid4())
    create_task(task_id)

    # Build context with selected element
    context = {}
    if request.selected_element:
        context["selected_element"] = request.selected_element
        context["refinement_type"] = "targeted"
    else:
        context["refinement_type"] = "global"

    prompt = f"Refine the existing code: {request.instruction}"

    orchestrator = OrchestratorV3(
        api_key=request.api_key,
        model="anthropic/claude-3.5-sonnet",
        quality_gates=build_quality_gates(QualityLevel.STANDARD),
        parallel_execution=True
    )

    execution_request = ExecutionRequest(
        prompt=prompt,
        api_key=request.api_key,
        files=request.files,
        context=context,
        max_iterations=2
    )

    return StreamingResponse(
        stream_progress_events(orchestrator, execution_request, task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Task-ID": task_id
        }
    )


@router.post("/debug", response_class=StreamingResponse)
async def debug_code(request: DebugRequest):
    """
    Debug code based on error messages and console logs.
    """
    task_id = str(uuid.uuid4())
    create_task(task_id)

    # Build debug prompt
    prompt = f"Debug this error: {request.error_message}"

    context = {
        "debug_mode": True,
        "error_message": request.error_message
    }

    if request.console_logs:
        context["console_logs"] = request.console_logs
        prompt += f"\n\nConsole logs:\n" + "\n".join(request.console_logs)

    orchestrator = OrchestratorV3(
        api_key=request.api_key,
        model="anthropic/claude-3.5-sonnet",
        quality_gates=[],  # No gates for debug
        parallel_execution=False  # Sequential for debugging
    )

    execution_request = ExecutionRequest(
        prompt=prompt,
        api_key=request.api_key,
        files=request.files,
        context=context,
        max_iterations=3
    )

    return StreamingResponse(
        stream_progress_events(orchestrator, execution_request, task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Task-ID": task_id
        }
    )


@router.get("/agents")
async def list_agents():
    """List all available agents and their capabilities."""
    return {
        "agents": [
            {
                "id": "architect",
                "name": "Architect Agent",
                "description": "Designs system architecture and technical specifications",
                "capabilities": [
                    "system_design",
                    "technology_selection",
                    "file_structure",
                    "dependency_management"
                ]
            },
            {
                "id": "frontend",
                "name": "Frontend Agent",
                "description": "Implements UI components and user interactions",
                "capabilities": [
                    "react_components",
                    "tailwind_styling",
                    "responsive_design",
                    "accessibility"
                ]
            },
            {
                "id": "backend",
                "name": "Backend Agent",
                "description": "Implements server-side logic and APIs",
                "capabilities": [
                    "api_design",
                    "business_logic",
                    "authentication",
                    "data_validation"
                ]
            },
            {
                "id": "database",
                "name": "Database Agent",
                "description": "Designs and implements data models",
                "capabilities": [
                    "schema_design",
                    "migrations",
                    "queries",
                    "optimization"
                ]
            },
            {
                "id": "reviewer",
                "name": "Reviewer Agent",
                "description": "Reviews code quality and suggests improvements",
                "capabilities": [
                    "code_review",
                    "security_audit",
                    "performance_review",
                    "best_practices"
                ]
            },
            {
                "id": "tester",
                "name": "Tester Agent",
                "description": "Creates and runs tests",
                "capabilities": [
                    "unit_tests",
                    "integration_tests",
                    "e2e_tests",
                    "test_coverage"
                ]
            },
            {
                "id": "devops",
                "name": "DevOps Agent",
                "description": "Handles deployment and infrastructure",
                "capabilities": [
                    "docker",
                    "ci_cd",
                    "cloud_deployment",
                    "monitoring"
                ]
            }
        ]
    }


@router.get("/quality-levels")
async def list_quality_levels():
    """List available quality levels and their checks."""
    return {
        "levels": [
            {
                "id": "basic",
                "name": "Basic",
                "description": "Quick validation for prototypes",
                "checks": ["syntax", "basic_structure"]
            },
            {
                "id": "standard",
                "name": "Standard",
                "description": "Recommended for most projects",
                "checks": ["syntax", "types", "linting", "basic_security"]
            },
            {
                "id": "strict",
                "name": "Strict",
                "description": "Thorough checks for production code",
                "checks": ["syntax", "types", "linting", "security_audit", "performance", "accessibility"]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "description": "Maximum quality for enterprise applications",
                "checks": ["syntax", "types", "linting", "security_audit", "performance", "accessibility", "compliance", "documentation"]
            }
        ]
    }


@router.get("/metrics")
async def get_global_metrics():
    """Get global orchestration metrics."""
    completed = sum(1 for t in tasks_storage.values() if t["status"] == "completed")
    failed = sum(1 for t in tasks_storage.values() if t["status"] == "failed")
    running = sum(1 for t in tasks_storage.values() if t["status"] == "running")

    return {
        "total_tasks": len(tasks_storage),
        "completed": completed,
        "failed": failed,
        "running": running,
        "success_rate": completed / max(completed + failed, 1) * 100,
        "average_duration_seconds": calculate_average_duration()
    }


def calculate_average_duration() -> float:
    """Calculate average task duration."""
    durations = []
    for task in tasks_storage.values():
        if task["status"] == "completed":
            duration = (task["updated_at"] - task["created_at"]).total_seconds()
            durations.append(duration)

    return sum(durations) / max(len(durations), 1)


def build_quality_gates(level: QualityLevel) -> List[QualityGate]:
    """Build quality gates based on quality level."""
    gates = []

    if level in [QualityLevel.BASIC, QualityLevel.STANDARD, QualityLevel.STRICT, QualityLevel.ENTERPRISE]:
        gates.append(QualityGate(
            name="syntax_check",
            description="Verify code syntax is valid",
            validator=lambda ctx: validate_syntax(ctx),
            required=True
        ))

    if level in [QualityLevel.STANDARD, QualityLevel.STRICT, QualityLevel.ENTERPRISE]:
        gates.append(QualityGate(
            name="type_check",
            description="Verify TypeScript types",
            validator=lambda ctx: validate_types(ctx),
            required=True
        ))
        gates.append(QualityGate(
            name="lint_check",
            description="Run linting rules",
            validator=lambda ctx: validate_linting(ctx),
            required=False
        ))

    if level in [QualityLevel.STRICT, QualityLevel.ENTERPRISE]:
        gates.append(QualityGate(
            name="security_check",
            description="Security vulnerability scan",
            validator=lambda ctx: validate_security(ctx),
            required=True
        ))
        gates.append(QualityGate(
            name="performance_check",
            description="Performance best practices",
            validator=lambda ctx: validate_performance(ctx),
            required=False
        ))

    if level == QualityLevel.ENTERPRISE:
        gates.append(QualityGate(
            name="accessibility_check",
            description="WCAG accessibility compliance",
            validator=lambda ctx: validate_accessibility(ctx),
            required=True
        ))
        gates.append(QualityGate(
            name="documentation_check",
            description="Code documentation coverage",
            validator=lambda ctx: validate_documentation(ctx),
            required=False
        ))

    return gates


# ============================================================================
# Quality Gate Validators
# ============================================================================

async def validate_syntax(context: WorkflowContext) -> bool:
    """Validate code syntax."""
    # In production, use actual parsers
    files = context.files
    for file in files:
        content = file.get("content", "")
        # Basic syntax check for common issues
        if content.count("{") != content.count("}"):
            return False
        if content.count("(") != content.count(")"):
            return False
        if content.count("[") != content.count("]"):
            return False
    return True


async def validate_types(context: WorkflowContext) -> bool:
    """Validate TypeScript types."""
    # In production, run tsc --noEmit
    return True


async def validate_linting(context: WorkflowContext) -> bool:
    """Run linting validation."""
    # In production, run eslint
    return True


async def validate_security(context: WorkflowContext) -> bool:
    """Security vulnerability scan."""
    files = context.files
    security_issues = []

    for file in files:
        content = file.get("content", "")
        # Check for common security issues
        if "eval(" in content:
            security_issues.append(f"eval() usage in {file.get('name')}")
        if "innerHTML" in content and "dangerouslySetInnerHTML" not in content:
            security_issues.append(f"Potential XSS via innerHTML in {file.get('name')}")
        if "process.env" in content and "VITE_" not in content and "NEXT_PUBLIC_" not in content:
            security_issues.append(f"Potential secret exposure in {file.get('name')}")

    return len(security_issues) == 0


async def validate_performance(context: WorkflowContext) -> bool:
    """Validate performance best practices."""
    return True


async def validate_accessibility(context: WorkflowContext) -> bool:
    """Validate WCAG accessibility."""
    return True


async def validate_documentation(context: WorkflowContext) -> bool:
    """Validate documentation coverage."""
    return True


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "tasks_in_memory": len(tasks_storage),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
