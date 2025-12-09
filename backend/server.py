from fastapi import FastAPI, APIRouter, HTTPException, Body, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import json
import base64
from github import Github, GithubException
from agents.orchestrator import OrchestratorAgent
from agents.orchestrator_v2 import OrchestratorV2
from agents.context_compressor import compress_context_if_needed
from config import settings
from routes_auth import router as auth_router
from routes_billing import router as billing_router
from routes_admin import router as admin_router
from routes_support import router as support_router
from routes_version_control import router as version_control_router
from routes_templates import router as templates_router
from routes_streaming import router as streaming_router
from realtime.websocket_routes import router as realtime_router
from auth import get_current_user
from fastapi import Path, Query
from middleware.security import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    validate_id_format,
    sanitize_error_message,
    log_security_event
)
from middleware.rate_limiter import limiter, RateLimits, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Import Memori SDK for persistent memory
try:
    from memory_service import DevoraMemory, get_memory_instance
    MEMORY_ENABLED = True
except ImportError:
    logging.warning("memory_service not available, running without persistent memory")
    MEMORY_ENABLED = False

# MongoDB connection with centralized config
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class UserSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    openrouter_api_key: Optional[str] = None
    github_token: Optional[str] = None
    vercel_token: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSettingsUpdate(BaseModel):
    openrouter_api_key: Optional[str] = None
    github_token: Optional[str] = None
    vercel_token: Optional[str] = None

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationMessage(BaseModel):
    """Simplified message for conversation history"""
    role: str
    content: str

class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectFile(BaseModel):
    name: str
    content: str
    language: str  # 'html', 'css', 'javascript', etc.

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    files: List[ProjectFile] = []
    conversation_history: List[ConversationMessage] = []  # BUG 4 FIX: Store conversation
    conversation_id: Optional[str] = None
    github_repo_url: Optional[str] = None
    vercel_url: Optional[str] = None
    project_type: Optional[str] = None  # saas, ecommerce, blog, etc.
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: str = "gpt-4o"
    provider: str = "openai"

class GenerateCodeRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None
    project_id: Optional[str] = None
    model: str = "gpt-4o"
    provider: str = "openai"

class OpenRouterRequest(BaseModel):
    message: str
    model: str
    api_key: str
    conversation_history: List[Dict[str, str]] = []

class AgenticRequest(BaseModel):
    message: str
    model: str
    api_key: str
    current_files: List[ProjectFile] = []
    conversation_history: List[Dict[str, str]] = []  # BUG 4 FIX: Accept conversation
    project_id: Optional[str] = None
    user_id: Optional[str] = None  # For memory integration

class FullStackRequest(BaseModel):
    """Request for full-stack project generation"""
    message: str
    model: str
    api_key: str
    current_files: List[ProjectFile] = []
    conversation_history: List[Dict[str, str]] = []
    project_type: Optional[str] = None  # saas, ecommerce, blog, dashboard, api
    project_id: Optional[str] = None
    user_id: Optional[str] = None  # For memory integration

class ExportGithubRequest(BaseModel):
    project_id: str
    repo_name: str
    github_token: str
    private: bool = False

class DeployVercelRequest(BaseModel):
    project_id: str
    vercel_token: str
    project_name: str

# User Settings Routes
@api_router.get("/settings", response_model=UserSettings)
async def get_settings():
    settings = await db.settings.find_one({}, {"_id": 0})
    if not settings:
        default_settings = UserSettings()
        doc = default_settings.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.settings.insert_one(doc)
        return default_settings
    
    if isinstance(settings.get('created_at'), str):
        settings['created_at'] = datetime.fromisoformat(settings['created_at'])
    if isinstance(settings.get('updated_at'), str):
        settings['updated_at'] = datetime.fromisoformat(settings['updated_at'])
    
    return UserSettings(**settings)

@api_router.put("/settings", response_model=UserSettings)
async def update_settings(updates: UserSettingsUpdate):
    current_settings = await get_settings()
    
    update_data = updates.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.now(timezone.utc)
    
    await db.settings.update_one(
        {"id": current_settings.id},
        {"$set": {**update_data, 'updated_at': update_data['updated_at'].isoformat()}}
    )
    
    updated_settings = await get_settings()
    return updated_settings

# Conversation Routes
@api_router.post("/conversations", response_model=Conversation)
async def create_conversation(title: str = Body(..., embed=True)):
    conversation = Conversation(title=title)
    doc = conversation.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    for msg in doc['messages']:
        msg['timestamp'] = msg['timestamp'].isoformat()
    
    await db.conversations.insert_one(doc)
    return conversation

@api_router.get("/conversations", response_model=List[Conversation])
async def get_conversations():
    conversations = await db.conversations.find({}, {"_id": 0}).to_list(1000)
    
    for conv in conversations:
        if isinstance(conv.get('created_at'), str):
            conv['created_at'] = datetime.fromisoformat(conv['created_at'])
        if isinstance(conv.get('updated_at'), str):
            conv['updated_at'] = datetime.fromisoformat(conv['updated_at'])
        for msg in conv.get('messages', []):
            if isinstance(msg.get('timestamp'), str):
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    
    return conversations

@api_router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    conversation = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if isinstance(conversation.get('created_at'), str):
        conversation['created_at'] = datetime.fromisoformat(conversation['created_at'])
    if isinstance(conversation.get('updated_at'), str):
        conversation['updated_at'] = datetime.fromisoformat(conversation['updated_at'])
    for msg in conversation.get('messages', []):
        if isinstance(msg.get('timestamp'), str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    
    return Conversation(**conversation)

@api_router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str = Path(..., min_length=1, max_length=255),
    current_user: dict = Depends(get_current_user)
):
    if not validate_id_format(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    result = await db.conversations.delete_one({"id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}

# Project Routes
@api_router.post("/projects", response_model=Project)
async def create_project(project: Project, current_user: dict = Depends(get_current_user)):
    doc = project.model_dump()
    doc['user_id'] = current_user['user_id']  # Link to user
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.projects.insert_one(doc)
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects(current_user: dict = Depends(get_current_user)):
    projects = await db.projects.find({"user_id": current_user['user_id']}, {"_id": 0}).to_list(1000)
    
    for proj in projects:
        if isinstance(proj.get('created_at'), str):
            proj['created_at'] = datetime.fromisoformat(proj['created_at'])
        if isinstance(proj.get('updated_at'), str):
            proj['updated_at'] = datetime.fromisoformat(proj['updated_at'])
    
    return projects

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str = Path(..., min_length=1, max_length=255),
    current_user: dict = Depends(get_current_user)
):
    if not validate_id_format(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    project = await db.projects.find_one({"id": project_id, "user_id": current_user["user_id"]}, {"_id": 0})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if isinstance(project.get('created_at'), str):
        project['created_at'] = datetime.fromisoformat(project['created_at'])
    if isinstance(project.get('updated_at'), str):
        project['updated_at'] = datetime.fromisoformat(project['updated_at'])
    
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str = Path(..., min_length=1, max_length=255),
    project: Project = Body(...),
    current_user: dict = Depends(get_current_user)
):
    if not validate_id_format(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    existing = await db.projects.find_one({"id": project_id, "user_id": current_user["user_id"]}, {"id": 1})
    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")
    project.updated_at = datetime.now(timezone.utc)
    doc = project.model_dump()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.projects.update_one(
        {"id": project_id},
        {"$set": doc}
    )
    
    return project

@api_router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str = Path(..., min_length=1, max_length=255),
    current_user: dict = Depends(get_current_user)
):
    if not validate_id_format(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    result = await db.projects.delete_one({"id": project_id, "user_id": current_user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# OpenRouter Models List
@api_router.get("/openrouter/models")
async def get_openrouter_models(api_key: str):
    """Get available models from OpenRouter"""
    if not api_key or not api_key.strip():
        raise HTTPException(status_code=422, detail="API key is required")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": os.environ.get('FRONTEND_URL', 'http://localhost:3000'),
                    "X-Title": "Devora"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch models")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Code Generation with OpenRouter
@api_router.post("/generate/openrouter")
async def generate_with_openrouter(request: OpenRouterRequest):
    """Generate code using OpenRouter API with context compression"""
    try:
        system_prompt = """You are an expert full-stack developer. Generate clean, production-ready code based on user requirements.
        
When generating code:
        1. For single files, provide complete, working code
        2. For multi-file projects, structure them clearly with file names
        3. Include HTML, CSS, and JavaScript as needed
        4. Use modern best practices
        5. Make the code responsive and accessible
        6. Add helpful comments
        
        Format your response with clear file separators like:
        ```html
        // filename: index.html
        [code here]
        ```
        
        ```css
        // filename: styles.css
        [code here]
        ```
        
        ```javascript
        // filename: script.js
        [code here]
        ```
        """
        
        # Apply context compression if needed
        conversation = request.conversation_history.copy()
        compressed_messages, _, compression_stats = compress_context_if_needed(
            conversation,
            system_prompt=system_prompt,
            keep_recent_messages=8
        )
        
        if compression_stats.get('compressed'):
            logging.info(f"Context compressed: saved {compression_stats['total']['tokens_saved']} tokens")
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add compressed conversation history
        messages.extend(compressed_messages)
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {request.api_key}",
                    "HTTP-Referer": os.environ.get('FRONTEND_URL', 'http://localhost:3000'),
                    "X-Title": "Devora",
                    "Content-Type": "application/json"
                },
                json={
                    "model": request.model,
                    "messages": messages
                },
                timeout=120.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result["choices"][0]["message"]["content"],
                    "model": request.model,
                    "context_compressed": compression_stats.get('compressed', False)
                }
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        logging.error(f"OpenRouter generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# GitHub Export
@api_router.post("/github/export")
async def export_to_github(request: ExportGithubRequest):
    """Export project to GitHub repository"""
    try:
        # Get project
        project = await get_project(request.project_id)
        
        if not project.files:
            raise HTTPException(status_code=400, detail="Project has no files to export")
        
        # Validate repo name
        repo_name = request.repo_name.strip()
        if not repo_name or '/' in repo_name or ' ' in repo_name:
            raise HTTPException(status_code=400, detail="Invalid repository name")
        
        # Create GitHub client
        g = Github(request.github_token)
        user = g.get_user()
        
        # Create repository
        try:
            repo = user.create_repo(
                name=repo_name,
                description=project.description or f"Created with Devora - {project.name}",
                private=request.private,
                auto_init=False  # Don't init to avoid merge conflicts
            )
        except GithubException as e:
            if "already exists" in str(e).lower() or e.status == 422:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Le repository '{repo_name}' existe deja. Choisissez un autre nom."
                )
            raise HTTPException(status_code=400, detail=f"Erreur GitHub: {str(e)}")
        
        # Add README first to initialize repo
        readme_content = f"# {project.name}\n\n{project.description or 'Created with Devora'}\n"
        try:
            repo.create_file(
                path="README.md",
                message="Initial commit - Created with Devora",
                content=readme_content
            )
        except GithubException as e:
            logging.warning(f"README creation warning: {str(e)}")
        
        # Add project files
        files_created = 0
        for file in project.files:
            try:
                repo.create_file(
                    path=file.name,
                    message=f"Add {file.name}",
                    content=file.content
                )
                files_created += 1
            except GithubException as e:
                logging.error(f"Error creating file {file.name}: {str(e)}")
        
        # Update project with GitHub URL
        project.github_repo_url = repo.html_url
        await update_project(request.project_id, project)
        
        return {
            "success": True,
            "repo_url": repo.html_url,
            "files_created": files_created,
            "message": f"Projet exporte sur GitHub avec {files_created} fichier(s)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"GitHub export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export: {str(e)}")

# Vercel Deploy
@api_router.post("/vercel/deploy")
async def deploy_to_vercel(request: DeployVercelRequest):
    """Deploy project to Vercel"""
    try:
        # Get project
        project = await get_project(request.project_id)

        if not project.files:
            raise HTTPException(status_code=400, detail="Project has no files to deploy")

        # Validate project name
        project_name = request.project_name.strip().lower()
        project_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in project_name)

        # Detect if Full-Stack project (Next.js/TypeScript)
        file_names = [f.name for f in project.files]
        has_typescript = any(f.endswith('.tsx') or f.endswith('.ts') for f in file_names)
        has_package_json = 'package.json' in file_names
        has_next_config = 'next.config.js' in file_names or 'next.config.ts' in file_names
        is_fullstack = has_typescript or (has_package_json and has_next_config)

        # Default files to exclude for Full-Stack projects
        default_files = ['index.html', 'styles.css', 'script.js']

        # Prepare files for Vercel
        files = []
        for file in project.files:
            # Skip default starter files for Full-Stack projects
            if is_fullstack and file.name in default_files:
                logging.info(f"Skipping default file for fullstack deploy: {file.name}")
                continue
            files.append({
                "file": file.name,
                "data": base64.b64encode(file.content.encode()).decode(),
                "encoding": "base64"
            })

        # Add vercel.json to allow iframe embedding if not present
        if not any(f["file"] == "vercel.json" for f in files):
            vercel_config = {
                "headers": [
                    {
                        "source": "/(.*)",
                        "headers": [
                            {"key": "X-Frame-Options", "value": "ALLOWALL"},
                            {"key": "Content-Security-Policy", "value": "frame-ancestors *"}
                        ]
                    }
                ]
            }
            # For Next.js projects, also set the framework
            if is_fullstack:
                vercel_config["framework"] = "nextjs"

            files.append({
                "file": "vercel.json",
                "data": base64.b64encode(json.dumps(vercel_config, indent=2).encode()).decode(),
                "encoding": "base64"
            })
            logging.info("Added vercel.json for iframe support")

        # Determine framework setting
        framework = "nextjs" if is_fullstack else None

        # Deploy to Vercel
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vercel.com/v13/deployments",
                headers={
                    "Authorization": f"Bearer {request.vercel_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": project_name,
                    "files": files,
                    "projectSettings": {
                        "framework": framework
                    },
                    "target": "production"
                },
                timeout=120.0
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                deployment_url = f"https://{result.get('url', '')}"
                
                # Update project with Vercel URL
                project.vercel_url = deployment_url
                await update_project(request.project_id, project)
                
                return {
                    "success": True,
                    "url": deployment_url,
                    "deployment_id": result.get('id'),
                    "message": "Projet deploye sur Vercel avec succes"
                }
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=401, 
                    detail="Token Vercel invalide ou expire"
                )
            elif response.status_code == 403:
                raise HTTPException(
                    status_code=403,
                    detail="Permissions insuffisantes. Verifiez les scopes de votre token."
                )
            else:
                error_detail = response.json() if response.text else {}
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=error_detail.get('error', {}).get('message', response.text)
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Vercel deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du deploiement: {str(e)}")

# Agentic Code Generation (Original - HTML/CSS/JS)
@api_router.post("/generate/agentic")
async def generate_with_agentic_system(request: AgenticRequest):
    """Generate code using the agentic system with context compression and persistent memory"""
    try:
        # Initialize memory if available
        memory = None
        memory_context = ""
        user_preferences = {}
        
        if MEMORY_ENABLED and request.user_id:
            try:
                memory = get_memory_instance(request.user_id, request.project_id)
                
                # Retrieve relevant context from past interactions
                relevant_memories = memory.get_relevant_context(request.message, limit=5)
                if relevant_memories:
                    memory_context = "\n\n--- Previous relevant context ---\n"
                    for mem in relevant_memories:
                        memory_context += f"- {mem.get('content', '')[:200]}...\n"
                
                # Get user preferences
                user_preferences = memory.get_user_preferences()
                logging.info(f"Memory loaded: {len(relevant_memories)} relevant memories, {len(user_preferences)} preferences")
            except Exception as mem_error:
                logging.warning(f"Memory retrieval error: {mem_error}")
        
        # Apply context compression to files if needed
        files_as_dicts = [f.model_dump() for f in request.current_files]
        conversation = request.conversation_history.copy()
        
        compressed_messages, compressed_files, compression_stats = compress_context_if_needed(
            conversation,
            files=files_as_dicts,
            keep_recent_messages=6,
            max_file_tokens=3000
        )
        
        if compression_stats.get('compressed'):
            logging.info(f"Agentic context compressed: saved {compression_stats['total']['tokens_saved']} tokens")
        
        # Enhance request with memory context
        enhanced_message = request.message
        if memory_context:
            enhanced_message = f"{request.message}\n{memory_context}"
        
        # Create orchestrator
        orchestrator = OrchestratorAgent(
            api_key=request.api_key,
            model=request.model
        )
        
        # Store progress events
        progress_events = []
        
        async def progress_callback(event: str, data: dict):
            progress_events.append({
                "event": event,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        orchestrator.set_progress_callback(progress_callback)
        
        # Execute agentic workflow with compressed context
        result = await orchestrator.execute(
            user_request=enhanced_message,
            current_files=compressed_files,
            conversation_history=compressed_messages
        )
        
        # Store interaction in memory for future learning
        if memory and result.get('success'):
            try:
                files_generated = [f.get('name', '') for f in result.get('files', [])]
                memory.store_interaction(
                    user_message=request.message,
                    assistant_response=f"Generated {len(files_generated)} files: {', '.join(files_generated)}",
                    metadata={
                        "mode": "agentic",
                        "model": request.model,
                        "files_count": len(files_generated),
                        "iterations": result.get('iterations', 1),
                        "project_id": request.project_id
                    }
                )
                logging.info("Interaction stored in memory")
            except Exception as store_error:
                logging.warning(f"Failed to store interaction: {store_error}")
        
        # Return result with progress events
        return {
            **result,
            "progress_events": progress_events,
            "context_compressed": compression_stats.get('compressed', False),
            "compression_stats": compression_stats if compression_stats.get('compressed') else None,
            "memory_enabled": memory is not None
        }
        
    except Exception as e:
        logging.error(f"Agentic generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Full-Stack Project Generation (NEW - Next.js/Supabase/Stripe)
@api_router.post("/generate/fullstack")
async def generate_fullstack_project(request: FullStackRequest):
    """Generate full-stack Next.js project using OrchestratorV2 with persistent memory.
    
    This endpoint uses specialized agents to generate:
    - Frontend: Next.js 14+ App Router, React, Tailwind, shadcn/ui
    - Backend: API Routes, Server Actions, Auth middleware
    - Database: Supabase schemas, RLS policies, migrations
    
    Supported project_type values:
    - saas: SaaS application with auth, billing, dashboard
    - ecommerce: Online store with products, cart, checkout
    - blog: Blog/CMS with MDX support
    - dashboard: Admin dashboard with analytics
    - api: REST/GraphQL API service
    - custom: Auto-detect from description
    """
    try:
        # Initialize memory if available
        memory = None
        memory_context = ""
        user_preferences = {}
        
        if MEMORY_ENABLED and request.user_id:
            try:
                memory = get_memory_instance(request.user_id, request.project_id)
                
                # Retrieve relevant context from past interactions
                relevant_memories = memory.get_relevant_context(request.message, limit=5)
                if relevant_memories:
                    memory_context = "\n\n--- Previous relevant context ---\n"
                    for mem in relevant_memories:
                        memory_context += f"- {mem.get('content', '')[:200]}...\n"
                
                # Get user preferences (preferred stack, patterns, etc.)
                user_preferences = memory.get_user_preferences()
                logging.info(f"Fullstack memory loaded: {len(relevant_memories)} memories, {len(user_preferences)} preferences")
            except Exception as mem_error:
                logging.warning(f"Memory retrieval error: {mem_error}")
        
        # Prepare files
        files_as_dicts = [f.model_dump() for f in request.current_files]
        conversation = request.conversation_history.copy()
        
        # Enhance request with memory context
        enhanced_message = request.message
        if memory_context:
            enhanced_message = f"{request.message}\n{memory_context}"
        
        # Apply user preferences if available
        project_type = request.project_type
        if not project_type and user_preferences.get('preferred_project_type'):
            project_type = user_preferences['preferred_project_type']
        
        # Create OrchestratorV2 for full-stack generation
        orchestrator = OrchestratorV2(
            api_key=request.api_key,
            model=request.model
        )
        
        # Store progress events for real-time feedback
        progress_events = []
        
        async def progress_callback(event: str, data: dict):
            progress_events.append({
                "event": event,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        orchestrator.set_progress_callback(progress_callback)
        
        # Execute full-stack generation workflow
        result = await orchestrator.execute(
            user_request=enhanced_message,
            current_files=files_as_dicts,
            conversation_history=conversation,
            project_type=project_type
        )
        
        # Store interaction in memory for future learning
        if memory and result.get('success'):
            try:
                files_generated = [f.get('name', '') for f in result.get('files', [])]
                memory.store_interaction(
                    user_message=request.message,
                    assistant_response=f"Generated fullstack project with {len(files_generated)} files: {', '.join(files_generated[:5])}...",
                    metadata={
                        "mode": "fullstack",
                        "model": request.model,
                        "project_type": project_type or "auto",
                        "files_count": len(files_generated),
                        "stack": ["next.js", "typescript", "tailwind", "supabase"],
                        "project_id": request.project_id
                    }
                )
                
                # Learn user preference for project type
                if project_type:
                    memory.store_interaction(
                        user_message=f"User prefers {project_type} projects",
                        assistant_response="Preference noted",
                        metadata={"type": "preference", "key": "preferred_project_type", "value": project_type}
                    )
                
                logging.info("Fullstack interaction stored in memory")
            except Exception as store_error:
                logging.warning(f"Failed to store fullstack interaction: {store_error}")
        
        # Return result with progress events and metadata
        return {
            **result,
            "progress_events": progress_events,
            "generation_mode": "fullstack",
            "stack": {
                "frontend": ["next.js", "react", "tailwind", "shadcn/ui"],
                "backend": ["api-routes", "server-actions"],
                "database": ["supabase", "postgresql"]
            },
            "memory_enabled": memory is not None
        }
        
    except Exception as e:
        logging.error(f"Full-stack generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# List available templates
@api_router.get("/templates")
async def list_templates():
    """List available project templates"""
    from templates import TEMPLATES
    
    templates_list = []
    for key, template in TEMPLATES.items():
        templates_list.append({
            "key": key,
            "name": template.get("name"),
            "description": template.get("description"),
            "stack": template.get("stack", {}),
            "features": [f["name"] for f in template.get("features", [])]
        })
    
    return {"templates": templates_list}

# Health check
@api_router.get("/")
async def root():
    return {
        "message": "Devora API", 
        "status": "running", 
        "version": "4.0.0",
        "features": [
            "openrouter",
            "agentic",
            "fullstack",
            "github-export",
            "vercel-deploy",
            "version-control",
            "templates-marketplace",
            "streaming-generation",
            "realtime-collaboration",
            "persistent-memory" if MEMORY_ENABLED else "memory-disabled"
        ]
    }

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(support_router, prefix="/api")
app.include_router(version_control_router, prefix="/api")
app.include_router(templates_router, prefix="/api")
app.include_router(streaming_router, prefix="/api")
app.include_router(realtime_router)
app.include_router(api_router)

# Security Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestValidationMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS - Configured properly for security
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:5173",
]
allowed_origins = [o for o in allowed_origins if o]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
