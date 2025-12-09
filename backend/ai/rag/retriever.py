"""
Context Retriever for RAG

Combines embedding generation and vector search to retrieve
relevant context for LLM augmentation.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .embeddings import EmbeddingService
from .vector_store import VectorStore, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class RetrievedContext:
    """Retrieved context for RAG"""
    text: str
    score: float
    source: str
    metadata: Dict[str, Any]


class ContextRetriever:
    """Retrieve relevant context for RAG"""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        score_threshold: float = 0.7,
        max_context_length: int = 4000,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.score_threshold = score_threshold
        self.max_context_length = max_context_length

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        text_field: str = "text",
        id_field: str = "id",
    ):
        """
        Add documents to the vector store

        Args:
            documents: List of documents to add
            text_field: Field containing the text to embed
            id_field: Field containing the document ID
        """
        if not documents:
            return

        # Extract texts and IDs
        texts = [doc[text_field] for doc in documents]
        ids = [doc[id_field] for doc in documents]

        # Generate embeddings
        logger.info(f"[Retriever] Generating embeddings for {len(documents)} documents...")
        embeddings = await self.embedding_service.embed_batch(texts)

        # Prepare metadata (exclude text and id)
        metadatas = []
        for doc in documents:
            metadata = {k: v for k, v in doc.items() if k not in [text_field, id_field]}
            metadatas.append(metadata)

        # Add to vector store
        await self.vector_store.add_batch(ids, texts, embeddings, metadatas)

        logger.info(f"[Retriever] Added {len(documents)} documents to vector store")

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_scores: bool = False,
    ) -> List[RetrievedContext]:
        """
        Retrieve relevant context for a query

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            include_scores: Whether to include similarity scores

        Returns:
            List of retrieved contexts
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query)

        # Search vector store
        results = await self.vector_store.search(
            query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
        )

        # Filter by score threshold
        filtered_results = [r for r in results if r.score >= self.score_threshold]

        # Convert to RetrievedContext
        contexts = []
        for result in filtered_results:
            contexts.append(RetrievedContext(
                text=result.text,
                score=result.score,
                source=result.id,
                metadata=result.metadata,
            ))

        logger.info(
            f"[Retriever] Retrieved {len(contexts)} contexts "
            f"(from {len(results)} total results)"
        )

        return contexts

    def format_context(
        self,
        contexts: List[RetrievedContext],
        include_sources: bool = True,
    ) -> str:
        """
        Format retrieved contexts into a single string for LLM

        Args:
            contexts: Retrieved contexts
            include_sources: Whether to include source references

        Returns:
            Formatted context string
        """
        if not contexts:
            return ""

        formatted_parts = []
        current_length = 0

        for i, ctx in enumerate(contexts, 1):
            # Build context block
            if include_sources:
                context_block = f"[Source {i}: {ctx.source}]\n{ctx.text}\n"
            else:
                context_block = f"{ctx.text}\n"

            # Check if adding this would exceed max length
            block_length = len(context_block)
            if current_length + block_length > self.max_context_length:
                break

            formatted_parts.append(context_block)
            current_length += block_length

        return "\n".join(formatted_parts)

    async def retrieve_and_format(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_sources: bool = True,
    ) -> str:
        """
        Retrieve and format context in one step

        Args:
            query: Search query
            top_k: Number of results to retrieve
            filter_metadata: Optional metadata filter
            include_sources: Whether to include source references

        Returns:
            Formatted context string ready for LLM
        """
        contexts = await self.retrieve(query, top_k, filter_metadata)
        return self.format_context(contexts, include_sources)

    async def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics"""
        embedding_stats = self.embedding_service.get_stats()
        vector_stats = await self.vector_store.get_stats()

        return {
            "embedding_stats": embedding_stats,
            "vector_store_stats": vector_stats,
            "score_threshold": self.score_threshold,
            "max_context_length": self.max_context_length,
        }
