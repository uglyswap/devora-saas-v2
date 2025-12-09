"""
DEVORA Deployment Routes - One-Click Deploy API with SSE Streaming
@version 2.0.0

Features:
- Deploy to Vercel, Netlify, Railway
- Real-time progress via SSE
- Environment variables management
- Deployment history
- Rollback support
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import uuid
import json
import logging
import asyncio
from datetime import datetime, timezone
from enum import Enum

from services.deploy_service import (
    deploy_service,
    DeploymentFile,
    DeploymentResult,
    DeployProvider,
    DeploymentStatus,
    DeploymentProgress
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/deploy", tags=["deployment"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class FileContent(BaseModel):
    """File to deploy"""
    name: str
    content: str
    language: Optional[str] = "plaintext"


class QuickDeployRequest(BaseModel):
    """Request for one-click deployment"""
    project_id: Optional[str] = None
    project_name: str
    files: List[FileContent]
    provider: str = "vercel"  # vercel, netlify, railway
    env_vars: Optional[Dict[str, str]] = None
    framework: Optional[str] = None  # Auto-detect if not provided


class DeploymentStatusResponse(BaseModel):
    """Deployment status response"""
    id: str
    success: bool = True
    status: str
    url: Optional[str] = None
    error: Optional[str] = None
    progress: int = 0
    provider: str = "vercel"
    deployment_id: Optional[str] = None
    created_at: Optional[str] = None
    logs: List[str] = []


class DeploymentHistoryItem(BaseModel):
    """Deployment history item"""
    id: str
    project_name: str
    provider: str
    status: str
    url: Optional[str] = None
    created_at: str


class ProviderInfo(BaseModel):
    """Provider information"""
    id: str
    name: str
    available: bool
    requires_token: bool
    features: List[str]


# In-memory storage for deployments (use database in production)
deployments_store: Dict[str, Dict] = {}


# =============================================================================
# DEPLOYMENT ENDPOINTS
# =============================================================================

@router.post("/quick", response_model=DeploymentStatusResponse)
async def quick_deploy(request: QuickDeployRequest, background_tasks: BackgroundTasks):
    """
    One-click deployment to Vercel, Netlify, or Railway

    - Automatically detects framework
    - Supports environment variables
    - Returns deployment URL when ready
    """
    deployment_id = str(uuid.uuid4())

    try:
        # Get token from settings or environment
        from config import get_db
        db = get_db()
        settings = await db.settings.find_one({}) or {}

        provider = DeployProvider(request.provider)
        token = None

        if provider == DeployProvider.VERCEL:
            token = settings.get("vercel_token") or os.getenv("VERCEL_TOKEN")
        elif provider == DeployProvider.NETLIFY:
            token = settings.get("netlify_token") or os.getenv("NETLIFY_TOKEN")
        elif provider == DeployProvider.RAILWAY:
            token = settings.get("railway_token") or os.getenv("RAILWAY_TOKEN")

        if not token:
            return DeploymentStatusResponse(
                id=deployment_id,
                success=False,
                status="error",
                error=f"No {request.provider} token configured. Please add it in settings.",
                progress=0,
                provider=request.provider
            )

        # Convert files
        deployment_files = [
            DeploymentFile(name=f.name, content=f.content)
            for f in request.files
        ]

        # Deploy
        result = await deploy_service.quick_deploy(
            files=deployment_files,
            project_name=request.project_name,
            provider=provider,
            token=token,
            env_vars=request.env_vars
        )

        # Store deployment info
        deployments_store[deployment_id] = {
            "id": deployment_id,
            "project_name": request.project_name,
            "provider": request.provider,
            "status": result.status.value,
            "url": result.url,
            "error": result.error,
            "deployment_id": result.deployment_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "logs": result.build_logs
        }

        return DeploymentStatusResponse(
            id=deployment_id,
            success=result.success,
            status=result.status.value,
            url=result.url,
            error=result.error,
            progress=100 if result.success else 0,
            provider=request.provider,
            deployment_id=result.deployment_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            logs=result.build_logs
        )

    except Exception as e:
        logger.exception(f"[Deploy] Error: {e}")
        return DeploymentStatusResponse(
            id=deployment_id,
            success=False,
            status="error",
            error=str(e),
            progress=0,
            provider=request.provider
        )


@router.post("/stream")
async def deploy_with_stream(request: QuickDeployRequest):
    """
    Deploy with real-time SSE progress updates

    Events:
    - start: Deployment initiated
    - progress: Progress update (0-100%)
    - log: Build log message
    - complete: Deployment successful
    - error: Deployment failed
    """
    try:
        # Get token
        from config import get_db
        db = get_db()
        settings = await db.settings.find_one({}) or {}

        provider = DeployProvider(request.provider)
        token = None

        if provider == DeployProvider.VERCEL:
            token = settings.get("vercel_token") or os.getenv("VERCEL_TOKEN")
        elif provider == DeployProvider.NETLIFY:
            token = settings.get("netlify_token") or os.getenv("NETLIFY_TOKEN")
        elif provider == DeployProvider.RAILWAY:
            token = settings.get("railway_token") or os.getenv("RAILWAY_TOKEN")

        if not token:
            async def error_stream():
                yield f"event: error\ndata: {json.dumps({'error': f'No {request.provider} token configured'})}\n\n"

            return StreamingResponse(
                error_stream(),
                media_type="text/event-stream"
            )

        # Convert files
        deployment_files = [
            DeploymentFile(name=f.name, content=f.content)
            for f in request.files
        ]

        # Return SSE stream
        return StreamingResponse(
            deploy_service.deploy_with_stream(
                files=deployment_files,
                project_name=request.project_name,
                provider=provider,
                token=token,
                env_vars=request.env_vars
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.exception(f"[Deploy] Stream error: {e}")

        async def error_stream():
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream"
        )


@router.get("/status/{deployment_id}", response_model=DeploymentStatusResponse)
async def get_deployment_status(deployment_id: str):
    """Get deployment status by ID"""
    if deployment_id not in deployments_store:
        raise HTTPException(status_code=404, detail="Deployment not found")

    data = deployments_store[deployment_id]

    return DeploymentStatusResponse(
        id=deployment_id,
        success=data.get("status") == "ready",
        status=data.get("status", "unknown"),
        url=data.get("url"),
        error=data.get("error"),
        progress=100 if data.get("status") == "ready" else 50,
        provider=data.get("provider", "vercel"),
        deployment_id=data.get("deployment_id"),
        created_at=data.get("created_at"),
        logs=data.get("logs", [])
    )


@router.get("/history", response_model=List[DeploymentHistoryItem])
async def get_deployment_history(limit: int = 50):
    """Get deployment history"""
    deployments = list(deployments_store.values())
    deployments.sort(key=lambda d: d.get("created_at", ""), reverse=True)

    return [
        DeploymentHistoryItem(
            id=d["id"],
            project_name=d.get("project_name", "Unknown"),
            provider=d.get("provider", "vercel"),
            status=d.get("status", "unknown"),
            url=d.get("url"),
            created_at=d.get("created_at", "")
        )
        for d in deployments[:limit]
    ]


@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers():
    """List available deployment providers"""
    # Check which providers have tokens configured
    from config import get_db
    db = get_db()
    settings = await db.settings.find_one({}) or {}

    vercel_available = bool(
        settings.get("vercel_token") or os.getenv("VERCEL_TOKEN")
    )
    netlify_available = bool(
        settings.get("netlify_token") or os.getenv("NETLIFY_TOKEN")
    )
    railway_available = bool(
        settings.get("railway_token") or os.getenv("RAILWAY_TOKEN")
    )

    return [
        ProviderInfo(
            id="vercel",
            name="Vercel",
            available=vercel_available,
            requires_token=True,
            features=[
                "Serverless Functions",
                "Edge Network",
                "Preview Deployments",
                "Custom Domains",
                "Environment Variables",
                "Analytics"
            ]
        ),
        ProviderInfo(
            id="netlify",
            name="Netlify",
            available=netlify_available,
            requires_token=True,
            features=[
                "Serverless Functions",
                "Forms",
                "Identity",
                "Large Media",
                "Split Testing",
                "Deploy Previews"
            ]
        ),
        ProviderInfo(
            id="railway",
            name="Railway",
            available=railway_available,
            requires_token=True,
            features=[
                "Databases",
                "Background Workers",
                "Cron Jobs",
                "Auto-scaling",
                "GitHub Integration"
            ]
        )
    ]


@router.delete("/{deployment_id}")
async def cancel_deployment(deployment_id: str):
    """Cancel a running deployment"""
    if deployment_id not in deployments_store:
        raise HTTPException(status_code=404, detail="Deployment not found")

    deployments_store[deployment_id]["status"] = "canceled"

    return {"success": True, "message": "Deployment cancelled"}


# =============================================================================
# CONFIGURATION ENDPOINTS
# =============================================================================

class ProviderTokenRequest(BaseModel):
    """Request to save provider token"""
    provider: str
    token: str


@router.post("/config/token")
async def save_provider_token(request: ProviderTokenRequest):
    """Save provider API token"""
    try:
        from config import get_db
        db = get_db()

        token_key = f"{request.provider}_token"

        await db.settings.update_one(
            {},
            {"$set": {token_key: request.token}},
            upsert=True
        )

        return {"success": True, "message": f"{request.provider} token saved"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/tokens")
async def get_configured_tokens():
    """Get list of configured provider tokens (masked)"""
    try:
        from config import get_db
        db = get_db()
        settings = await db.settings.find_one({}) or {}

        def mask_token(token: Optional[str]) -> Optional[str]:
            if not token:
                return None
            if len(token) <= 8:
                return "****"
            return f"{token[:4]}...{token[-4:]}"

        return {
            "vercel": mask_token(settings.get("vercel_token")),
            "netlify": mask_token(settings.get("netlify_token")),
            "railway": mask_token(settings.get("railway_token"))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# DEMO ENDPOINT
# =============================================================================

@router.get("/demo")
async def demo_deploy():
    """Demo deployment for testing"""
    return DeploymentStatusResponse(
        id=str(uuid.uuid4()),
        success=True,
        status="ready",
        url=f"https://demo-{uuid.uuid4().hex[:8]}.vercel.app",
        progress=100,
        provider="vercel",
        deployment_id=f"dpl_{uuid.uuid4().hex[:12]}",
        created_at=datetime.now(timezone.utc).isoformat()
    )
