"""
RAG (Retrieval-Augmented Generation) Module

Provides:
- Embedding generation for text
- Vector storage and similarity search
- Context retrieval for LLM augmentation
"""

from .embeddings import EmbeddingService
from .vector_store import VectorStore, VectorStoreConfig
from .retriever import ContextRetriever

__all__ = [
    "EmbeddingService",
    "VectorStore",
    "VectorStoreConfig",
    "ContextRetriever",
]
