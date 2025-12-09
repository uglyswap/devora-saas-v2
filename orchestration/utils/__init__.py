"""
Utilitaires pour l'orchestration Devora.

Fournit les composants de base pour la gestion LLM, logging, tokens et progression.
"""

from .llm_client import (
    LLMClient,
    LLMConfig,
    LLMResponse,
    ModelType,
    RateLimitError,
    create_llm_client,
)
from .logger import (
    StructuredLogger,
    LogLevel,
    Colors,
    setup_logger,
    get_logger,
    default_logger,
)
from .token_manager import (
    TokenManager,
    TokenUsage,
    CompressionResult,
    ModelTokenLimits,
    default_token_manager,
    count_tokens,
)
from .progress_emitter import (
    ProgressEmitter,
    ProgressEvent,
    EventType,
    EventPriority,
    default_emitter,
    emit_event,
)

__all__ = [
    # LLM Client
    "LLMClient",
    "LLMConfig",
    "LLMResponse",
    "ModelType",
    "RateLimitError",
    "create_llm_client",
    # Logger
    "StructuredLogger",
    "LogLevel",
    "Colors",
    "setup_logger",
    "get_logger",
    "default_logger",
    # Token Manager
    "TokenManager",
    "TokenUsage",
    "CompressionResult",
    "ModelTokenLimits",
    "default_token_manager",
    "count_tokens",
    # Progress Emitter
    "ProgressEmitter",
    "ProgressEvent",
    "EventType",
    "EventPriority",
    "default_emitter",
    "emit_event",
]

__version__ = "0.1.0"
