"""
API v2 Router - Centralized routing with modular endpoints
"""
from fastapi import APIRouter
from .endpoints import auth, projects, generation, billing, admin

# Create main v2 router
api_v2_router = APIRouter(prefix="/v2", tags=["v2"])

# Include sub-routers
api_v2_router.include_router(auth.router, prefix="/auth", tags=["v2-auth"])
api_v2_router.include_router(projects.router, prefix="/projects", tags=["v2-projects"])
api_v2_router.include_router(generation.router, prefix="/generate", tags=["v2-generation"])
api_v2_router.include_router(billing.router, prefix="/billing", tags=["v2-billing"])
api_v2_router.include_router(admin.router, prefix="/admin", tags=["v2-admin"])


@api_v2_router.get("/", summary="API v2 Health Check")
async def api_v2_root():
    """
    Health check endpoint for API v2

    Returns:
        API version, status, and available features
    """
    return {
        "message": "Devora API v2",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "rate-limiting",
            "redis-caching",
            "openapi-spec",
            "type-safety",
            "enhanced-error-handling"
        ],
        "documentation": "/docs"
    }
