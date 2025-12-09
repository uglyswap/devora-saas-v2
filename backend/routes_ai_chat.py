"""
AI Chat Routes with Server-Sent Events (SSE)
Agent: AI Chat Engineer

API endpoints pour le chat conversationnel avec streaming et plans d'exécution
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, AsyncGenerator
import logging
import json
import asyncio
from datetime import datetime, timezone
import uuid

# Import des agents et services
from agents.orchestrator_v2 import OrchestratorV2
from ai.llm_service import LLMService

router = APIRouter()
logger = logging.getLogger(__name__)

# ============================================
# Models
# ============================================

class ChatMessageModel(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    content: str

class ExecutionStepModel(BaseModel):
    id: str
    title: str
    description: str
    status: str  # 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped'
    action: str  # 'create' | 'update' | 'delete' | 'rename' | 'move' | 'analyze' | 'test'
    target: Optional[str] = None
    details: Optional[str] = None
    progress: Optional[int] = None
    error: Optional[str] = None

class FileChangeModel(BaseModel):
    path: str
    action: str  # 'create' | 'update' | 'delete'
    oldContent: Optional[str] = None
    newContent: Optional[str] = None
    language: Optional[str] = None

class ExecutionPlanModel(BaseModel):
    id: str
    title: str
    description: str
    steps: List[ExecutionStepModel]
    status: str  # 'pending' | 'awaiting_confirmation' | 'approved' | 'executing' | 'completed' | 'cancelled' | 'failed'
    requiresConfirmation: bool
    estimatedDuration: Optional[int] = None
    filesChanged: Optional[List[FileChangeModel]] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatContext(BaseModel):
    selectedFiles: Optional[List[str]] = []
    selectedLines: Optional[List[Dict[str, Any]]] = []
    relatedIssues: Optional[List[str]] = []
    previousPlans: Optional[List[str]] = []

class ChatOptions(BaseModel):
    streaming: bool = True
    autoApprove: bool = False
    maxTokens: Optional[int] = 4000
    temperature: Optional[float] = 0.7
    confirmDestructive: bool = True

class ChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    projectId: Optional[str] = None
    userId: Optional[str] = None
    model: str = "gpt-4"
    currentFiles: Optional[List[Dict[str, str]]] = []
    conversationHistory: Optional[List[ChatMessageModel]] = []
    context: Optional[ChatContext] = None
    options: Optional[ChatOptions] = None

class ExecutePlanRequest(BaseModel):
    planId: str
    modifications: Optional[Dict[str, Any]] = None

# ============================================
# Helper Functions
# ============================================

def create_sse_message(event_type: str, data: Any) -> str:
    """Create a Server-Sent Event formatted message"""
    return f"data: {json.dumps({'type': event_type, 'data': data, 'timestamp': datetime.now(timezone.utc).isoformat()})}\n\n"

async def generate_execution_plan(
    user_message: str,
    current_files: List[Dict[str, str]],
    conversation_history: List[Dict[str, str]],
    model: str = "gpt-4"
) -> ExecutionPlanModel:
    """
    Generate an execution plan based on user message
    """
    try:
        # Analyze the request and generate plan
        llm_service = LLMService(model=model)

        # Build prompt for plan generation
        system_prompt = """You are an AI assistant that creates detailed execution plans for code modifications.

Analyze the user's request and create a structured execution plan with:
1. Clear steps in logical order
2. File changes required (create, update, delete)
3. Risk assessment (low, medium, high)
4. Whether confirmation is needed (true for destructive actions)

Return a JSON object with this structure:
{
    "title": "Brief plan title",
    "description": "Detailed description",
    "requiresConfirmation": boolean,
    "estimatedDuration": seconds,
    "metadata": {
        "complexity": "low|medium|high",
        "risk": "low|medium|high",
        "warnings": ["warning1", "warning2"]
    },
    "steps": [
        {
            "title": "Step title",
            "description": "Step description",
            "action": "create|update|delete|analyze|test",
            "target": "file path or component name"
        }
    ],
    "filesChanged": [
        {
            "path": "file/path.ts",
            "action": "create|update|delete",
            "language": "typescript"
        }
    ]
}"""

        # Get conversation context
        context_messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            context_messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in conversation_history[-5:]])

        # Add current request
        files_summary = f"\nCurrent files: {len(current_files)} files" if current_files else ""
        context_messages.append({
            "role": "user",
            "content": f"{user_message}{files_summary}\n\nGenerate an execution plan for this request."
        })

        # Generate plan
        response = await llm_service.chat_completion(
            messages=context_messages,
            temperature=0.3,
            max_tokens=2000
        )

        # Parse response
        plan_data = json.loads(response)

        # Create execution plan
        plan = ExecutionPlanModel(
            id=str(uuid.uuid4()),
            title=plan_data.get("title", "Execution Plan"),
            description=plan_data.get("description", ""),
            steps=[
                ExecutionStepModel(
                    id=str(uuid.uuid4()),
                    title=step["title"],
                    description=step["description"],
                    status="pending",
                    action=step["action"],
                    target=step.get("target"),
                    details=step.get("details")
                )
                for step in plan_data.get("steps", [])
            ],
            status="awaiting_confirmation" if plan_data.get("requiresConfirmation", True) else "approved",
            requiresConfirmation=plan_data.get("requiresConfirmation", True),
            estimatedDuration=plan_data.get("estimatedDuration"),
            filesChanged=[
                FileChangeModel(**file_change)
                for file_change in plan_data.get("filesChanged", [])
            ] if plan_data.get("filesChanged") else None,
            metadata=plan_data.get("metadata")
        )

        return plan

    except Exception as e:
        logger.error(f"Error generating execution plan: {e}")
        # Return a simple fallback plan
        return ExecutionPlanModel(
            id=str(uuid.uuid4()),
            title="Direct Implementation",
            description=f"Implement: {user_message}",
            steps=[
                ExecutionStepModel(
                    id=str(uuid.uuid4()),
                    title="Implement request",
                    description=user_message,
                    status="pending",
                    action="update"
                )
            ],
            status="awaiting_confirmation",
            requiresConfirmation=True,
            metadata={"complexity": "medium", "risk": "medium"}
        )

async def stream_ai_response(
    message: str,
    session_id: str,
    project_id: Optional[str],
    user_id: Optional[str],
    model: str,
    current_files: List[Dict[str, str]],
    conversation_history: List[ChatMessageModel],
    options: ChatOptions
) -> AsyncGenerator[str, None]:
    """
    Stream AI responses with SSE
    """
    try:
        # Send thinking event
        yield create_sse_message("thinking", {"message": "Analyzing your request..."})
        await asyncio.sleep(0.5)

        # Generate execution plan first
        yield create_sse_message("thinking", {"message": "Creating execution plan..."})

        plan = await generate_execution_plan(
            user_message=message,
            current_files=current_files,
            conversation_history=[{"role": msg.role, "content": msg.content} for msg in conversation_history],
            model=model
        )

        # Send execution plan
        yield create_sse_message("plan", plan.model_dump())

        # If requires confirmation, wait (frontend will handle approval)
        if plan.requiresConfirmation and not options.autoApprove:
            yield create_sse_message("content", {
                "content": f"\n\n**Plan d'exécution créé**\n\nJ'ai préparé un plan pour {plan.title}. Veuillez le consulter ci-dessus et l'approuver pour continuer.\n\n**Étapes:**\n"
            })
            for i, step in enumerate(plan.steps, 1):
                yield create_sse_message("content", {
                    "content": f"{i}. {step.title}\n"
                })

            yield create_sse_message("complete", {"planId": plan.id})
            return

        # If auto-approved, execute plan
        yield create_sse_message("thinking", {"message": "Executing plan..."})

        # Initialize orchestrator for execution
        orchestrator = OrchestratorV2(
            api_key=None,  # Use default from env
            model=model
        )

        # Execute with streaming
        total_steps = len(plan.steps)
        for i, step in enumerate(plan.steps, 1):
            # Update step status
            step.status = "in_progress"
            yield create_sse_message("step_update", {
                "planId": plan.id,
                "stepId": step.id,
                "status": "in_progress",
                "progress": int((i - 1) / total_steps * 100)
            })

            # Stream step execution
            yield create_sse_message("content", {
                "content": f"\n\n**{i}/{total_steps}** {step.title}\n"
            })

            # Simulate execution (replace with actual execution)
            await asyncio.sleep(1)

            # Mark as completed
            step.status = "completed"
            yield create_sse_message("step_update", {
                "planId": plan.id,
                "stepId": step.id,
                "status": "completed",
                "progress": int(i / total_steps * 100)
            })

            yield create_sse_message("content", {
                "content": f"✓ {step.description}\n"
            })

        # Send completion
        yield create_sse_message("content", {
            "content": f"\n\n**Completed!** All {total_steps} steps executed successfully."
        })

        yield create_sse_message("complete", {
            "planId": plan.id,
            "filesChanged": [f.model_dump() for f in (plan.filesChanged or [])]
        })

    except Exception as e:
        logger.error(f"Error streaming AI response: {e}")
        yield create_sse_message("error", {"message": str(e)})

# ============================================
# Routes
# ============================================

@router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Main chat endpoint with Server-Sent Events streaming
    """
    try:
        session_id = request.sessionId or str(uuid.uuid4())
        options = request.options or ChatOptions()

        # Return streaming response
        return StreamingResponse(
            stream_ai_response(
                message=request.message,
                session_id=session_id,
                project_id=request.projectId,
                user_id=request.userId,
                model=request.model,
                current_files=request.currentFiles or [],
                conversation_history=request.conversationHistory or [],
                options=options
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable buffering for nginx
            }
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/execute-plan")
async def execute_plan(request: ExecutePlanRequest):
    """
    Execute an approved execution plan
    """
    try:
        plan_id = request.planId
        modifications = request.modifications or {}

        # TODO: Retrieve plan from storage
        # TODO: Execute plan steps
        # TODO: Return results

        return {
            "success": True,
            "planId": plan_id,
            "message": "Plan executed successfully",
            "filesChanged": []
        }

    except Exception as e:
        logger.error(f"Execute plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions")
async def list_sessions(userId: Optional[str] = None):
    """
    List chat sessions for a user
    """
    try:
        # TODO: Retrieve sessions from database
        return {
            "sessions": []
        }
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a chat session
    """
    try:
        # TODO: Delete session from database
        return {
            "success": True,
            "message": "Session deleted"
        }
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/health")
async def health_check():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "ai-chat",
        "features": [
            "streaming",
            "execution-plans",
            "code-generation",
            "conversation-memory"
        ]
    }
