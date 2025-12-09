"""
AI Module - Advanced LLM Integration & RAG for Devora

This module provides:
- Multi-provider LLM support (OpenRouter, Anthropic, OpenAI)
- Advanced retry logic with exponential backoff
- Token counting and cost tracking
- Streaming support
- RAG (Retrieval-Augmented Generation) capabilities
- Prompt template management
"""

from .llm_service import LLMService, LLMProvider, LLMConfig
from .cache import ResponseCache
from .rag.embeddings import EmbeddingService
from .rag.vector_store import VectorStore
from .prompts.template_manager import PromptTemplateManager

__all__ = [
    "LLMService",
    "LLMProvider",
    "LLMConfig",
    "ResponseCache",
    "EmbeddingService",
    "VectorStore",
    "PromptTemplateManager",
]
