"""
RAG Pipeline
============
Retrieval-Augmented Generation for contextual AI assistance
"""

import asyncpg
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass
from .embeddings import EmbeddingService, get_embedding_service
from .search_service import SearchService, get_search_service

logger = logging.getLogger(__name__)


@dataclass
class RAGContext:
    """Context retrieved for RAG"""
    text: str
    source_type: str
    source_id: str
    relevance_score: float
    metadata: Dict[str, Any]


@dataclass
class RAGResponse:
    """RAG pipeline response"""
    contexts: List[RAGContext]
    total_contexts: int
    query: str
    retrieval_time_ms: int


class RAGPipeline:
    """
    Retrieval-Augmented Generation Pipeline

    Features:
    - Hybrid search (semantic + keyword)
    - Context ranking and filtering
    - Conversation history integration
    - Source attribution
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        embedding_service: Optional[EmbeddingService] = None,
        search_service: Optional[SearchService] = None
    ):
        self.db_pool = db_pool
        self.embedding_service = embedding_service or get_embedding_service(db_pool)
        self.search_service = search_service or get_search_service(db_pool)

    async def retrieve_context(
        self,
        query: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        max_contexts: int = 5,
        use_semantic: bool = True,
        use_keyword: bool = True,
        semantic_weight: float = 0.6
    ) -> RAGResponse:
        """
        Retrieve relevant context for a query

        Args:
            query: User query
            user_id: User ID for filtering
            conversation_id: Optional conversation context
            max_contexts: Maximum context chunks
            use_semantic: Use semantic search
            use_keyword: Use keyword search
            semantic_weight: Weight for semantic vs keyword (0-1)

        Returns:
            RAGResponse with retrieved contexts
        """
        start_time = datetime.now()

        contexts = []

        # 1. Semantic search (if enabled)
        semantic_results = []
        if use_semantic:
            try:
                semantic_results = await self.embedding_service.semantic_search(
                    query_text=query,
                    entity_types=['project', 'conversation', 'message', 'file'],
                    limit=max_contexts * 2,
                    similarity_threshold=0.6
                )
            except Exception as e:
                logger.error(f"Semantic search failed: {e}")

        # 2. Keyword search (if enabled)
        keyword_results = []
        if use_keyword:
            try:
                search_response = await self.search_service.search_all(
                    query=query,
                    user_id=user_id,
                    limit=max_contexts * 2
                )
                keyword_results = search_response.results
            except Exception as e:
                logger.error(f"Keyword search failed: {e}")

        # 3. Merge and rank results
        merged_contexts = await self._merge_results(
            semantic_results,
            keyword_results,
            semantic_weight,
            user_id
        )

        # 4. Add conversation context if available
        if conversation_id:
            conv_context = await self._get_conversation_context(
                conversation_id,
                max_messages=3
            )
            if conv_context:
                merged_contexts.insert(0, conv_context)

        # 5. Limit to max_contexts
        merged_contexts = merged_contexts[:max_contexts]

        retrieval_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return RAGResponse(
            contexts=merged_contexts,
            total_contexts=len(merged_contexts),
            query=query,
            retrieval_time_ms=retrieval_time_ms
        )

    async def _merge_results(
        self,
        semantic_results: List[Dict[str, Any]],
        keyword_results: List[Any],
        semantic_weight: float,
        user_id: str
    ) -> List[RAGContext]:
        """Merge and rank semantic + keyword results"""
        # Track entities we've seen
        seen_entities = set()
        merged = []

        # Process semantic results
        for result in semantic_results:
            entity_key = f"{result['entity_type']}:{result['entity_id']}"

            if entity_key not in seen_entities:
                seen_entities.add(entity_key)

                # Get full entity data
                entity_data = await self._fetch_entity_data(
                    result['entity_type'],
                    result['entity_id']
                )

                if entity_data:
                    merged.append(RAGContext(
                        text=entity_data['text'],
                        source_type=result['entity_type'],
                        source_id=result['entity_id'],
                        relevance_score=result['similarity'] * semantic_weight,
                        metadata=entity_data['metadata']
                    ))

        # Process keyword results
        keyword_weight = 1.0 - semantic_weight
        for result in keyword_results:
            entity_key = f"{result.entity_type}:{result.entity_id}"

            if entity_key not in seen_entities:
                seen_entities.add(entity_key)

                # Get full entity data
                entity_data = await self._fetch_entity_data(
                    result.entity_type,
                    result.entity_id
                )

                if entity_data:
                    merged.append(RAGContext(
                        text=entity_data['text'],
                        source_type=result.entity_type,
                        source_id=result.entity_id,
                        relevance_score=result.score * keyword_weight,
                        metadata=entity_data['metadata']
                    ))
            else:
                # Entity already in results from semantic search
                # Boost its score
                for context in merged:
                    if f"{context.source_type}:{context.source_id}" == entity_key:
                        context.relevance_score += result.score * keyword_weight * 0.5
                        break

        # Sort by relevance score
        merged.sort(key=lambda x: x.relevance_score, reverse=True)

        return merged

    async def _fetch_entity_data(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch full entity data for context"""
        async with self.db_pool.acquire() as conn:
            try:
                if entity_type == 'project':
                    row = await conn.fetchrow('''
                        SELECT
                            name,
                            description,
                            project_type,
                            created_at
                        FROM projects
                        WHERE id = $1
                    ''', entity_id)

                    if row:
                        return {
                            'text': f"Project: {row['name']}\n{row['description'] or ''}",
                            'metadata': {
                                'name': row['name'],
                                'type': row['project_type'],
                                'created_at': row['created_at'].isoformat()
                            }
                        }

                elif entity_type == 'conversation':
                    row = await conn.fetchrow('''
                        SELECT
                            title,
                            created_at
                        FROM conversations
                        WHERE id = $1
                    ''', entity_id)

                    if row:
                        # Get recent messages
                        messages = await conn.fetch('''
                            SELECT content, role
                            FROM messages
                            WHERE conversation_id = $1
                            ORDER BY timestamp DESC
                            LIMIT 5
                        ''', entity_id)

                        text = f"Conversation: {row['title']}\n"
                        text += "\n".join([
                            f"{msg['role']}: {msg['content'][:200]}"
                            for msg in messages
                        ])

                        return {
                            'text': text,
                            'metadata': {
                                'title': row['title'],
                                'message_count': len(messages),
                                'created_at': row['created_at'].isoformat()
                            }
                        }

                elif entity_type == 'message':
                    row = await conn.fetchrow('''
                        SELECT
                            m.content,
                            m.role,
                            m.timestamp,
                            c.title as conversation_title
                        FROM messages m
                        JOIN conversations c ON m.conversation_id = c.id
                        WHERE m.id = $1
                    ''', entity_id)

                    if row:
                        return {
                            'text': f"{row['role']}: {row['content']}",
                            'metadata': {
                                'role': row['role'],
                                'conversation': row['conversation_title'],
                                'timestamp': row['timestamp'].isoformat()
                            }
                        }

                elif entity_type == 'file':
                    row = await conn.fetchrow('''
                        SELECT
                            pf.name,
                            pf.content,
                            pf.language,
                            p.name as project_name
                        FROM project_files pf
                        JOIN projects p ON pf.project_id = p.id
                        WHERE pf.id = $1
                    ''', entity_id)

                    if row:
                        return {
                            'text': f"File: {row['name']}\n{row['content'][:1000]}",
                            'metadata': {
                                'filename': row['name'],
                                'language': row['language'],
                                'project': row['project_name']
                            }
                        }

            except Exception as e:
                logger.error(f"Error fetching entity data: {e}")

        return None

    async def _get_conversation_context(
        self,
        conversation_id: str,
        max_messages: int = 3
    ) -> Optional[RAGContext]:
        """Get recent conversation context"""
        async with self.db_pool.acquire() as conn:
            try:
                # Get conversation title
                conv = await conn.fetchrow('''
                    SELECT title FROM conversations WHERE id = $1
                ''', conversation_id)

                if not conv:
                    return None

                # Get recent messages
                messages = await conn.fetch('''
                    SELECT content, role, timestamp
                    FROM messages
                    WHERE conversation_id = $1
                    ORDER BY timestamp DESC
                    LIMIT $2
                ''', conversation_id, max_messages)

                if not messages:
                    return None

                # Build context text
                text = f"Recent conversation: {conv['title']}\n\n"
                for msg in reversed(messages):  # Chronological order
                    text += f"{msg['role']}: {msg['content']}\n\n"

                return RAGContext(
                    text=text,
                    source_type='conversation_context',
                    source_id=conversation_id,
                    relevance_score=1.0,  # Always highly relevant
                    metadata={
                        'title': conv['title'],
                        'message_count': len(messages)
                    }
                )

            except Exception as e:
                logger.error(f"Error getting conversation context: {e}")
                return None

    def format_context_for_prompt(
        self,
        contexts: List[RAGContext],
        max_tokens: int = 2000
    ) -> str:
        """
        Format contexts into a prompt-ready string

        Args:
            contexts: List of RAGContext objects
            max_tokens: Maximum tokens for context (rough estimate)

        Returns:
            Formatted context string
        """
        if not contexts:
            return ""

        formatted = "# Relevant Context\n\n"

        current_length = 0
        max_length = max_tokens * 4  # Rough character estimate

        for i, context in enumerate(contexts, 1):
            source_info = f"[Source: {context.source_type}]"

            context_block = f"## Context {i} {source_info}\n"
            context_block += f"{context.text}\n\n"

            if current_length + len(context_block) > max_length:
                break

            formatted += context_block
            current_length += len(context_block)

        return formatted

    async def augment_query(
        self,
        query: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        max_context_tokens: int = 2000
    ) -> Tuple[str, RAGResponse]:
        """
        Augment a query with retrieved context

        Args:
            query: Original user query
            user_id: User ID
            conversation_id: Optional conversation context
            max_context_tokens: Maximum tokens for context

        Returns:
            Tuple of (augmented_prompt, rag_response)
        """
        # Retrieve context
        rag_response = await self.retrieve_context(
            query=query,
            user_id=user_id,
            conversation_id=conversation_id,
            max_contexts=5
        )

        # Format context
        context_str = self.format_context_for_prompt(
            rag_response.contexts,
            max_tokens=max_context_tokens
        )

        # Build augmented prompt
        if context_str:
            augmented_prompt = f"""{context_str}

# User Query
{query}

# Instructions
Answer the user's query using the provided context. If the context doesn't contain relevant information, say so and provide your best answer based on your knowledge.
"""
        else:
            augmented_prompt = query

        return augmented_prompt, rag_response


# Singleton instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline(db_pool: asyncpg.Pool) -> RAGPipeline:
    """Get or create RAGPipeline singleton"""
    global _rag_pipeline

    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(db_pool)

    return _rag_pipeline
