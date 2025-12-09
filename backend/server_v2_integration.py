"""
Example integration of API V2 into existing server.py

Add this code to your server.py to enable V2 endpoints
"""

# ========================================
# STEP 1: Add imports at the top
# ========================================
from api_v2 import api_v2_router
from api_v2.middleware import limiter, rate_limit_exceeded_handler
from api_v2.middleware.cache import init_redis_cache
from slowapi.errors import RateLimitExceeded
import os

# ========================================
# STEP 2: After app = FastAPI(), add:
# ========================================

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Initialize Redis cache (optional but recommended)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    init_redis_cache(redis_url)
    logging.info(f"Redis cache initialized: {redis_url}")
except Exception as e:
    logging.warning(f"Redis cache initialization failed: {e}. Running without cache.")

# ========================================
# STEP 3: Include V2 router (before or after existing routers)
# ========================================

# Include API v2 router
app.include_router(api_v2_router, prefix="/api")
logging.info("API v2 router registered at /api/v2/*")

# Existing routers
app.include_router(auth_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(support_router, prefix="/api")
app.include_router(api_router)  # Legacy routes

# ========================================
# STEP 4: Update root endpoint to show V2
# ========================================

@api_router.get("/")
async def root():
    return {
        "message": "Devora API",
        "status": "running",
        "version": "3.2.0",  # Increment version
        "api_versions": {
            "v1": "/api/*",
            "v2": "/api/v2/*"  # NEW
        },
        "features": [
            "openrouter",
            "agentic",
            "fullstack",
            "github-export",
            "vercel-deploy",
            "persistent-memory" if MEMORY_ENABLED else "memory-disabled",
            "rate-limiting",  # NEW
            "redis-caching",  # NEW
            "oauth2"  # NEW
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "spec": "/openapi.yaml"  # Static file
        }
    }

# ========================================
# STEP 5: Add environment variables to .env
# ========================================

"""
# Add to .env file:

# Redis Cache (optional but recommended)
REDIS_URL=redis://localhost:6379/0

# OAuth2 - Google
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# OAuth2 - GitHub
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback
"""

# ========================================
# STEP 6: Test the integration
# ========================================

"""
# Start server
uvicorn server:app --reload

# Test endpoints
curl http://localhost:8000/api/v2/
# Should return: {"message": "Devora API v2", "version": "2.0.0", ...}

# Test rate limiting
for i in {1..6}; do curl http://localhost:8000/api/v2/auth/login; done
# 6th request should return 429 Too Many Requests

# Test OpenAPI docs
open http://localhost:8000/docs
# Should show all v2 endpoints under "v2-*" tags
"""

# ========================================
# STEP 7: Generate TypeScript types
# ========================================

"""
# Generate types for frontend
python generate_typescript_types.py

# Copy to frontend
cp devora-api-types.ts ../frontend/src/types/

# Use in frontend
import { UserResponse, ProjectResponse } from '@/types/devora-api-types';
"""

# ========================================
# COMPLETE EXAMPLE: Full server.py integration
# ========================================

"""
# server.py (with V2 integration)

from fastapi import FastAPI, APIRouter, HTTPException, Body, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
from config import settings

# V2 imports
from api_v2 import api_v2_router
from api_v2.middleware import limiter, rate_limit_exceeded_handler
from api_v2.middleware.cache import init_redis_cache
from slowapi.errors import RateLimitExceeded

# Existing imports
from routes_auth import router as auth_router
from routes_billing import router as billing_router
from routes_admin import router as admin_router
from routes_support import router as support_router
from auth import get_current_user

# MongoDB connection
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

# Create app
app = FastAPI(
    title="Devora API",
    description="AI-powered code generation platform",
    version="3.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

api_router = APIRouter(prefix="/api")

# Configure rate limiting (V2)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Initialize Redis cache (V2)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    init_redis_cache(redis_url)
    logging.info(f"Redis initialized: {redis_url}")
except Exception as e:
    logging.warning(f"Redis init failed: {e}")

# ... (rest of your existing code: models, routes, etc.)

# Include routers
app.include_router(api_v2_router, prefix="/api")  # V2 first
app.include_router(auth_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(support_router, prefix="/api")
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Configure for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Run with: uvicorn server:app --reload --port 8000
"""
