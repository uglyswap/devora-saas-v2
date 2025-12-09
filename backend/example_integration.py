"""
Example Integration - Data Squad Features
==========================================
Exemples d'intégration des fonctionnalités analytics, search et RAG
dans une application FastAPI existante.
"""

import asyncpg
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel

# Imports Data Squad
from analytics import (
    get_posthog_client,
    get_metrics_service,
    track_event,
    EventType,
    track_project_created,
    track_code_generation
)
from search import (
    get_search_service,
    get_rag_pipeline,
    get_embedding_service,
    SearchType
)

# ============================================================================
# Setup Application
# ============================================================================

app = FastAPI(title="Devora API with Data Squad")

# PostgreSQL connection pool
@app.on_event("startup")
async def startup():
    """Initialize database pool and services"""
    app.state.db_pool = await asyncpg.create_pool(
        "postgresql://devora_user:password@localhost/devora_db",
        min_size=5,
        max_size=20
    )

    # Initialize services (singletons)
    app.state.posthog = get_posthog_client(app.state.db_pool)
    app.state.metrics = get_metrics_service(app.state.db_pool)
    app.state.search = get_search_service(app.state.db_pool)
    app.state.rag = get_rag_pipeline(app.state.db_pool)
    app.state.embeddings = get_embedding_service(app.state.db_pool)

    print("✅ Data Squad services initialized")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if hasattr(app.state, 'posthog'):
        app.state.posthog.shutdown()

    if hasattr(app.state, 'db_pool'):
        await app.state.db_pool.close()


# Dependency pour récupérer le pool
async def get_db_pool():
    return app.state.db_pool


# Mock user dependency (remplacer par votre vrai auth)
async def get_current_user():
    return {"id": "user-uuid-123", "email": "user@example.com"}


# ============================================================================
# Example 1: Analytics Integration
# ============================================================================

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    project_type: str


@app.post("/api/projects")
async def create_project(
    data: ProjectCreate,
    user=Depends(get_current_user),
    db_pool=Depends(get_db_pool)
):
    """
    Créer un projet avec tracking analytics automatique
    """
    async with db_pool.acquire() as conn:
        # 1. Créer le projet en DB
        project_id = await conn.fetchval('''
            INSERT INTO projects (user_id, name, description, project_type)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        ''', user['id'], data.name, data.description, data.project_type)

        # 2. Track l'événement dans PostHog
        track_project_created(
            user_id=user['id'],
            project_id=str(project_id),
            project_name=data.name,
            project_type=data.project_type
        )

        # 3. Générer embedding pour recherche sémantique (async, non-blocking)
        import asyncio
        asyncio.create_task(
            app.state.embeddings.embed_project(str(project_id))
        )

        return {
            "id": str(project_id),
            "name": data.name,
            "message": "Project created and indexed for search"
        }


@app.post("/api/chat")
async def chat_with_ai(
    message: str,
    conversation_id: Optional[str] = None,
    user=Depends(get_current_user)
):
    """
    Chat avec AI en utilisant RAG pour contexte
    """
    # 1. Utiliser RAG pour augmenter le prompt
    augmented_prompt, rag_response = await app.state.rag.augment_query(
        query=message,
        user_id=user['id'],
        conversation_id=conversation_id,
        max_context_tokens=2000
    )

    # 2. Appeler votre LLM (OpenAI, Anthropic, etc.)
    # ai_response = await call_your_llm(augmented_prompt)
    ai_response = f"[Mock AI response using {rag_response.total_contexts} contexts]"

    # 3. Track l'événement
    track_event(
        EventType.CHAT_MESSAGE_SENT,
        user_id=user['id'],
        properties={
            "message_length": len(message),
            "contexts_used": rag_response.total_contexts,
            "retrieval_time_ms": rag_response.retrieval_time_ms,
            "conversation_id": conversation_id
        }
    )

    return {
        "response": ai_response,
        "contexts_used": rag_response.total_contexts,
        "sources": [
            {
                "type": ctx.source_type,
                "id": ctx.source_id,
                "relevance": ctx.relevance_score
            }
            for ctx in rag_response.contexts
        ]
    }


# ============================================================================
# Example 2: Search Integration
# ============================================================================

@app.get("/api/search")
async def search(
    q: str = Query(..., description="Search query"),
    type: SearchType = Query(SearchType.ALL, description="Search type"),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(get_current_user)
):
    """
    Recherche full-text avec ranking
    """
    # Effectuer la recherche
    results = await app.state.search.search(
        query=q,
        user_id=user['id'],
        search_type=type,
        limit=limit
    )

    # Track la recherche
    track_event(
        EventType.SEARCH_PERFORMED,
        user_id=user['id'],
        properties={
            "query": q,
            "search_type": type.value,
            "results_count": results.total_count,
            "execution_time_ms": results.execution_time_ms
        }
    )

    return {
        "query": q,
        "results": [
            {
                "type": r.entity_type,
                "id": r.entity_id,
                "title": r.title,
                "snippet": r.snippet,
                "score": r.score,
                "metadata": r.metadata,
                "created_at": r.created_at.isoformat()
            }
            for r in results.results
        ],
        "total": results.total_count,
        "execution_time_ms": results.execution_time_ms
    }


@app.get("/api/search/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=2),
    user=Depends(get_current_user)
):
    """
    Autocomplete pour recherche
    """
    suggestions = await app.state.search.get_search_suggestions(
        query=q,
        user_id=user['id'],
        limit=5
    )

    return {"suggestions": suggestions}


@app.get("/api/search/semantic")
async def semantic_search(
    q: str = Query(..., description="Semantic search query"),
    limit: int = Query(10, ge=1, le=50),
    user=Depends(get_current_user)
):
    """
    Recherche sémantique par similarité vectorielle
    """
    results = await app.state.embeddings.semantic_search(
        query_text=q,
        entity_types=['project', 'conversation', 'message'],
        limit=limit,
        similarity_threshold=0.7
    )

    return {
        "query": q,
        "results": results,
        "total": len(results)
    }


# ============================================================================
# Example 3: Admin Dashboard avec Metrics
# ============================================================================

@app.get("/api/admin/dashboard")
async def admin_dashboard(
    user=Depends(get_current_user)  # Add admin check in production
):
    """
    Dashboard complet pour admin
    """
    # Récupérer toutes les métriques
    dashboard = await app.state.metrics.get_dashboard_metrics()

    return {
        "generated_at": dashboard.generated_at.isoformat(),
        "users": {
            "total": dashboard.user_metrics.total_users,
            "active_today": dashboard.user_metrics.active_users_today,
            "active_week": dashboard.user_metrics.active_users_week,
            "active_month": dashboard.user_metrics.active_users_month,
            "new_today": dashboard.user_metrics.new_users_today,
            "new_week": dashboard.user_metrics.new_users_week,
            "new_month": dashboard.user_metrics.new_users_month,
            "churned_month": dashboard.user_metrics.churned_users_month,
            "retention_30d": dashboard.user_metrics.retention_rate_30d
        },
        "revenue": {
            "total": float(dashboard.revenue_metrics.total_revenue),
            "today": float(dashboard.revenue_metrics.revenue_today),
            "week": float(dashboard.revenue_metrics.revenue_week),
            "month": float(dashboard.revenue_metrics.revenue_month),
            "last_month": float(dashboard.revenue_metrics.revenue_last_month),
            "mrr": float(dashboard.revenue_metrics.mrr),
            "arr": float(dashboard.revenue_metrics.arr),
            "arpu": float(dashboard.revenue_metrics.average_revenue_per_user),
            "ltv": float(dashboard.revenue_metrics.lifetime_value)
        },
        "engagement": {
            "total_projects": dashboard.engagement_metrics.total_projects,
            "projects_today": dashboard.engagement_metrics.projects_created_today,
            "projects_week": dashboard.engagement_metrics.projects_created_week,
            "projects_month": dashboard.engagement_metrics.projects_created_month,
            "total_conversations": dashboard.engagement_metrics.total_conversations,
            "total_messages": dashboard.engagement_metrics.total_messages,
            "avg_messages_per_conversation": dashboard.engagement_metrics.average_messages_per_conversation,
            "avg_projects_per_user": dashboard.engagement_metrics.average_projects_per_user,
            "avg_session_duration_min": dashboard.engagement_metrics.average_session_duration_minutes
        },
        "performance": {
            "avg_query_time_ms": dashboard.performance_metrics.average_query_time_ms,
            "slow_queries": dashboard.performance_metrics.slow_queries_count,
            "error_rate": dashboard.performance_metrics.error_rate,
            "api_p95_ms": dashboard.performance_metrics.api_response_time_p95,
            "successful_deployments": dashboard.performance_metrics.successful_deployments,
            "failed_deployments": dashboard.performance_metrics.failed_deployments,
            "deployment_success_rate": dashboard.performance_metrics.deployment_success_rate
        }
    }


@app.get("/api/admin/metrics/cohort/{cohort_date}")
async def cohort_retention(
    cohort_date: date,
    period_days: int = Query(30, ge=1, le=90),
    user=Depends(get_current_user)
):
    """
    Analyse de cohorte pour une date donnée
    """
    retention = await app.state.metrics.get_cohort_retention(
        cohort_date=cohort_date,
        period_days=period_days
    )

    return retention


# ============================================================================
# Example 4: Feature Flags avec PostHog
# ============================================================================

@app.get("/api/features/{feature_key}")
async def check_feature_flag(
    feature_key: str,
    user=Depends(get_current_user)
):
    """
    Vérifier si une feature flag est activée pour l'utilisateur
    """
    is_enabled = app.state.posthog.feature_enabled(
        key=feature_key,
        distinct_id=user['id'],
        default=False
    )

    # Get variant (for multivariate flags)
    variant = app.state.posthog.get_feature_flag(
        key=feature_key,
        distinct_id=user['id']
    )

    return {
        "feature": feature_key,
        "enabled": is_enabled,
        "variant": variant
    }


# ============================================================================
# Example 5: User Identification (PostHog)
# ============================================================================

@app.post("/api/auth/login")
async def login(email: str, password: str):
    """
    Login avec identification PostHog
    """
    # 1. Authentifier l'utilisateur (votre logique)
    user = {"id": "user-uuid-123", "email": email}

    # 2. Identifier dans PostHog avec traits
    app.state.posthog.identify(
        distinct_id=user['id'],
        properties={
            "email": user['email'],
            "name": user.get('full_name'),
            "subscription_status": user.get('subscription_status'),
            "created_at": user.get('created_at'),
            "is_admin": user.get('is_admin', False)
        }
    )

    # 3. Track login event
    track_event(
        EventType.USER_LOGGED_IN,
        user_id=user['id'],
        properties={
            "login_method": "email",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    return {"user": user, "token": "jwt-token-here"}


# ============================================================================
# Example 6: Error Tracking
# ============================================================================

from analytics.events import track_error

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """
    Capturer et tracker toutes les erreurs
    """
    import traceback

    # Track error dans PostHog
    track_error(
        user_id=None,  # Ou extraire de request.state.user si disponible
        error_type=type(exc).__name__,
        error_message=str(exc),
        stack_trace=traceback.format_exc(),
        context={
            "path": str(request.url),
            "method": request.method,
            "client": request.client.host if request.client else None
        }
    )

    return {
        "error": "Internal server error",
        "message": str(exc) if app.debug else "An error occurred"
    }


# ============================================================================
# Example 7: Background Task - Generate Embeddings
# ============================================================================

from fastapi import BackgroundTasks

@app.post("/api/projects/{project_id}/reindex")
async def reindex_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    """
    Régénérer l'embedding d'un projet (pour améliorer la recherche)
    """
    # Lancer en background
    background_tasks.add_task(
        app.state.embeddings.embed_project,
        project_id
    )

    return {
        "message": "Reindexing started",
        "project_id": project_id
    }


@app.post("/api/admin/reindex-all")
async def reindex_all_projects(
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
    db_pool=Depends(get_db_pool)
):
    """
    Régénérer tous les embeddings (admin only)
    """
    async def reindex_task():
        async with db_pool.acquire() as conn:
            projects = await conn.fetch(
                "SELECT id FROM projects WHERE deleted_at IS NULL"
            )

            for project in projects:
                result = await app.state.embeddings.embed_project(
                    str(project['id'])
                )
                print(f"Project {project['id']}: {'✓' if result.success else '✗'}")

    background_tasks.add_task(reindex_task)

    return {"message": "Reindexing all projects started"}


# ============================================================================
# Example 8: Health Check
# ============================================================================

@app.get("/health")
async def health_check(db_pool=Depends(get_db_pool)):
    """
    Health check avec vérification de tous les services
    """
    health = {
        "status": "healthy",
        "services": {}
    }

    # Check PostgreSQL
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        health["services"]["postgresql"] = "ok"
    except Exception as e:
        health["services"]["postgresql"] = f"error: {str(e)}"
        health["status"] = "unhealthy"

    # Check PostHog
    health["services"]["posthog"] = "ok" if app.state.posthog.enabled else "disabled"

    # Check Embeddings (OpenAI)
    health["services"]["embeddings"] = "ok" if app.state.embeddings.enabled else "disabled"

    return health


# ============================================================================
# Example 9: Utilisation Avancée du RAG
# ============================================================================

@app.post("/api/ai/ask")
async def ask_ai_with_context(
    question: str,
    context_types: List[str] = Query(
        default=['project', 'conversation'],
        description="Types de contexte à inclure"
    ),
    user=Depends(get_current_user)
):
    """
    Poser une question à l'IA avec contexte intelligent
    """
    # 1. Récupérer contexte via RAG
    rag_response = await app.state.rag.retrieve_context(
        query=question,
        user_id=user['id'],
        max_contexts=5,
        use_semantic=True,
        use_keyword=True,
        semantic_weight=0.7  # 70% semantic, 30% keyword
    )

    # 2. Formatter le contexte pour le prompt
    context_text = app.state.rag.format_context_for_prompt(
        rag_response.contexts,
        max_tokens=2000
    )

    # 3. Construire le prompt complet
    full_prompt = f"""{context_text}

# User Question
{question}

# Instructions
Answer the question using the provided context about the user's projects and conversations.
Be specific and reference the sources when possible.
"""

    # 4. Appeler votre LLM
    # ai_response = await your_llm_call(full_prompt)

    return {
        "question": question,
        "contexts_found": rag_response.total_contexts,
        "retrieval_time_ms": rag_response.retrieval_time_ms,
        "sources": [
            {
                "type": ctx.source_type,
                "relevance": ctx.relevance_score,
                "preview": ctx.text[:200]
            }
            for ctx in rag_response.contexts
        ],
        # "answer": ai_response
        "answer": "[Mock AI answer using retrieved context]"
    }


# ============================================================================
# Example 10: Analytics Webhook (PostHog → Your App)
# ============================================================================

@app.post("/webhooks/posthog")
async def posthog_webhook(payload: dict):
    """
    Recevoir des webhooks de PostHog pour actions automatisées

    Exemples d'usage:
    - Envoyer email quand user atteint un milestone
    - Déclencher onboarding automatique
    - Alertes pour comportements anormaux
    """
    event_name = payload.get('event')
    properties = payload.get('properties', {})
    distinct_id = payload.get('distinct_id')

    # Exemple: Détection de churn
    if event_name == 'subscription_canceled':
        # Envoyer email de win-back
        print(f"User {distinct_id} canceled subscription - send win-back email")

    # Exemple: Milestone atteint
    if event_name == 'project_created':
        project_count = properties.get('total_projects', 0)
        if project_count == 10:
            # Badge ou email de félicitations
            print(f"User {distinct_id} created 10 projects - send milestone email")

    return {"status": "processed"}


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
