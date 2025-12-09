"""
Health Check Endpoints for Kubernetes and Load Balancer Probes

Endpoints:
- /health - Comprehensive health check (all dependencies)
- /healthz - Simple liveness probe (is the app running?)
- /readyz - Readiness probe (can the app accept traffic?)
- /metrics - Prometheus metrics endpoint
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import redis
import psutil
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
import logging

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


class ComponentHealth(BaseModel):
    """Health status of a single component."""
    name: str
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthStatus(BaseModel):
    """Overall health status response."""
    status: str  # healthy, degraded, unhealthy
    timestamp: str
    version: str
    uptime_seconds: float
    components: Dict[str, ComponentHealth]


# Track app start time for uptime calculation
APP_START_TIME = datetime.utcnow()


async def check_database(db_engine: AsyncEngine) -> ComponentHealth:
    """Check database connectivity and query performance."""
    start_time = datetime.utcnow()
    try:
        async with db_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()

        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return ComponentHealth(
            name="database",
            status="healthy" if response_time < 100 else "degraded",
            response_time_ms=response_time,
            details={"type": "postgresql"}
        )
    except Exception as e:
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"Database health check failed: {e}")
        return ComponentHealth(
            name="database",
            status="unhealthy",
            response_time_ms=response_time,
            error=str(e)
        )


async def check_redis(redis_client: redis.Redis) -> ComponentHealth:
    """Check Redis connectivity and performance."""
    start_time = datetime.utcnow()
    try:
        await asyncio.get_event_loop().run_in_executor(
            None, redis_client.ping
        )

        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Get Redis info
        info = await asyncio.get_event_loop().run_in_executor(
            None, redis_client.info, "memory"
        )

        return ComponentHealth(
            name="redis",
            status="healthy" if response_time < 50 else "degraded",
            response_time_ms=response_time,
            details={
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        )
    except Exception as e:
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"Redis health check failed: {e}")
        return ComponentHealth(
            name="redis",
            status="unhealthy",
            response_time_ms=response_time,
            error=str(e)
        )


def check_system() -> ComponentHealth:
    """Check system resources (CPU, memory, disk)."""
    start_time = datetime.utcnow()
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Determine status based on resource usage
        status = "healthy"
        if cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
            status = "degraded"
        if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
            status = "unhealthy"

        return ComponentHealth(
            name="system",
            status=status,
            response_time_ms=response_time,
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        )
    except Exception as e:
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"System health check failed: {e}")
        return ComponentHealth(
            name="system",
            status="unhealthy",
            response_time_ms=response_time,
            error=str(e)
        )


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check(
    db_engine: AsyncEngine = Depends(),  # Inject from app state
    redis_client: redis.Redis = Depends()  # Inject from app state
):
    """
    Comprehensive health check endpoint.

    Checks all dependencies (database, Redis, system resources).
    Returns 200 if healthy/degraded, 503 if unhealthy.
    """
    # Run all checks concurrently
    db_health, redis_health, system_health = await asyncio.gather(
        check_database(db_engine),
        check_redis(redis_client),
        asyncio.get_event_loop().run_in_executor(None, check_system),
        return_exceptions=True
    )

    # Handle any exceptions from gather
    if isinstance(db_health, Exception):
        db_health = ComponentHealth(name="database", status="unhealthy", response_time_ms=0, error=str(db_health))
    if isinstance(redis_health, Exception):
        redis_health = ComponentHealth(name="redis", status="unhealthy", response_time_ms=0, error=str(redis_health))
    if isinstance(system_health, Exception):
        system_health = ComponentHealth(name="system", status="unhealthy", response_time_ms=0, error=str(system_health))

    components = {
        "database": db_health,
        "redis": redis_health,
        "system": system_health
    }

    # Determine overall status
    statuses = [c.status for c in components.values()]
    if "unhealthy" in statuses:
        overall_status = "unhealthy"
    elif "degraded" in statuses:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    # Calculate uptime
    uptime = (datetime.utcnow() - APP_START_TIME).total_seconds()

    response = HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=os.getenv("VERSION", "unknown"),
        uptime_seconds=uptime,
        components=components
    )

    # Return 503 if unhealthy
    if overall_status == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.model_dump()
        )

    return response


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def liveness_probe():
    """
    Simple liveness probe for Kubernetes.

    Only checks if the app is running.
    Returns 200 if alive, used for restart decisions.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat() + "Z"}


@router.get("/readyz", status_code=status.HTTP_200_OK)
async def readiness_probe(
    db_engine: AsyncEngine = Depends(),
    redis_client: redis.Redis = Depends()
):
    """
    Readiness probe for Kubernetes.

    Checks if the app can accept traffic (database and Redis connected).
    Returns 200 if ready, 503 if not ready.
    """
    try:
        # Quick database check
        async with db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        # Quick Redis check
        await asyncio.get_event_loop().run_in_executor(
            None, redis_client.ping
        )

        return {"status": "ready", "timestamp": datetime.utcnow().isoformat() + "Z"}

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "error": str(e)}
        )


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format.
    Use with prometheus_client library for full implementation.
    """
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi.responses import Response

        metrics = generate_latest()
        return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)

    except ImportError:
        # Fallback if prometheus_client not installed
        uptime = (datetime.utcnow() - APP_START_TIME).total_seconds()
        system = check_system()

        metrics = f"""# HELP devora_up Service availability
# TYPE devora_up gauge
devora_up 1

# HELP devora_uptime_seconds Service uptime in seconds
# TYPE devora_uptime_seconds counter
devora_uptime_seconds {uptime}

# HELP devora_cpu_usage_percent CPU usage percentage
# TYPE devora_cpu_usage_percent gauge
devora_cpu_usage_percent {system.details.get('cpu_percent', 0)}

# HELP devora_memory_usage_percent Memory usage percentage
# TYPE devora_memory_usage_percent gauge
devora_memory_usage_percent {system.details.get('memory_percent', 0)}
"""
        return Response(content=metrics, media_type="text/plain")
