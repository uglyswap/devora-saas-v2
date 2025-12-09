"""
Routes API pour le système d'orchestration Devora.

Ce module expose le nouveau système d'orchestration multi-agents via FastAPI,
permettant l'exécution de tâches complexes avec des squads spécialisées
(Business, Engineering, Quality Assurance).

Features:
- Exécution de tâches avec orchestration complète
- Workflows prédéfinis (code review, architecture, testing, etc.)
- Streaming en temps réel via Server-Sent Events
- WebSocket support pour la progression
- Quality gates automatiques
- Gestion des agents et squads
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime
from enum import Enum
import asyncio
import json
import logging
import uuid

# Imports du système d'orchestration
# TODO: Adapter ces imports selon la structure finale du module orchestration
try:
    from orchestration.core import BaseAgent, AgentConfig, AgentStatus
    from orchestration.utils.llm_client import LLMClient, ModelType, create_llm_client
    ORCHESTRATION_ENABLED = True
except ImportError:
    logging.warning("Orchestration module not available")
    ORCHESTRATION_ENABLED = False

# Logging setup
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/orchestrate", tags=["orchestration"])


# ============================================================================
# Models / Schemas
# ============================================================================

class TaskPriority(str, Enum):
    """Priorité d'une tâche."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Statut d'exécution d'une tâche."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowType(str, Enum):
    """Types de workflows prédéfinis."""
    CODE_REVIEW = "code_review"
    ARCHITECTURE_DESIGN = "architecture_design"
    FEATURE_DEVELOPMENT = "feature_development"
    BUG_FIX = "bug_fix"
    TESTING = "testing"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    OPTIMIZATION = "optimization"
    CUSTOM = "custom"


class SquadType(str, Enum):
    """Types de squads disponibles."""
    BUSINESS = "business"
    ENGINEERING = "engineering"
    QA = "qa"
    FULL_STACK = "full_stack"


class OrchestrationRequest(BaseModel):
    """Requête pour exécuter une tâche orchestrée."""
    task_description: str = Field(..., description="Description de la tâche à exécuter")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Contexte additionnel (fichiers, requirements, etc.)")
    model: str = Field(default="anthropic/claude-3.5-sonnet", description="Modèle LLM à utiliser")
    api_key: str = Field(..., description="Clé API OpenRouter")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Priorité de la tâche")
    max_iterations: int = Field(default=3, description="Nombre maximum d'itérations")
    enable_quality_gate: bool = Field(default=True, description="Activer le quality gate automatique")
    squad_type: Optional[SquadType] = Field(default=None, description="Type de squad à utiliser (auto-détecté si None)")


class WorkflowExecutionRequest(BaseModel):
    """Requête pour exécuter un workflow prédéfini."""
    workflow_type: WorkflowType = Field(..., description="Type de workflow à exécuter")
    input_data: Dict[str, Any] = Field(..., description="Données d'entrée du workflow")
    model: str = Field(default="anthropic/claude-3.5-sonnet", description="Modèle LLM à utiliser")
    api_key: str = Field(..., description="Clé API OpenRouter")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Priorité du workflow")


class QualityGateRequest(BaseModel):
    """Requête pour exécuter le quality gate."""
    artifacts: List[Dict[str, Any]] = Field(..., description="Artefacts à valider")
    requirements: Dict[str, Any] = Field(..., description="Critères de qualité requis")
    model: str = Field(default="anthropic/claude-3.5-sonnet", description="Modèle LLM pour l'analyse")
    api_key: str = Field(..., description="Clé API OpenRouter")


class TaskResponse(BaseModel):
    """Réponse après création/exécution d'une tâche."""
    task_id: str
    status: TaskStatus
    message: str
    created_at: datetime
    estimated_duration: Optional[int] = None  # en secondes


class TaskStatusResponse(BaseModel):
    """Statut détaillé d'une tâche."""
    task_id: str
    status: TaskStatus
    progress: float = Field(ge=0, le=100, description="Progression en pourcentage")
    current_step: Optional[str] = None
    agents_involved: List[str] = []
    metrics: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class AgentInfo(BaseModel):
    """Informations sur un agent."""
    name: str
    role: str
    squad: str
    capabilities: List[str]
    status: str
    current_task: Optional[str] = None


class SquadInfo(BaseModel):
    """Informations sur une squad."""
    name: str
    type: SquadType
    agents: List[AgentInfo]
    description: str
    workflows_supported: List[WorkflowType]


class WorkflowInfo(BaseModel):
    """Informations sur un workflow."""
    name: str
    type: WorkflowType
    description: str
    required_squads: List[SquadType]
    estimated_duration: int  # en secondes
    steps: List[str]


class QualityGateResult(BaseModel):
    """Résultat d'un quality gate."""
    passed: bool
    score: float = Field(ge=0, le=100, description="Score de qualité global")
    checks: List[Dict[str, Any]]
    recommendations: List[str]
    blockers: List[str] = []
    warnings: List[str] = []
    timestamp: datetime


# ============================================================================
# In-Memory Task Storage (pour demo - à remplacer par DB)
# ============================================================================

tasks_store: Dict[str, Dict[str, Any]] = {}
websocket_connections: Dict[str, List[WebSocket]] = {}


def create_task_id() -> str:
    """Génère un ID unique pour une tâche."""
    return f"task_{uuid.uuid4().hex[:12]}"


def store_task(task_id: str, task_data: Dict[str, Any]):
    """Stocke une tâche dans le store."""
    tasks_store[task_id] = task_data
    logger.info(f"Task stored: {task_id}")


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Récupère une tâche depuis le store."""
    return tasks_store.get(task_id)


def update_task(task_id: str, updates: Dict[str, Any]):
    """Met à jour une tâche."""
    if task_id in tasks_store:
        tasks_store[task_id].update(updates)
        tasks_store[task_id]["updated_at"] = datetime.utcnow()
        logger.debug(f"Task updated: {task_id}")


# ============================================================================
# WebSocket Management
# ============================================================================

async def broadcast_progress(task_id: str, event: Dict[str, Any]):
    """Diffuse un événement de progression à tous les clients connectés."""
    if task_id in websocket_connections:
        disconnected = []
        for ws in websocket_connections[task_id]:
            try:
                await ws.send_json(event)
            except Exception as e:
                logger.warning(f"Failed to send to websocket: {e}")
                disconnected.append(ws)

        # Nettoyage des connexions mortes
        for ws in disconnected:
            websocket_connections[task_id].remove(ws)


# ============================================================================
# Helper Functions
# ============================================================================

def detect_squad_type(task_description: str) -> SquadType:
    """
    Auto-détecte le type de squad nécessaire basé sur la description.

    Args:
        task_description: Description de la tâche

    Returns:
        Type de squad le plus approprié
    """
    description_lower = task_description.lower()

    # Keywords pour chaque squad
    business_keywords = ["product", "feature spec", "requirements", "user story", "business logic"]
    engineering_keywords = ["code", "implement", "develop", "architecture", "api", "database"]
    qa_keywords = ["test", "qa", "quality", "validation", "bug", "regression"]

    # Score pour chaque squad
    scores = {
        SquadType.BUSINESS: sum(1 for kw in business_keywords if kw in description_lower),
        SquadType.ENGINEERING: sum(1 for kw in engineering_keywords if kw in description_lower),
        SquadType.QA: sum(1 for kw in qa_keywords if kw in description_lower),
    }

    # Si multiples squads sont nécessaires, utiliser full_stack
    if sum(1 for score in scores.values() if score > 0) > 1:
        return SquadType.FULL_STACK

    # Sinon prendre le plus haut score
    return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else SquadType.ENGINEERING


async def execute_orchestrated_task(
    task_id: str,
    request: OrchestrationRequest
) -> Dict[str, Any]:
    """
    Exécute une tâche orchestrée avec le système d'agents.

    Cette fonction est le cœur de l'orchestration. Elle:
    1. Détecte ou utilise la squad appropriée
    2. Initialise les agents nécessaires
    3. Exécute la tâche avec progression en temps réel
    4. Applique le quality gate si activé
    5. Retourne les résultats

    Args:
        task_id: ID de la tâche
        request: Requête d'orchestration

    Returns:
        Résultats de l'exécution
    """
    try:
        # Update task status
        update_task(task_id, {
            "status": TaskStatus.RUNNING,
            "progress": 0,
            "current_step": "Initializing orchestration"
        })

        await broadcast_progress(task_id, {
            "event": "task_started",
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Detect squad if not provided
        squad_type = request.squad_type or detect_squad_type(request.task_description)
        logger.info(f"Task {task_id}: Using squad type {squad_type}")

        update_task(task_id, {
            "progress": 10,
            "current_step": f"Initializing {squad_type} squad"
        })

        # TODO: Initialiser le vrai système d'orchestration ici
        # Pour l'instant, simulation
        await asyncio.sleep(1)  # Simulation

        update_task(task_id, {
            "progress": 30,
            "current_step": "Executing task with agents"
        })

        await broadcast_progress(task_id, {
            "event": "agents_working",
            "task_id": task_id,
            "squad": squad_type,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Simulation d'exécution
        for i in range(3):
            await asyncio.sleep(1)
            progress = 30 + (i + 1) * 20
            update_task(task_id, {
                "progress": progress,
                "current_step": f"Iteration {i + 1}/{request.max_iterations}"
            })

            await broadcast_progress(task_id, {
                "event": "progress_update",
                "task_id": task_id,
                "progress": progress,
                "iteration": i + 1,
                "timestamp": datetime.utcnow().isoformat()
            })

        # Quality gate if enabled
        if request.enable_quality_gate:
            update_task(task_id, {
                "progress": 90,
                "current_step": "Running quality gate"
            })

            await broadcast_progress(task_id, {
                "event": "quality_gate_running",
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            await asyncio.sleep(1)  # Simulation

        # Complete task
        result = {
            "success": True,
            "output": {
                "description": request.task_description,
                "squad_used": squad_type,
                "iterations": request.max_iterations,
                "quality_passed": request.enable_quality_gate
            },
            "metrics": {
                "total_time": 5.0,
                "tokens_used": 1500,
                "agents_used": 3
            }
        }

        update_task(task_id, {
            "status": TaskStatus.COMPLETED,
            "progress": 100,
            "current_step": "Completed",
            "result": result,
            "completed_at": datetime.utcnow()
        })

        await broadcast_progress(task_id, {
            "event": "task_completed",
            "task_id": task_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)

        update_task(task_id, {
            "status": TaskStatus.FAILED,
            "error": str(e),
            "completed_at": datetime.utcnow()
        })

        await broadcast_progress(task_id, {
            "event": "task_failed",
            "task_id": task_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })

        raise


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/", response_model=TaskResponse, summary="Exécuter une tâche orchestrée")
async def orchestrate_task(request: OrchestrationRequest):
    """
    Exécute une tâche complexe avec le système d'orchestration multi-agents.

    Cette endpoint:
    1. Crée une nouvelle tâche
    2. Auto-détecte la squad appropriée (Business, Engineering, QA, ou Full-Stack)
    3. Lance l'exécution en arrière-plan
    4. Retourne immédiatement avec un task_id pour suivre la progression

    Utilisez ensuite:
    - GET /api/orchestrate/status/{task_id} pour le statut
    - WebSocket /ws/orchestrate/{task_id} pour la progression en temps réel
    """
    if not ORCHESTRATION_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Orchestration system not available"
        )

    # Create task
    task_id = create_task_id()
    now = datetime.utcnow()

    task_data = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "progress": 0,
        "current_step": "Queued",
        "request": request.dict(),
        "created_at": now,
        "updated_at": now,
        "agents_involved": [],
        "result": None,
        "error": None,
        "completed_at": None
    }

    store_task(task_id, task_data)

    # Launch async execution
    asyncio.create_task(execute_orchestrated_task(task_id, request))

    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="Task queued for orchestration",
        created_at=now,
        estimated_duration=300  # 5 minutes estimate
    )


@router.post("/workflow/{workflow_name}", response_model=TaskResponse, summary="Exécuter un workflow prédéfini")
async def execute_workflow(workflow_name: WorkflowType, request: WorkflowExecutionRequest):
    """
    Exécute un workflow prédéfini (code review, architecture, testing, etc.).

    Workflows disponibles:
    - code_review: Review de code avec feedback détaillé
    - architecture_design: Design d'architecture système
    - feature_development: Développement de feature complète
    - bug_fix: Analyse et fix de bug
    - testing: Génération et exécution de tests
    - refactoring: Refactoring de code
    - documentation: Génération de documentation
    - optimization: Optimisation de performance
    """
    if not ORCHESTRATION_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Orchestration system not available"
        )

    # TODO: Implémenter les workflows réels
    # Pour l'instant, retourne une réponse mockée

    task_id = create_task_id()
    now = datetime.utcnow()

    task_data = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "workflow_type": workflow_name,
        "created_at": now,
        "updated_at": now
    }

    store_task(task_id, task_data)

    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message=f"Workflow '{workflow_name}' queued",
        created_at=now,
        estimated_duration=180
    )


@router.get("/squads", response_model=List[SquadInfo], summary="Lister les squads disponibles")
async def list_squads():
    """
    Liste toutes les squads disponibles avec leurs agents et capacités.

    Squads disponibles:
    - Business Squad: Product Manager, Business Analyst
    - Engineering Squad: Architect, Frontend, Backend, DevOps
    - QA Squad: Tester, Quality Analyst, Security Auditor
    - Full-Stack: Combinaison de toutes les squads
    """
    if not ORCHESTRATION_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Orchestration system not available"
        )

    # Mock data - à remplacer par vraie implémentation
    squads = [
        SquadInfo(
            name="Business Squad",
            type=SquadType.BUSINESS,
            agents=[
                AgentInfo(
                    name="Product Manager",
                    role="product_manager",
                    squad="business",
                    capabilities=["requirements", "user_stories", "prioritization"],
                    status="idle"
                )
            ],
            description="Handles product requirements and business logic",
            workflows_supported=[WorkflowType.FEATURE_DEVELOPMENT]
        ),
        SquadInfo(
            name="Engineering Squad",
            type=SquadType.ENGINEERING,
            agents=[
                AgentInfo(
                    name="Architect",
                    role="architect",
                    squad="engineering",
                    capabilities=["system_design", "architecture", "tech_decisions"],
                    status="idle"
                )
            ],
            description="Handles code development and architecture",
            workflows_supported=[
                WorkflowType.ARCHITECTURE_DESIGN,
                WorkflowType.FEATURE_DEVELOPMENT,
                WorkflowType.REFACTORING
            ]
        ),
        SquadInfo(
            name="QA Squad",
            type=SquadType.QA,
            agents=[
                AgentInfo(
                    name="QA Tester",
                    role="tester",
                    squad="qa",
                    capabilities=["testing", "validation", "quality_assurance"],
                    status="idle"
                )
            ],
            description="Handles testing and quality assurance",
            workflows_supported=[WorkflowType.TESTING, WorkflowType.CODE_REVIEW]
        )
    ]

    return squads


@router.get("/agents", response_model=List[AgentInfo], summary="Lister tous les agents")
async def list_agents():
    """
    Liste tous les agents disponibles dans le système d'orchestration.

    Agents disponibles par squad:
    - Business: Product Manager, Business Analyst
    - Engineering: Architect, Frontend Dev, Backend Dev, DevOps
    - QA: Tester, Quality Analyst, Security Auditor
    """
    if not ORCHESTRATION_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Orchestration system not available"
        )

    # Mock data
    agents = [
        AgentInfo(
            name="Product Manager",
            role="product_manager",
            squad="business",
            capabilities=["requirements", "user_stories", "prioritization"],
            status="idle"
        ),
        AgentInfo(
            name="Architect",
            role="architect",
            squad="engineering",
            capabilities=["system_design", "architecture", "tech_decisions"],
            status="idle"
        ),
        AgentInfo(
            name="QA Tester",
            role="tester",
            squad="qa",
            capabilities=["testing", "validation", "quality_assurance"],
            status="idle"
        )
    ]

    return agents


@router.get("/workflows", response_model=List[WorkflowInfo], summary="Lister les workflows")
async def list_workflows():
    """
    Liste tous les workflows prédéfinis disponibles.

    Chaque workflow combine plusieurs agents et squads pour
    accomplir une tâche complexe de bout en bout.
    """
    if not ORCHESTRATION_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Orchestration system not available"
        )

    workflows = [
        WorkflowInfo(
            name="Code Review",
            type=WorkflowType.CODE_REVIEW,
            description="Complete code review with quality checks",
            required_squads=[SquadType.ENGINEERING, SquadType.QA],
            estimated_duration=120,
            steps=["Static analysis", "Security scan", "Best practices check", "Generate report"]
        ),
        WorkflowInfo(
            name="Architecture Design",
            type=WorkflowType.ARCHITECTURE_DESIGN,
            description="Design system architecture with diagrams",
            required_squads=[SquadType.BUSINESS, SquadType.ENGINEERING],
            estimated_duration=300,
            steps=["Requirements analysis", "Architecture design", "Tech stack selection", "Documentation"]
        ),
        WorkflowInfo(
            name="Feature Development",
            type=WorkflowType.FEATURE_DEVELOPMENT,
            description="Full feature development from spec to deployment",
            required_squads=[SquadType.FULL_STACK],
            estimated_duration=600,
            steps=["Spec review", "Design", "Implementation", "Testing", "Documentation"]
        )
    ]

    return workflows


@router.post("/quality-gate", response_model=QualityGateResult, summary="Exécuter le quality gate")
async def run_quality_gate(request: QualityGateRequest):
    """
    Exécute le quality gate sur des artefacts (code, tests, docs, etc.).

    Le quality gate vérifie:
    - Couverture de tests
    - Standards de code
    - Documentation
    - Sécurité
    - Performance

    Retourne un score et des recommandations.
    """
    if not ORCHESTRATION_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Orchestration system not available"
        )

    # TODO: Implémenter le vrai quality gate
    # Pour l'instant, mock

    return QualityGateResult(
        passed=True,
        score=85.0,
        checks=[
            {"name": "Test Coverage", "passed": True, "score": 90},
            {"name": "Code Quality", "passed": True, "score": 85},
            {"name": "Security", "passed": True, "score": 80},
        ],
        recommendations=[
            "Increase test coverage to 95%",
            "Add more edge case tests",
            "Update documentation"
        ],
        warnings=[
            "Some functions lack type hints"
        ],
        timestamp=datetime.utcnow()
    )


@router.get("/status/{task_id}", response_model=TaskStatusResponse, summary="Statut d'une tâche")
async def get_task_status(task_id: str):
    """
    Récupère le statut détaillé d'une tâche en cours ou terminée.

    Inclut:
    - Statut actuel
    - Progression (0-100%)
    - Étape en cours
    - Agents impliqués
    - Métriques
    - Résultat (si complété)
    - Erreur (si échoué)
    """
    task = get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        progress=task.get("progress", 0),
        current_step=task.get("current_step"),
        agents_involved=task.get("agents_involved", []),
        metrics=task.get("metrics"),
        result=task.get("result"),
        error=task.get("error"),
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        completed_at=task.get("completed_at")
    )


@router.websocket("/ws/{task_id}")
async def websocket_task_progress(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint pour la progression en temps réel d'une tâche.

    Envoi des événements:
    - task_started
    - progress_update (avec progression %)
    - agents_working
    - quality_gate_running
    - task_completed
    - task_failed

    Format JSON:
    {
        "event": "progress_update",
        "task_id": "task_abc123",
        "progress": 45,
        "timestamp": "2025-01-15T10:30:00Z"
    }
    """
    await websocket.accept()

    # Register connection
    if task_id not in websocket_connections:
        websocket_connections[task_id] = []
    websocket_connections[task_id].append(websocket)

    logger.info(f"WebSocket connected for task {task_id}")

    try:
        # Send initial status
        task = get_task(task_id)
        if task:
            await websocket.send_json({
                "event": "connection_established",
                "task_id": task_id,
                "current_status": task.get("status"),
                "progress": task.get("progress", 0),
                "timestamp": datetime.utcnow().isoformat()
            })

        # Keep connection alive and listen for client messages
        while True:
            try:
                data = await websocket.receive_text()
                # Client peut envoyer des commandes (pause, cancel, etc.)
                # TODO: Implémenter les commandes
                logger.debug(f"Received from client: {data}")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break

    finally:
        # Cleanup
        if task_id in websocket_connections:
            websocket_connections[task_id].remove(websocket)
            if not websocket_connections[task_id]:
                del websocket_connections[task_id]

        logger.info(f"WebSocket disconnected for task {task_id}")


@router.get("/stream/{task_id}", summary="Stream SSE de la progression")
async def stream_task_progress(task_id: str):
    """
    Server-Sent Events (SSE) endpoint pour streamer la progression.

    Alternative au WebSocket pour les clients qui préfèrent SSE.

    Format des événements:
    event: progress
    data: {"progress": 45, "step": "Running tests"}

    event: completed
    data: {"success": true, "result": {...}}
    """

    async def event_generator() -> AsyncIterator[str]:
        """Génère les événements SSE."""
        # Check if task exists
        task = get_task(task_id)
        if not task:
            yield f"event: error\ndata: {json.dumps({'error': 'Task not found'})}\n\n"
            return

        # Stream updates while task is running
        last_progress = -1
        while True:
            task = get_task(task_id)
            if not task:
                break

            current_progress = task.get("progress", 0)

            # Send update if progress changed
            if current_progress != last_progress:
                event_data = {
                    "progress": current_progress,
                    "status": task.get("status"),
                    "step": task.get("current_step"),
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"event: progress\ndata: {json.dumps(event_data)}\n\n"
                last_progress = current_progress

            # Check if completed or failed
            if task.get("status") in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                final_data = {
                    "status": task.get("status"),
                    "result": task.get("result"),
                    "error": task.get("error"),
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"event: completed\ndata: {json.dumps(final_data)}\n\n"
                break

            await asyncio.sleep(1)  # Poll every second

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/health", summary="Health check de l'orchestration")
async def orchestration_health():
    """
    Health check pour vérifier que le système d'orchestration est opérationnel.

    Retourne:
    - Status: healthy/degraded/unhealthy
    - Nombre de tâches actives
    - Squads disponibles
    - Agents disponibles
    """
    return {
        "status": "healthy" if ORCHESTRATION_ENABLED else "unhealthy",
        "orchestration_enabled": ORCHESTRATION_ENABLED,
        "active_tasks": len([t for t in tasks_store.values() if t.get("status") == TaskStatus.RUNNING]),
        "total_tasks": len(tasks_store),
        "websocket_connections": sum(len(conns) for conns in websocket_connections.values()),
        "timestamp": datetime.utcnow().isoformat()
    }
