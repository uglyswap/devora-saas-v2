"""
Vector Store for Similarity Search

Supports:
- In-memory vector storage with cosine similarity
- PostgreSQL with pgvector extension
- Pinecone (cloud vector database)
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VectorStoreType(str, Enum):
    """Supported vector store backends"""
    MEMORY = "memory"
    PGVECTOR = "pgvector"
    PINECONE = "pinecone"


@dataclass
class VectorStoreConfig:
    """Configuration for vector store"""
    store_type: VectorStoreType = VectorStoreType.MEMORY
    connection_string: Optional[str] = None  # For pgvector
    api_key: Optional[str] = None  # For Pinecone
    index_name: str = "devora-embeddings"
    dimension: int = 1536
    metric: str = "cosine"  # cosine, euclidean, dotproduct


@dataclass
class SearchResult:
    """Search result from vector store"""
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class VectorStore:
    """Vector store for similarity search"""

    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self._backend = None

        # Initialize appropriate backend
        if config.store_type == VectorStoreType.MEMORY:
            self._backend = InMemoryVectorStore(config)
        elif config.store_type == VectorStoreType.PGVECTOR:
            self._backend = PGVectorStore(config)
        elif config.store_type == VectorStoreType.PINECONE:
            self._backend = PineconeVectorStore(config)
        else:
            raise ValueError(f"Unsupported vector store type: {config.store_type}")

    async def add(
        self,
        id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a vector to the store"""
        await self._backend.add(id, text, embedding, metadata or {})

    async def add_batch(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """Add multiple vectors to the store"""
        if metadatas is None:
            metadatas = [{}] * len(ids)

        await self._backend.add_batch(ids, texts, embeddings, metadatas)

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors"""
        return await self._backend.search(query_embedding, top_k, filter_metadata)

    async def delete(self, id: str):
        """Delete a vector by ID"""
        await self._backend.delete(id)

    async def clear(self):
        """Clear all vectors"""
        await self._backend.clear()

    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        return await self._backend.get_stats()


class InMemoryVectorStore:
    """In-memory vector store using numpy"""

    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self._vectors: Dict[str, Tuple[List[float], str, Dict[str, Any]]] = {}

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    async def add(
        self,
        id: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Add vector to memory"""
        self._vectors[id] = (embedding, text, metadata)
        logger.debug(f"[VectorStore] Added vector {id}")

    async def add_batch(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """Add multiple vectors"""
        for id, text, emb, meta in zip(ids, texts, embeddings, metadatas):
            await self.add(id, text, emb, meta)

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors"""
        if not self._vectors:
            return []

        query_vec = np.array(query_embedding)
        results = []

        # Calculate similarities
        for id, (embedding, text, metadata) in self._vectors.items():
            # Apply metadata filter if provided
            if filter_metadata:
                if not all(metadata.get(k) == v for k, v in filter_metadata.items()):
                    continue

            vec = np.array(embedding)

            if self.config.metric == "cosine":
                score = self.cosine_similarity(query_vec, vec)
            elif self.config.metric == "euclidean":
                score = -np.linalg.norm(query_vec - vec)  # Negative distance (higher is better)
            elif self.config.metric == "dotproduct":
                score = np.dot(query_vec, vec)
            else:
                score = self.cosine_similarity(query_vec, vec)

            results.append(SearchResult(
                id=id,
                text=text,
                score=float(score),
                metadata=metadata
            ))

        # Sort by score (descending) and return top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    async def delete(self, id: str):
        """Delete vector"""
        if id in self._vectors:
            del self._vectors[id]
            logger.debug(f"[VectorStore] Deleted vector {id}")

    async def clear(self):
        """Clear all vectors"""
        self._vectors.clear()
        logger.info("[VectorStore] Cleared all vectors")

    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            "total_vectors": len(self._vectors),
            "store_type": "memory",
        }


class PGVectorStore:
    """PostgreSQL vector store using pgvector extension"""

    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self._pool = None

    async def _get_pool(self):
        """Get or create connection pool"""
        if self._pool is None:
            try:
                import asyncpg
                self._pool = await asyncpg.create_pool(self.config.connection_string)

                # Create table if not exists
                async with self._pool.acquire() as conn:
                    await conn.execute("""
                        CREATE EXTENSION IF NOT EXISTS vector;

                        CREATE TABLE IF NOT EXISTS embeddings (
                            id TEXT PRIMARY KEY,
                            text TEXT NOT NULL,
                            embedding vector(%s),
                            metadata JSONB,
                            created_at TIMESTAMP DEFAULT NOW()
                        );

                        CREATE INDEX IF NOT EXISTS embeddings_vector_idx
                        ON embeddings USING ivfflat (embedding vector_cosine_ops);
                    """ % self.config.dimension)

                logger.info("[VectorStore] Connected to PostgreSQL with pgvector")

            except ImportError:
                logger.error("[VectorStore] asyncpg not installed. Install with: pip install asyncpg")
                raise
            except Exception as e:
                logger.error(f"[VectorStore] Failed to connect to PostgreSQL: {e}")
                raise

        return self._pool

    async def add(
        self,
        id: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Add vector to PostgreSQL"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            import json
            await conn.execute(
                """
                INSERT INTO embeddings (id, text, embedding, metadata)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE
                SET text = $2, embedding = $3, metadata = $4
                """,
                id, text, embedding, json.dumps(metadata)
            )
        logger.debug(f"[VectorStore] Added vector {id} to PostgreSQL")

    async def add_batch(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """Add multiple vectors"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            import json
            await conn.executemany(
                """
                INSERT INTO embeddings (id, text, embedding, metadata)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE
                SET text = $2, embedding = $3, metadata = $4
                """,
                [(id, text, emb, json.dumps(meta))
                 for id, text, emb, meta in zip(ids, texts, embeddings, metadatas)]
            )
        logger.debug(f"[VectorStore] Added {len(ids)} vectors to PostgreSQL")

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search using pgvector"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Build query based on metric
            if self.config.metric == "cosine":
                distance_op = "<=>"
            elif self.config.metric == "euclidean":
                distance_op = "<->"
            else:
                distance_op = "<=>"

            # Add metadata filter if provided
            where_clause = ""
            if filter_metadata:
                import json
                conditions = [f"metadata @> '{json.dumps({k: v})}'" for k, v in filter_metadata.items()]
                where_clause = "WHERE " + " AND ".join(conditions)

            query = f"""
                SELECT id, text, embedding {distance_op} $1 AS score, metadata
                FROM embeddings
                {where_clause}
                ORDER BY score
                LIMIT $2
            """

            rows = await conn.fetch(query, query_embedding, top_k)

            results = []
            for row in rows:
                import json
                results.append(SearchResult(
                    id=row["id"],
                    text=row["text"],
                    score=1.0 - float(row["score"]),  # Convert distance to similarity
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {}
                ))

            return results

    async def delete(self, id: str):
        """Delete vector"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM embeddings WHERE id = $1", id)
        logger.debug(f"[VectorStore] Deleted vector {id} from PostgreSQL")

    async def clear(self):
        """Clear all vectors"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM embeddings")
        logger.info("[VectorStore] Cleared all vectors from PostgreSQL")

    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM embeddings")
            return {
                "total_vectors": count,
                "store_type": "pgvector",
            }

    async def close(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()


class PineconeVectorStore:
    """Pinecone cloud vector store"""

    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self._index = None

    def _get_index(self):
        """Get or create Pinecone index"""
        if self._index is None:
            try:
                from pinecone import Pinecone

                pc = Pinecone(api_key=self.config.api_key)

                # Create index if not exists
                if self.config.index_name not in pc.list_indexes().names():
                    pc.create_index(
                        name=self.config.index_name,
                        dimension=self.config.dimension,
                        metric=self.config.metric,
                    )
                    logger.info(f"[VectorStore] Created Pinecone index: {self.config.index_name}")

                self._index = pc.Index(self.config.index_name)
                logger.info(f"[VectorStore] Connected to Pinecone index: {self.config.index_name}")

            except ImportError:
                logger.error("[VectorStore] pinecone-client not installed. Install with: pip install pinecone-client")
                raise
            except Exception as e:
                logger.error(f"[VectorStore] Failed to connect to Pinecone: {e}")
                raise

        return self._index

    async def add(
        self,
        id: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Add vector to Pinecone"""
        index = self._get_index()
        metadata["text"] = text
        index.upsert(vectors=[(id, embedding, metadata)])
        logger.debug(f"[VectorStore] Added vector {id} to Pinecone")

    async def add_batch(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """Add multiple vectors"""
        index = self._get_index()
        vectors = []
        for id, text, emb, meta in zip(ids, texts, embeddings, metadatas):
            meta["text"] = text
            vectors.append((id, emb, meta))

        # Pinecone recommends batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)

        logger.debug(f"[VectorStore] Added {len(ids)} vectors to Pinecone")

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search using Pinecone"""
        index = self._get_index()

        # Build filter
        pinecone_filter = filter_metadata if filter_metadata else None

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=pinecone_filter,
            include_metadata=True,
        )

        search_results = []
        for match in results.matches:
            metadata = match.metadata or {}
            text = metadata.pop("text", "")

            search_results.append(SearchResult(
                id=match.id,
                text=text,
                score=match.score,
                metadata=metadata
            ))

        return search_results

    async def delete(self, id: str):
        """Delete vector"""
        index = self._get_index()
        index.delete(ids=[id])
        logger.debug(f"[VectorStore] Deleted vector {id} from Pinecone")

    async def clear(self):
        """Clear all vectors"""
        index = self._get_index()
        index.delete(delete_all=True)
        logger.info("[VectorStore] Cleared all vectors from Pinecone")

    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        index = self._get_index()
        stats = index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "store_type": "pinecone",
            "index_fullness": stats.index_fullness,
        }
