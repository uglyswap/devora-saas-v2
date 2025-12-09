from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, AsyncGenerator
import json
import asyncio
import logging

from auth import get_current_user
from agents.orchestrator_v2 import OrchestratorV2

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/stream', tags=['streaming'])

class StreamGenerateRequest(BaseModel):
    message: str
    model: str = "openai/gpt-4o"
    api_key: str
    current_files: List[Dict] = []
    project_id: Optional[str] = None

async def generate_stream(
    request: StreamGenerateRequest,
    user_id: str
) -> AsyncGenerator[str, None]:
    """Générateur de stream SSE"""

    try:
        # Progress: Démarrage
        yield f"data: {json.dumps({'type': 'progress', 'step': 'Initialisation...', 'progress': 5})}\n\n"
        await asyncio.sleep(0.1)

        # Initialiser l'orchestrator
        orchestrator = OrchestratorV2(
            api_key=request.api_key,
            model=request.model
        )

        yield f"data: {json.dumps({'type': 'progress', 'step': 'Analyse de la demande...', 'progress': 15})}\n\n"

        # Phase 1: Architecture
        yield f"data: {json.dumps({'type': 'progress', 'step': 'Agent Architecte en action...', 'progress': 25})}\n\n"

        # Appeler l'orchestrator
        result = await orchestrator.process(
            message=request.message,
            current_files=request.current_files,
            model=request.model,
            user_id=user_id,
            project_id=request.project_id
        )

        yield f"data: {json.dumps({'type': 'progress', 'step': 'Génération du code...', 'progress': 60})}\n\n"

        # Envoyer chaque fichier
        for i, file in enumerate(result.get("files", [])):
            progress = 60 + (i + 1) * (30 / max(len(result.get("files", [])), 1))
            yield f"data: {json.dumps({'type': 'file', 'file': file, 'progress': int(progress)})}\n\n"
            await asyncio.sleep(0.05)  # Petit délai pour UX

        # Terminé
        yield f"data: {json.dumps({'type': 'done', 'success': True, 'message': result.get('message', 'Génération terminée'), 'files_count': len(result.get('files', []))})}\n\n"

    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.post("/generate")
async def stream_generate(
    request: StreamGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Endpoint de génération avec streaming SSE"""

    return StreamingResponse(
        generate_stream(request, current_user["user_id"]),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
