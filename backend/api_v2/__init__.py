"""
Devora API v2 - Modern REST API Architecture
Features:
- Rate limiting
- Redis caching
- Comprehensive error handling
- OpenAPI documentation
- Type-safe schemas
"""
from .router import api_v2_router

__all__ = ["api_v2_router"]
