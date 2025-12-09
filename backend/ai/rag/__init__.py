"""
RAG (Retrieval-Augmented Generation) Module

Provides:
- Embedding generation for text (OpenRouter, OpenAI, local)
- Vector storage and similarity search
- Document loading and chunking
- RAG Engine for context retrieval and prompt augmentation
"""

from .embeddings import EmbeddingService, EmbeddingsService, EmbeddingProvider, quick_embed
from .vector_store import VectorStore, VectorStoreConfig, VectorStoreType, SearchResult, InMemoryVectorStore
from .retriever import ContextRetriever, RetrievedContext
from .document_loader import DocumentLoader, Document, Chunk, ChunkConfig, DocumentType, load_and_chunk_files
from .rag_engine import RAGEngine, RAGConfig, RAGSource, create_rag_engine

__all__ = [
    # Embeddings
    "EmbeddingService",
    "EmbeddingsService",
    "EmbeddingProvider",
    "quick_embed",
    # Vector Store
    "VectorStore",
    "VectorStoreConfig",
    "VectorStoreType",
    "SearchResult",
    "InMemoryVectorStore",
    # Retriever
    "ContextRetriever",
    "RetrievedContext",
    # Document Loader
    "DocumentLoader",
    "Document",
    "Chunk",
    "ChunkConfig",
    "DocumentType",
    "load_and_chunk_files",
    # RAG Engine
    "RAGEngine",
    "RAGConfig",
    "RAGSource",
    "create_rag_engine",
]
