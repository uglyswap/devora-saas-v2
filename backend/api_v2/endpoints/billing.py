"""
Billing endpoints (placeholder - uses existing Stripe service)
"""
from fastapi import APIRouter
from api_v2.middleware import limiter, RateLimits

router = APIRouter()

# NOTE: Billing endpoints use existing routes_billing.py logic
# This is a placeholder for future V2 migration
