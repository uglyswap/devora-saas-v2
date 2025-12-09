"""DEVORA DEPLOY SERVICE - Ultimate 1-Click Deployment @version 5.0.0"""

import os
import json
import asyncio
import logging
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class DeployProvider(str, Enum):
    VERCEL = "vercel"
    NETLIFY = "netlify"
    RAILWAY = "railway"

class DeploymentStatus(str, Enum):
    QUEUED = "queued"
    BUILDING = "building"
    DEPLOYING = "deploying"
    READY = "ready"
    ERROR = "error"
    CANCELED = "canceled"

class DeploymentFile(BaseModel):
    name: str
    content: str
    encoding: str = "utf-8"

class DeploymentResult(BaseModel):
    success: bool
    deployment_id: Optional[str] = None
    url: Optional[str] = None
    status: DeploymentStatus = DeploymentStatus.QUEUED
    provider: DeployProvider = DeployProvider.VERCEL
    build_logs: List[str] = []
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ready_at: Optional[datetime] = None

class DeploymentProgress(BaseModel):
    stage: str
    progress: int
    message: str
    logs: List[str] = []

class DeployService:
    VERCEL_API = "https://api.vercel.com"
    NETLIFY_API = "https://api.netlify.com/api/v1"

    def __init__(self):
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=120.0)
        return self._http_client

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()

    async def deploy_to_vercel(self, files: List[DeploymentFile], project_name: str, vercel_token: str, team_id: Optional[str] = None, env_vars: Optional[Dict[str, str]] = None, framework: str = "nextjs", on_progress: Optional[callable] = None) -> DeploymentResult:
        try:
            client = await self._get_client()
            if on_progress: await on_progress(DeploymentProgress(stage="preparing", progress=10, message="Préparation des fichiers..."))
            vercel_files = []
            for file in files:
                file_path = file.name if file.name.startswith('/') else '/' + file.name
                vercel_files.append({"file": file_path, "data": file.content, "encoding": file.encoding})
            has_vercel_config = any(f["file"] in ["/vercel.json", "vercel.json"] for f in vercel_files)
            if not has_vercel_config:
                vercel_config = self._generate_vercel_config(framework)
                vercel_files.append({"file": "/vercel.json", "data": json.dumps(vercel_config, indent=2), "encoding": "utf-8"})
            if on_progress: await on_progress(DeploymentProgress(stage="uploading", progress=30, message="Upload des fichiers vers Vercel..."))
            headers = {"Authorization": f"Bearer {vercel_token}", "Content-Type": "application/json"}
            deploy_payload = {"name": project_name, "files": vercel_files, "projectSettings": {"framework": framework if framework != "static" else None, "buildCommand": self._get_build_command(framework), "outputDirectory": self._get_output_directory(framework), "installCommand": "npm install" if framework != "static" else None}, "target": "production"}
            if env_vars: deploy_payload["env"] = env_vars
            params = {"teamId": team_id} if team_id else {}
            response = await client.post(f"{self.VERCEL_API}/v13/deployments", headers=headers, json=deploy_payload, params=params)
            if response.status_code not in [200, 201]:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", response.text)
                return DeploymentResult(success=False, provider=DeployProvider.VERCEL, status=DeploymentStatus.ERROR, error=error_msg)
            data = response.json()
            deployment_id = data.get("id")
            deployment_url = data.get("url")
            if on_progress: await on_progress(DeploymentProgress(stage="building", progress=50, message="Build en cours..."))
            final_url = await self._wait_for_vercel_deployment(deployment_id, vercel_token, team_id, on_progress)
            return DeploymentResult(success=True, deployment_id=deployment_id, url=f"https://{final_url or deployment_url}", status=DeploymentStatus.READY, provider=DeployProvider.VERCEL, ready_at=datetime.utcnow())
        except Exception as e:
            logger.error(f"[Deploy] Vercel deployment failed: {e}")
            return DeploymentResult(success=False, provider=DeployProvider.VERCEL, status=DeploymentStatus.ERROR, error=str(e))

    async def _wait_for_vercel_deployment(self, deployment_id: str, token: str, team_id: Optional[str], on_progress: Optional[callable] = None, max_wait: int = 180, poll_interval: int = 3) -> Optional[str]:
        client = await self._get_client()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"teamId": team_id} if team_id else {}
        elapsed = 0
        last_state = None
        while elapsed < max_wait:
            try:
                response = await client.get(f"{self.VERCEL_API}/v13/deployments/{deployment_id}", headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    state = data.get("readyState", data.get("state"))
                    url = data.get("url")
                    if state != last_state:
                        last_state = state
                        progress = {"QUEUED": 40, "BUILDING": 60, "INITIALIZING": 70, "READY": 100, "ERROR": 100, "CANCELED": 100}.get(state, 50)
                        if on_progress: await on_progress(DeploymentProgress(stage=state.lower(), progress=progress, message=f"État: {state}"))
                    if state == "READY": return url
                    elif state in ["ERROR", "CANCELED"]: raise Exception(f"Deployment {state}")
            except httpx.RequestError as e:
                logger.warning(f"[Deploy] Polling error: {e}")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        raise Exception("Deployment timeout")

    def _generate_vercel_config(self, framework: str) -> Dict[str, Any]:
        config = {"headers": [{"source": "/(.*)", "headers": [{"key": "X-Frame-Options", "value": "ALLOWALL"}, {"key": "Content-Security-Policy", "value": "frame-ancestors *"}, {"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]}]}
        if framework == "static": config["rewrites"] = [{"source": "/(.*)", "destination": "/index.html"}]
        return config

    def _get_build_command(self, framework: str) -> Optional[str]:
        return {"nextjs": "npm run build", "react": "npm run build", "vite": "npm run build", "static": None}.get(framework)

    def _get_output_directory(self, framework: str) -> Optional[str]:
        return {"nextjs": ".next", "react": "build", "vite": "dist", "static": "."}.get(framework)

    async def deploy_to_netlify(self, files: List[DeploymentFile], site_name: str, netlify_token: str, on_progress: Optional[callable] = None) -> DeploymentResult:
        try:
            client = await self._get_client()
            if on_progress: await on_progress(DeploymentProgress(stage="preparing", progress=10, message="Préparation du déploiement Netlify..."))
            headers = {"Authorization": f"Bearer {netlify_token}", "Content-Type": "application/json"}
            site_response = await client.post(f"{self.NETLIFY_API}/sites", headers=headers, json={"name": site_name})
            if site_response.status_code == 422:
                sites_response = await client.get(f"{self.NETLIFY_API}/sites", headers=headers, params={"name": site_name})
                sites = sites_response.json()
                site = next((s for s in sites if s.get("name") == site_name), None)
                if not site: raise Exception("Site not found and cannot create")
                site_id = site["id"]
            elif site_response.status_code in [200, 201]:
                site = site_response.json()
                site_id = site["id"]
            else: raise Exception(f"Failed to create site: {site_response.text}")
            if on_progress: await on_progress(DeploymentProgress(stage="uploading", progress=40, message="Upload des fichiers..."))
            import hashlib
            file_hashes = {}
            file_contents = {}
            for file in files:
                file_path = file.name[1:] if file.name.startswith('/') else file.name
                content_bytes = file.content.encode(file.encoding)
                file_hash = hashlib.sha1(content_bytes).hexdigest()
                file_hashes[f"/{file_path}"] = file_hash
                file_contents[file_hash] = content_bytes
            deploy_response = await client.post(f"{self.NETLIFY_API}/sites/{site_id}/deploys", headers=headers, json={"files": file_hashes, "draft": False})
            if deploy_response.status_code not in [200, 201]: raise Exception(f"Failed to create deployment: {deploy_response.text}")
            deploy_data = deploy_response.json()
            deploy_id = deploy_data["id"]
            required_files = deploy_data.get("required", [])
            if on_progress: await on_progress(DeploymentProgress(stage="uploading", progress=60, message=f"Upload de {len(required_files)} fichiers..."))
            for file_hash in required_files:
                if file_hash in file_contents:
                    await client.put(f"{self.NETLIFY_API}/deploys/{deploy_id}/files/{file_hash}", headers={"Authorization": f"Bearer {netlify_token}", "Content-Type": "application/octet-stream"}, content=file_contents[file_hash])
            if on_progress: await on_progress(DeploymentProgress(stage="ready", progress=100, message="Déploiement terminé!"))
            final_response = await client.get(f"{self.NETLIFY_API}/deploys/{deploy_id}", headers=headers)
            final_data = final_response.json()
            deploy_url = final_data.get("ssl_url") or final_data.get("url")
            return DeploymentResult(success=True, deployment_id=deploy_id, url=deploy_url, status=DeploymentStatus.READY, provider=DeployProvider.NETLIFY, ready_at=datetime.utcnow())
        except Exception as e:
            logger.error(f"[Deploy] Netlify deployment failed: {e}")
            return DeploymentResult(success=False, provider=DeployProvider.NETLIFY, status=DeploymentStatus.ERROR, error=str(e))

    async def quick_deploy(self, files: List[DeploymentFile], project_name: str, provider: DeployProvider = DeployProvider.VERCEL, token: str = None, env_vars: Optional[Dict[str, str]] = None, on_progress: Optional[callable] = None) -> DeploymentResult:
        clean_name = "".join(c if c.isalnum() or c == "-" else "-" for c in project_name.lower())[:50]
        framework = self._detect_framework(files)
        if provider == DeployProvider.VERCEL:
            return await self.deploy_to_vercel(files=files, project_name=clean_name, vercel_token=token, env_vars=env_vars, framework=framework, on_progress=on_progress)
        elif provider == DeployProvider.NETLIFY:
            return await self.deploy_to_netlify(files=files, site_name=clean_name, netlify_token=token, on_progress=on_progress)
        else:
            return DeploymentResult(success=False, provider=provider, status=DeploymentStatus.ERROR, error=f"Provider {provider} not yet implemented")

    def _detect_framework(self, files: List[DeploymentFile]) -> str:
        file_names = [f.name.lower() for f in files]
        pkg_file = next((f for f in files if f.name.lower() == 'package.json'), None)
        if pkg_file:
            try:
                pkg = json.loads(pkg_file.content)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                if 'next' in deps: return 'nextjs'
                if 'vite' in deps: return 'vite'
                if 'react' in deps: return 'react'
                if 'vue' in deps: return 'vue'
            except json.JSONDecodeError: pass
        if 'next.config.js' in file_names or 'next.config.ts' in file_names: return 'nextjs'
        if 'vite.config.js' in file_names or 'vite.config.ts' in file_names: return 'vite'
        if any(f.endswith('.tsx') for f in file_names): return 'react'
        return 'static'

deploy_service = DeployService()

async def quick_deploy(files: List[Dict[str, str]], project_name: str, token: str, provider: str = "vercel") -> DeploymentResult:
    deployment_files = [DeploymentFile(name=f["name"], content=f["content"]) for f in files]
    return await deploy_service.quick_deploy(files=deployment_files, project_name=project_name, provider=DeployProvider(provider), token=token)
