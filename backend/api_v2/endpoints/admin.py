"""
Admin endpoints (placeholder - uses existing admin routes)
"""
from fastapi import APIRouter
from api_v2.middleware import limiter, RateLimits

router = APIRouter()

# NOTE: Admin endpoints use existing routes_admin.py logic
# This is a placeholder for future V2 migration
