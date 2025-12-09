"""
Code generation endpoints (placeholder - uses existing logic)
"""
from fastapi import APIRouter, HTTPException, status
from schemas.generation_schemas import (
    AgenticRequest, AgenticResponse,
    FullStackRequest, FullStackResponse
)
from api_v2.middleware import limiter, RateLimits
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/agentic",
    response_model=AgenticResponse,
    summary="Generate code with agentic system",
    description="Generate HTML/CSS/JS code using multi-agent orchestration"
)
@limiter.limit(RateLimits.GENERATE_AGENTIC)
async def generate_agentic(request: AgenticRequest):
    """
    Generate code using agentic orchestration

    Args:
        request: Generation request with prompt, files, conversation history

    Returns:
        Generated files and metadata

    Rate limit:
        10 requests per minute
    """
    # TODO: Import and use existing agentic logic from server.py
    # This is a placeholder showing the API structure
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint en cours de migration. Utilisez /api/generate/agentic pour l'instant."
    )


@router.post(
    "/fullstack",
    response_model=FullStackResponse,
    summary="Generate full-stack Next.js project",
    description="Generate complete Next.js + TypeScript + Supabase project"
)
@limiter.limit(RateLimits.GENERATE_FULLSTACK)
async def generate_fullstack(request: FullStackRequest):
    """
    Generate full-stack project

    Args:
        request: Full-stack generation request

    Returns:
        Generated project files with stack information

    Rate limit:
        5 requests per minute
    """
    # TODO: Import and use existing fullstack logic from server.py
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint en cours de migration. Utilisez /api/generate/fullstack pour l'instant."
    )
