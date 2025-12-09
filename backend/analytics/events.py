"""
Analytics Events Definition
============================
Centralized event tracking schema for Devora
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from .posthog_client import get_posthog_client


class EventType(str, Enum):
    """Standardized event types for analytics"""

    # User lifecycle
    USER_SIGNED_UP = "user_signed_up"
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGGED_OUT = "user_logged_out"
    USER_UPDATED_PROFILE = "user_updated_profile"

    # Subscription & billing
    SUBSCRIPTION_STARTED = "subscription_started"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    SUBSCRIPTION_CANCELED = "subscription_canceled"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDED = "trial_ended"

    # Project management
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    PROJECT_EXPORTED = "project_exported"
    PROJECT_DEPLOYED = "project_deployed"

    # Code generation
    CODE_GENERATED = "code_generated"
    CODE_REGENERATED = "code_regenerated"
    CODE_EDITED = "code_edited"
    FILE_CREATED = "file_created"
    FILE_DELETED = "file_deleted"

    # AI interactions
    CHAT_MESSAGE_SENT = "chat_message_sent"
    AI_RESPONSE_RECEIVED = "ai_response_received"
    CONVERSATION_STARTED = "conversation_started"
    CONVERSATION_DELETED = "conversation_deleted"

    # Integrations
    GITHUB_CONNECTED = "github_connected"
    GITHUB_PUSH_SUCCEEDED = "github_push_succeeded"
    GITHUB_PUSH_FAILED = "github_push_failed"
    VERCEL_CONNECTED = "vercel_connected"
    VERCEL_DEPLOY_SUCCEEDED = "vercel_deploy_succeeded"
    VERCEL_DEPLOY_FAILED = "vercel_deploy_failed"

    # Search & discovery
    SEARCH_PERFORMED = "search_performed"
    SEARCH_RESULT_CLICKED = "search_result_clicked"

    # Errors & issues
    ERROR_OCCURRED = "error_occurred"
    API_ERROR = "api_error"
    RATE_LIMIT_HIT = "rate_limit_hit"

    # Feature usage
    FEATURE_USED = "feature_used"
    TEMPLATE_USED = "template_used"
    AGENT_INVOKED = "agent_invoked"


def track_event(
    event: EventType,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    distinct_id: Optional[str] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Track an analytics event

    Args:
        event: Event type from EventType enum
        user_id: Database user ID
        properties: Additional event properties
        distinct_id: PostHog distinct ID (defaults to user_id)
        session_id: Session identifier
        ip_address: User IP address
        user_agent: User agent string

    Returns:
        bool: True if event was tracked successfully

    Example:
        >>> track_event(
        ...     EventType.PROJECT_CREATED,
        ...     user_id="123",
        ...     properties={
        ...         "project_name": "My App",
        ...         "project_type": "saas"
        ...     }
        ... )
    """
    client = get_posthog_client()

    return client.capture(
        distinct_id=distinct_id or user_id,
        event=event.value,
        properties=properties or {},
        user_id=user_id,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


# Convenience functions for common events

def track_user_signup(
    user_id: str,
    email: str,
    signup_source: Optional[str] = None,
    **kwargs
) -> bool:
    """Track user sign up event"""
    return track_event(
        EventType.USER_SIGNED_UP,
        user_id=user_id,
        properties={
            "email": email,
            "signup_source": signup_source,
            **kwargs
        }
    )


def track_project_created(
    user_id: str,
    project_id: str,
    project_name: str,
    project_type: Optional[str] = None,
    **kwargs
) -> bool:
    """Track project creation"""
    return track_event(
        EventType.PROJECT_CREATED,
        user_id=user_id,
        properties={
            "project_id": project_id,
            "project_name": project_name,
            "project_type": project_type,
            **kwargs
        }
    )


def track_code_generation(
    user_id: str,
    project_id: str,
    model: str,
    tokens_used: Optional[int] = None,
    generation_time_ms: Optional[int] = None,
    **kwargs
) -> bool:
    """Track code generation event"""
    return track_event(
        EventType.CODE_GENERATED,
        user_id=user_id,
        properties={
            "project_id": project_id,
            "model": model,
            "tokens_used": tokens_used,
            "generation_time_ms": generation_time_ms,
            **kwargs
        }
    )


def track_subscription_event(
    event_type: EventType,
    user_id: str,
    subscription_id: str,
    plan: str,
    amount: Optional[float] = None,
    **kwargs
) -> bool:
    """Track subscription-related events"""
    return track_event(
        event_type,
        user_id=user_id,
        properties={
            "subscription_id": subscription_id,
            "plan": plan,
            "amount": amount,
            **kwargs
        }
    )


def track_error(
    user_id: Optional[str],
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Track error occurrence"""
    return track_event(
        EventType.ERROR_OCCURRED,
        user_id=user_id or "anonymous",
        properties={
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context,
            **kwargs
        }
    )


def track_feature_usage(
    user_id: str,
    feature_name: str,
    feature_context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Track feature usage"""
    return track_event(
        EventType.FEATURE_USED,
        user_id=user_id,
        properties={
            "feature_name": feature_name,
            "feature_context": feature_context,
            **kwargs
        }
    )
