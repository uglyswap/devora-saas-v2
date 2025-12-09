"""
Embeddings Service
==================
Generate and manage vector embeddings for semantic search
"""

import asyncpg
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import openai
import os
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    entity_type: str
    entity_id: str
    embedding_id: str
    success: bool
    error: Optional[str] = None


class EmbeddingService:
    """
    Service for generating and managing vector embeddings

    Features:
    - OpenAI embeddings generation
    - Batch processing for efficiency
    - Automatic updates on content change
    - Cosine similarity search
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        openai_api_key: Optional[str] = None,
        model: str = "text-embedding-ada-002"
    ):
        self.db_pool = db_pool
        self.model = model

        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.enabled = True
            logger.info(f"Embedding service initialized with model: {model}")
        else:
            self.enabled = False
            logger.warning("OpenAI API key not found, embeddings disabled")

    async def generate_embedding(
        self,
        text: str,
        retry_on_error: bool = True
    ) -> Optional[List[float]]:
        """
        Generate embedding vector for text

        Args:
            text: Text to embed
            retry_on_error: Retry once on failure

        Returns:
            Embedding vector or None on failure
        """
        if not self.enabled:
            return None

        try:
            # Truncate text if too long (8191 tokens for ada-002)
            if len(text) > 32000:  # Rough character limit
                text = text[:32000]

            response = await openai.Embedding.acreate(
                model=self.model,
                input=text
            )

            embedding = response['data'][0]['embedding']
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")

            if retry_on_error:
                logger.info("Retrying embedding generation...")
                return await self.generate_embedding(text, retry_on_error=False)

            return None

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batches

        Args:
            texts: List of texts to embed
            batch_size: Batch size for API calls

        Returns:
            List of embedding vectors (None for failed items)
        """
        if not self.enabled:
            return [None] * len(texts)

        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = await openai.Embedding.acreate(
                    model=self.model,
                    input=batch
                )

                batch_embeddings = [item['embedding'] for item in response['data']]
                embeddings.extend(batch_embeddings)

            except Exception as e:
                logger.error(f"Failed to generate batch embeddings: {e}")
                # Add None for failed batch
                embeddings.extend([None] * len(batch))

        return embeddings

    async def store_embedding(
        self,
        entity_type: str,
        entity_id: str,
        text_content: str,
        embedding: List[float]
    ) -> str:
        """
        Store embedding in database

        Args:
            entity_type: Type of entity ('project', 'conversation', 'message', 'file')
            entity_id: Entity UUID
            text_content: Original text
            embedding: Embedding vector

        Returns:
            Embedding ID
        """
        async with self.db_pool.acquire() as conn:
            embedding_id = await conn.fetchval('''
                INSERT INTO embeddings (
                    entity_type, entity_id, text_content,
                    embedding_vector, model_name, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (entity_type, entity_id)
                DO UPDATE SET
                    text_content = EXCLUDED.text_content,
                    embedding_vector = EXCLUDED.embedding_vector,
                    updated_at = NOW()
                RETURNING id
            ''',
                entity_type,
                entity_id,
                text_content,
                embedding,
                self.model,
                datetime.utcnow()
            )

            return str(embedding_id)

    async def generate_and_store_embedding(
        self,
        entity_type: str,
        entity_id: str,
        text_content: str
    ) -> EmbeddingResult:
        """
        Generate and store embedding for an entity

        Args:
            entity_type: Type of entity
            entity_id: Entity UUID
            text_content: Text to embed

        Returns:
            EmbeddingResult with success status
        """
        try:
            # Generate embedding
            embedding = await self.generate_embedding(text_content)

            if embedding is None:
                return EmbeddingResult(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    embedding_id='',
                    success=False,
                    error="Failed to generate embedding"
                )

            # Store in database
            embedding_id = await self.store_embedding(
                entity_type,
                entity_id,
                text_content,
                embedding
            )

            return EmbeddingResult(
                entity_type=entity_type,
                entity_id=entity_id,
                embedding_id=embedding_id,
                success=True
            )

        except Exception as e:
            logger.error(f"Error generating/storing embedding: {e}")
            return EmbeddingResult(
                entity_type=entity_type,
                entity_id=entity_id,
                embedding_id='',
                success=False,
                error=str(e)
            )

    async def embed_project(
        self,
        project_id: str
    ) -> EmbeddingResult:
        """Generate embedding for a project"""
        async with self.db_pool.acquire() as conn:
            # Get project data
            project = await conn.fetchrow('''
                SELECT name, description
                FROM projects
                WHERE id = $1
            ''', project_id)

            if not project:
                return EmbeddingResult(
                    entity_type='project',
                    entity_id=project_id,
                    embedding_id='',
                    success=False,
                    error="Project not found"
                )

            # Combine text for embedding
            text = f"{project['name']}\n{project['description'] or ''}"

            return await self.generate_and_store_embedding(
                'project',
                project_id,
                text
            )

    async def embed_conversation(
        self,
        conversation_id: str
    ) -> EmbeddingResult:
        """Generate embedding for a conversation"""
        async with self.db_pool.acquire() as conn:
            # Get conversation with messages
            conversation = await conn.fetchrow('''
                SELECT title FROM conversations WHERE id = $1
            ''', conversation_id)

            if not conversation:
                return EmbeddingResult(
                    entity_type='conversation',
                    entity_id=conversation_id,
                    embedding_id='',
                    success=False,
                    error="Conversation not found"
                )

            # Get recent messages
            messages = await conn.fetch('''
                SELECT content
                FROM messages
                WHERE conversation_id = $1
                ORDER BY timestamp DESC
                LIMIT 10
            ''', conversation_id)

            # Combine text
            text = conversation['title'] + "\n"
            text += "\n".join([msg['content'] for msg in messages])

            return await self.generate_and_store_embedding(
                'conversation',
                conversation_id,
                text
            )

    async def embed_message(
        self,
        message_id: str
    ) -> EmbeddingResult:
        """Generate embedding for a message"""
        async with self.db_pool.acquire() as conn:
            message = await conn.fetchrow('''
                SELECT content FROM messages WHERE id = $1
            ''', message_id)

            if not message:
                return EmbeddingResult(
                    entity_type='message',
                    entity_id=message_id,
                    embedding_id='',
                    success=False,
                    error="Message not found"
                )

            return await self.generate_and_store_embedding(
                'message',
                message_id,
                message['content']
            )

    async def embed_file(
        self,
        file_id: str
    ) -> EmbeddingResult:
        """Generate embedding for a file"""
        async with self.db_pool.acquire() as conn:
            file = await conn.fetchrow('''
                SELECT name, content FROM project_files WHERE id = $1
            ''', file_id)

            if not file:
                return EmbeddingResult(
                    entity_type='file',
                    entity_id=file_id,
                    embedding_id='',
                    success=False,
                    error="File not found"
                )

            # Combine filename and content
            text = f"{file['name']}\n{file['content']}"

            return await self.generate_and_store_embedding(
                'file',
                file_id,
                text
            )

    async def semantic_search(
        self,
        query_text: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using vector similarity

        Args:
            query_text: Search query
            entity_types: Filter by entity types
            limit: Maximum results
            similarity_threshold: Minimum cosine similarity

        Returns:
            List of similar entities with scores
        """
        if not self.enabled:
            return []

        # Generate query embedding
        query_embedding = await self.generate_embedding(query_text)

        if query_embedding is None:
            return []

        async with self.db_pool.acquire() as conn:
            # Build query
            entity_filter = ""
            if entity_types:
                entity_filter = f"AND entity_type = ANY($2)"
                params = [query_embedding, entity_types, limit, similarity_threshold]
            else:
                params = [query_embedding, limit, similarity_threshold]

            query = f'''
                SELECT
                    id,
                    entity_type,
                    entity_id,
                    text_content,
                    1 - (embedding_vector <=> $1::vector) as similarity
                FROM embeddings
                WHERE 1 - (embedding_vector <=> $1::vector) >= ${len(params)}
                {entity_filter}
                ORDER BY similarity DESC
                LIMIT ${len(params) - 1}
            '''

            rows = await conn.fetch(query, *params)

            results = []
            for row in rows:
                results.append({
                    'embedding_id': str(row['id']),
                    'entity_type': row['entity_type'],
                    'entity_id': str(row['entity_id']),
                    'text_preview': row['text_content'][:200],
                    'similarity': float(row['similarity'])
                })

            return results

    async def find_similar_entities(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar entities to a given entity

        Args:
            entity_type: Type of source entity
            entity_id: Source entity ID
            limit: Maximum similar entities

        Returns:
            List of similar entities
        """
        async with self.db_pool.acquire() as conn:
            # Get source embedding
            source = await conn.fetchrow('''
                SELECT embedding_vector
                FROM embeddings
                WHERE entity_type = $1 AND entity_id = $2
            ''', entity_type, entity_id)

            if not source:
                return []

            # Find similar
            rows = await conn.fetch('''
                SELECT
                    id,
                    entity_type,
                    entity_id,
                    text_content,
                    1 - (embedding_vector <=> $1::vector) as similarity
                FROM embeddings
                WHERE NOT (entity_type = $2 AND entity_id = $3)
                ORDER BY similarity DESC
                LIMIT $4
            ''', source['embedding_vector'], entity_type, entity_id, limit)

            results = []
            for row in rows:
                results.append({
                    'entity_type': row['entity_type'],
                    'entity_id': str(row['entity_id']),
                    'text_preview': row['text_content'][:200],
                    'similarity': float(row['similarity'])
                })

            return results


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(db_pool: asyncpg.Pool) -> EmbeddingService:
    """Get or create EmbeddingService singleton"""
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService(db_pool)

    return _embedding_service
