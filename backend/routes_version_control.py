"""
Version Control API Routes

Git-like version control endpoints for Devora projects.
Provides commit, history, restore, and diff functionality.

Routes:
- GET  /projects/{id}/commits          - Get commit history
- POST /projects/{id}/commits          - Create a new commit
- GET  /projects/{id}/commits/count    - Get commit count
- GET  /commits/{id}                   - Get commit details
- POST /commits/{id}/restore           - Restore to a commit
- GET  /commits/{id}/diff              - Get commit diff
- POST /commits/compare                - Compare two commits
- GET  /projects/{id}/files/{path}/history - Get file history
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from config import settings
from auth import get_current_user
from services.version_control import (
    VersionControlService,
    Commit,
    CommitCreate,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["version-control"])

# MongoDB connection with centralized config
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

# Initialize the version control service
vc_service = VersionControlService(db)


# ============================================================================
# Request/Response Models
# ============================================================================

class CommitRequest(BaseModel):
    """Request body for creating a commit"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Commit message describing the changes"
    )
    files: List[Dict[str, Any]] = Field(
        ...,
        description="Current project files to snapshot"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add user authentication feature",
                "files": [
                    {
                        "name": "auth.py",
                        "content": "def login(user, password): ...",
                        "language": "python"
                    }
                ]
            }
        }


class CommitSummaryResponse(BaseModel):
    """Summary response for a commit (without full file contents)"""
    id: str
    project_id: str
    message: str
    author_id: str
    author_email: Optional[str] = None
    parent_id: Optional[str] = None
    files_count: int
    diff_summary: Dict[str, int]
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "project_id": "proj_456",
                "message": "Add login feature",
                "author_id": "user_789",
                "author_email": "user@example.com",
                "parent_id": "def456",
                "files_count": 5,
                "diff_summary": {
                    "added": 2,
                    "modified": 1,
                    "deleted": 0
                },
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class CommitHistoryResponse(BaseModel):
    """Response for commit history listing"""
    commits: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int
    has_more: bool


class RestoreRequest(BaseModel):
    """Request for restore operation"""
    create_commit: bool = Field(
        default=True,
        description="Whether to create a new commit after restore"
    )
    commit_message: Optional[str] = Field(
        default=None,
        description="Custom commit message (default: 'Restore to commit {id}')"
    )


class RestoreResponse(BaseModel):
    """Response for restore operation"""
    success: bool
    files: List[Dict[str, Any]]
    files_count: int
    restored_from_commit: str
    new_commit_id: Optional[str] = None
    message: str


class CompareRequest(BaseModel):
    """Request to compare two commits"""
    from_commit_id: str = Field(..., description="Base commit ID (older)")
    to_commit_id: str = Field(..., description="Target commit ID (newer)")


class DiffResponse(BaseModel):
    """Response containing diff information"""
    added: List[str]
    modified: List[Dict[str, Any]]
    deleted: List[str]
    unchanged: List[str]
    stats: Dict[str, int]


# ============================================================================
# Project Commit Routes
# ============================================================================

@router.get("/projects/{project_id}/commits", response_model=CommitHistoryResponse)
async def get_commit_history(
    project_id: str = Path(..., description="Project ID"),
    skip: int = Query(0, ge=0, description="Number of commits to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum commits to return"),
    include_files: bool = Query(False, description="Include full file snapshots"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the commit history for a project.

    Returns a paginated list of commits, ordered by most recent first.
    By default, file contents are excluded for performance.
    """
    # Verify project exists and belongs to user
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["user_id"]},
        {"_id": 0, "id": 1}
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or you don't have access to it"
        )

    # Get commits
    commits = await vc_service.get_history(
        project_id=project_id,
        limit=limit + 1,  # Get one extra to check if there are more
        skip=skip,
        include_files=include_files
    )

    # Check if there are more commits
    has_more = len(commits) > limit
    if has_more:
        commits = commits[:limit]

    # Get total count
    total = await vc_service.get_commit_count(project_id)

    # Convert commits to summary format if files not included
    if not include_files:
        formatted_commits = []
        for c in commits:
            formatted_commits.append({
                "id": c.get("id"),
                "project_id": c.get("project_id"),
                "message": c.get("message"),
                "author_id": c.get("author_id"),
                "author_email": c.get("author_email"),
                "parent_id": c.get("parent_id"),
                "files_count": len(c.get("files_snapshot", [])) if "files_snapshot" in c else c.get("files_count", 0),
                "diff_summary": {
                    "added": len(c.get("diff", {}).get("added", [])),
                    "modified": len(c.get("diff", {}).get("modified", [])),
                    "deleted": len(c.get("diff", {}).get("deleted", [])),
                },
                "created_at": c.get("created_at"),
            })
        commits = formatted_commits

    return CommitHistoryResponse(
        commits=commits,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )


@router.post("/projects/{project_id}/commits", response_model=CommitSummaryResponse)
async def create_commit(
    project_id: str = Path(..., description="Project ID"),
    commit_data: CommitRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new commit for a project.

    This saves a snapshot of the current project files along with a commit message.
    The diff from the previous commit is automatically calculated.
    """
    # Verify project exists and belongs to user
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["user_id"]},
        {"_id": 0, "id": 1}
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or you don't have access to it"
        )

    try:
        commit = await vc_service.commit(
            project_id=project_id,
            message=commit_data.message,
            files=commit_data.files,
            author_id=current_user["user_id"],
            author_email=current_user.get("email")
        )

        logger.info(f"Created commit {commit.id} for project {project_id} by user {current_user['user_id']}")

        return CommitSummaryResponse(
            id=commit.id,
            project_id=commit.project_id,
            message=commit.message,
            author_id=commit.author_id,
            author_email=commit.author_email,
            parent_id=commit.parent_id,
            files_count=len(commit.files_snapshot),
            diff_summary={
                "added": len(commit.diff.get("added", [])),
                "modified": len(commit.diff.get("modified", [])),
                "deleted": len(commit.diff.get("deleted", [])),
            },
            created_at=commit.created_at
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating commit: {e}")
        raise HTTPException(status_code=500, detail="Failed to create commit")


@router.get("/projects/{project_id}/commits/count")
async def get_commit_count(
    project_id: str = Path(..., description="Project ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get the total number of commits for a project."""
    # Verify project access
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["user_id"]},
        {"_id": 0, "id": 1}
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or you don't have access to it"
        )

    count = await vc_service.get_commit_count(project_id)

    return {"project_id": project_id, "commit_count": count}


# ============================================================================
# Individual Commit Routes
# ============================================================================

@router.get("/commits/{commit_id}")
async def get_commit(
    commit_id: str = Path(..., description="Commit ID"),
    include_files: bool = Query(True, description="Include full file snapshots"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific commit.

    By default includes full file snapshots. Set include_files=false
    for a lighter response.
    """
    commit = await vc_service.get_commit(commit_id)

    if not commit:
        raise HTTPException(status_code=404, detail="Commit not found")

    # Verify user has access to the project
    project = await db.projects.find_one(
        {"id": commit.project_id, "user_id": current_user["user_id"]},
        {"_id": 0, "id": 1}
    )

    if not project:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this commit's project"
        )

    if include_files:
        return commit.model_dump()
    else:
        return commit.to_summary()


@router.post("/commits/{commit_id}/restore", response_model=RestoreResponse)
async def restore_commit(
    commit_id: str = Path(..., description="Commit ID to restore to"),
    restore_options: RestoreRequest = Body(default=RestoreRequest()),
    current_user: dict = Depends(get_current_user)
):
    """
    Restore project files to a specific commit state.

    This returns the files from the specified commit. Optionally creates
    a new commit recording the restore operation.
    """
    # Get the commit to restore
    commit = await vc_service.get_commit(commit_id)

    if not commit:
        raise HTTPException(status_code=404, detail="Commit not found")

    # Verify user has access to the project
    project = await db.projects.find_one(
        {"id": commit.project_id, "user_id": current_user["user_id"]},
        {"_id": 0, "id": 1}
    )

    if not project:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this commit's project"
        )

    try:
        # Restore files
        files = await vc_service.restore(commit_id)

        new_commit_id = None

        # Optionally create a new commit
        if restore_options.create_commit:
            message = restore_options.commit_message or f"Restore to commit {commit_id[:8]}"

            new_commit = await vc_service.commit(
                project_id=commit.project_id,
                message=message,
                files=files,
                author_id=current_user["user_id"],
                author_email=current_user.get("email")
            )
            new_commit_id = new_commit.id

        # Update the project's current files
        await db.projects.update_one(
            {"id": commit.project_id},
            {
                "$set": {
                    "files": files,
                    "updated_at": datetime.now().isoformat()
                }
            }
        )

        logger.info(f"Restored project {commit.project_id} to commit {commit_id}")

        return RestoreResponse(
            success=True,
            files=files,
            files_count=len(files),
            restored_from_commit=commit_id,
            new_commit_id=new_commit_id,
            message=f"Successfully restored {len(files)} files from commit {commit_id[:8]}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error restoring commit: {e}")
        raise HTTPException(status_code=500, detail="Failed to restore commit")


@router.get("/commits/{commit_id}/diff", response_model=DiffResponse)
async def get_commit_diff(
    commit_id: str = Path(..., description="Commit ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the diff for a specific commit.

    Returns the changes made in this commit compared to its parent.
    """
    commit = await vc_service.get_commit(commit_id)

    if not commit:
        raise HTTPException(status_code=404, detail="Commit not found")

    # Verify user has access
    project = await db.projects.find_one(
        {"id": commit.project_id, "user_id": current_user["user_id"]},
        {"_id": 0, "id": 1}
    )

    if not project:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this commit's project"
        )

    try:
        diff = await vc_service.get_diff(commit_id)
        return DiffResponse(**diff)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/commits/compare", response_model=DiffResponse)
async def compare_commits(
    compare_data: CompareRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Compare two commits and return the diff between them.

    Useful for seeing all changes between any two points in history.
    """
    # Get both commits and verify access
    from_commit = await vc_service.get_commit(compare_data.from_commit_id)
    to_commit = await vc_service.get_commit(compare_data.to_commit_id)

    if not from_commit:
        raise HTTPException(status_code=404, detail=f"From commit {compare_data.from_commit_id} not found")
    if not to_commit:
        raise HTTPException(status_code=404, detail=f"To commit {compare_data.to_commit_id} not found")

    # Verify same project
    if from_commit.project_id != to_commit.project_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot compare commits from different projects"
        )

    # Verify user has access
    project = await db.projects.find_one(
        {"id": from_commit.project_id, "user_id": current_user["user_id"]},
        {"_id": 0, "id": 1}
    )

    if not project:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to these commits' project"
        )

    try:
        diff = await vc_service.compare_commits(
            compare_data.from_commit_id,
            compare_data.to_commit_id
        )
        return DiffResponse(**diff)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# File History Route
# ============================================================================

@router.get("/projects/{project_id}/files/{file_path:path}/history")
async def get_file_history(
    project_id: str = Path(..., description="Project ID"),
    file_path: str = Path(..., description="File path within the project"),
    limit: int = Query(20, ge=1, le=50, description="Maximum versions to return"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the version history of a specific file.

    Shows when the file was added, modified, or deleted across commits.
    """
    # Verify project access
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["user_id"]},
        {"_id": 0, "id": 1}
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or you don't have access to it"
        )

    history = await vc_service.get_file_history(
        project_id=project_id,
        file_name=file_path,
        limit=limit
    )

    return {
        "project_id": project_id,
        "file_path": file_path,
        "versions": history,
        "total_versions": len(history)
    }


# ============================================================================
# Initialization
# ============================================================================

@router.on_event("startup")
async def startup_event():
    """Initialize indexes on startup"""
    await vc_service.ensure_indexes()
    logger.info("Version control service initialized")
