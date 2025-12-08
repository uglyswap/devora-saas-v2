from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import json
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/deploy", tags=["deploy"])

VERCEL_SYSTEM_TOKEN = os.getenv("VERCEL_SYSTEM_TOKEN")
deployments: Dict[str, dict] = {}

class FileContent(BaseModel):
    name: str
    content: str
    language: Optional[str] = "plaintext"

class DeployRequest(BaseModel):
    project_name: str
    files: List[FileContent]
    provider: str = "vercel"

class DeploymentStatus(BaseModel):
    id: str
    status: str
    url: Optional[str] = None
    error: Optional[str] = None
    progress: int = 0

@router.post("/quick", response_model=DeploymentStatus)
async def quick_deploy(request: DeployRequest, background_tasks: BackgroundTasks):
    deployment_id = str(uuid.uuid4())
    safe_name = request.project_name.lower()
    safe_name = "".join(c if c.isalnum() or c == "-" else "-" for c in safe_name)[:40]
    
    deployments[deployment_id] = {
        "id": deployment_id,
        "status": "pending",
        "url": None,
        "error": None,
        "progress": 0
    }
    
    # Simulate quick deploy
    deployments[deployment_id]["status"] = "ready"
    deployments[deployment_id]["url"] = f"https://{safe_name}.vercel.app"
    deployments[deployment_id]["progress"] = 100
    
    return DeploymentStatus(**deployments[deployment_id])

@router.get("/status/{deployment_id}", response_model=DeploymentStatus)
async def get_deployment_status(deployment_id: str):
    if deployment_id not in deployments:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return DeploymentStatus(**deployments[deployment_id])

@router.get("/demo")
async def demo_deploy():
    return {
        "id": str(uuid.uuid4()),
        "status": "ready",
        "url": f"https://demo-{uuid.uuid4().hex[:8]}.vercel.app",
        "progress": 100
    }
