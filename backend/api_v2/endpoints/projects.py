"""
Project management endpoints with caching
"""
from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from datetime import datetime, timezone
from schemas.project_schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from auth import get_current_user
from config import settings
from api_v2.middleware import limiter, RateLimits
from api_v2.middleware.cache import cached, CacheConfig, invalidate_project_cache
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# MongoDB connection
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]


@router.get(
    "",
    response_model=List[ProjectResponse],
    summary="List user projects",
    description="Get all projects for the authenticated user with caching"
)
@limiter.limit(RateLimits.PROJECT_LIST)
@cached(ttl=CacheConfig.PROJECT_LIST, key_prefix="projects")
async def list_projects(current_user: dict = Depends(get_current_user)):
    """
    List all projects for current user

    Args:
        current_user: Authenticated user from JWT

    Returns:
        List of projects

    Cache:
        15 minutes TTL, invalidated on project create/update/delete
    """
    projects = await db.projects.find(
        {"user_id": current_user['user_id']},
        {"_id": 0}
    ).to_list(1000)

    # Parse datetime fields
    for proj in projects:
        if isinstance(proj.get('created_at'), str):
            proj['created_at'] = datetime.fromisoformat(proj['created_at'])
        if isinstance(proj.get('updated_at'), str):
            proj['updated_at'] = datetime.fromisoformat(proj['updated_at'])

    return projects


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project",
    description="Create a new project with files and conversation history"
)
@limiter.limit(RateLimits.PROJECT_CREATE)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new project

    Args:
        project: Project data (name, description, files, etc.)
        current_user: Authenticated user

    Returns:
        Created project

    Side effects:
        Invalidates project list cache for user
    """
    from models import Project

    # Create project instance
    new_project = Project(
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        files=[f.model_dump() for f in project.files],
        conversation_history=[m.model_dump() for m in project.conversation_history]
    )

    # Prepare for database
    project_dict = new_project.model_dump()
    project_dict['user_id'] = current_user['user_id']
    project_dict['created_at'] = project_dict['created_at'].isoformat()
    project_dict['updated_at'] = project_dict['updated_at'].isoformat()

    # Insert into database
    await db.projects.insert_one(project_dict)

    logger.info(f"Project created: {new_project.id} by user {current_user['user_id']}")

    # Invalidate cache
    from api_v2.middleware.cache import invalidate_user_cache
    await invalidate_user_cache(current_user['user_id'])

    return ProjectResponse(**new_project.model_dump())


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project details",
    description="Get detailed information about a specific project"
)
@cached(ttl=CacheConfig.PROJECT_DETAIL, key_prefix="project")
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get project by ID

    Args:
        project_id: Project unique identifier
        current_user: Authenticated user

    Returns:
        Project details

    Raises:
        HTTPException 404: Project not found
        HTTPException 403: User doesn't own project

    Cache:
        10 minutes TTL
    """
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet non trouvé"
        )

    # Verify ownership
    if project.get('user_id') != current_user['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé à ce projet"
        )

    # Parse datetime fields
    if isinstance(project.get('created_at'), str):
        project['created_at'] = datetime.fromisoformat(project['created_at'])
    if isinstance(project.get('updated_at'), str):
        project['updated_at'] = datetime.fromisoformat(project['updated_at'])

    return ProjectResponse(**project)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update project details, files, or conversation history"
)
@limiter.limit(RateLimits.PROJECT_UPDATE)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update existing project

    Args:
        project_id: Project ID to update
        updates: Fields to update
        current_user: Authenticated user

    Returns:
        Updated project

    Raises:
        HTTPException 404: Project not found
        HTTPException 403: User doesn't own project

    Side effects:
        Invalidates project cache
    """
    # Verify project exists and user owns it
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet non trouvé"
        )

    if project.get('user_id') != current_user['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )

    # Prepare update data
    update_data = updates.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()

    # Convert file and message objects to dicts
    if 'files' in update_data:
        update_data['files'] = [f.model_dump() if hasattr(f, 'model_dump') else f for f in update_data['files']]
    if 'conversation_history' in update_data:
        update_data['conversation_history'] = [m.model_dump() if hasattr(m, 'model_dump') else m for m in update_data['conversation_history']]

    # Update in database
    await db.projects.update_one(
        {"id": project_id},
        {"$set": update_data}
    )

    logger.info(f"Project updated: {project_id}")

    # Invalidate cache
    await invalidate_project_cache(project_id)

    # Get updated project
    updated_project = await get_project(project_id, current_user)
    return updated_project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Permanently delete a project"
)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete project

    Args:
        project_id: Project ID to delete
        current_user: Authenticated user

    Raises:
        HTTPException 404: Project not found
        HTTPException 403: User doesn't own project

    Side effects:
        Invalidates project cache
    """
    # Verify ownership
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projet non trouvé"
        )

    if project.get('user_id') != current_user['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )

    # Delete from database
    result = await db.projects.delete_one({"id": project_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Échec de suppression"
        )

    logger.info(f"Project deleted: {project_id}")

    # Invalidate cache
    await invalidate_project_cache(project_id)
    from api_v2.middleware.cache import invalidate_user_cache
    await invalidate_user_cache(current_user['user_id'])

    return None
