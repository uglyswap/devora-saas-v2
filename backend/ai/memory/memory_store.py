"""
Memory Store Module - MongoDB-based persistence for agent memories.

Provides CRUD operations and advanced querying for the memory system:
- Add/update/delete memories
- Search with text matching and filters
- Consolidation of short-term to long-term memories
- Automatic forgetting of low-importance memories
- Memory statistics and analytics
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import re

from .memory_types import (
    Memory,
    MemoryType,
    MemorySearchResult,
    MemoryConsolidationResult,
)

logger = logging.getLogger(__name__)


class MemoryStore:
    """MongoDB-based memory store for agent memories.

    Provides persistent storage with:
    - Text-based search (with optional vector search via embeddings)
    - Memory consolidation algorithms
    - Automatic cleanup of expired/low-importance memories
    - User-isolated namespaces

    Example:
        store = MemoryStore(db)
        await store.initialize_indexes()

        memory_id = await store.add(memory)
        results = await store.search(user_id, "typescript preferences")
        await store.consolidate(user_id)
    """

    COLLECTION_NAME = "agent_memories"

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize the memory store.

        Args:
            db: Motor async MongoDB database instance
        """
        self.db = db
        self.collection = db[self.COLLECTION_NAME]

    async def initialize_indexes(self) -> None:
        """Create necessary indexes for efficient querying.

        Should be called during application startup.
        """
        try:
            # User + type compound index for filtered queries
            await self.collection.create_index(
                [("user_id", 1), ("memory_type", 1)],
                name="user_type_idx"
            )

            # User + importance for priority queries
            await self.collection.create_index(
                [("user_id", 1), ("importance", -1)],
                name="user_importance_idx"
            )

            # Text index for content search
            await self.collection.create_index(
                [("content", "text"), ("tags", "text")],
                name="content_text_idx",
                default_language="english"
            )

            # TTL index for automatic expiration of short-term memories
            await self.collection.create_index(
                "expires_at",
                name="expiration_idx",
                expireAfterSeconds=0
            )

            # Last accessed for cleanup queries
            await self.collection.create_index(
                [("user_id", 1), ("last_accessed", 1)],
                name="user_last_accessed_idx"
            )

            logger.info("Memory store indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to create memory store indexes: {e}")
            raise

    async def add(self, memory: Memory) -> str:
        """Add a new memory to the store.

        Args:
            memory: The Memory object to store

        Returns:
            The ID of the stored memory

        Raises:
            Exception: If storage fails
        """
        try:
            doc = memory.to_mongo_dict()
            result = await self.collection.insert_one(doc)
            logger.debug(f"Stored memory {memory.id} for user {memory.user_id}")
            return memory.id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    async def get(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID.

        Args:
            memory_id: The unique memory identifier

        Returns:
            Memory object if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"id": memory_id})
            if doc:
                memory = Memory.from_mongo_dict(doc)
                # Update access tracking
                memory.update_access()
                await self.update(memory)
                return memory
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve memory {memory_id}: {e}")
            return None

    async def update(self, memory: Memory) -> bool:
        """Update an existing memory.

        Args:
            memory: The Memory object with updated fields

        Returns:
            True if update successful, False otherwise
        """
        try:
            doc = memory.to_mongo_dict()
            result = await self.collection.update_one(
                {"id": memory.id},
                {"$set": doc}
            )
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Failed to update memory {memory.id}: {e}")
            return False

    async def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID.

        Args:
            memory_id: The unique memory identifier

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.collection.delete_one({"id": memory_id})
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    async def search(
        self,
        user_id: str,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
        min_importance: float = 0.0,
        tags: Optional[List[str]] = None,
        include_expired: bool = False
    ) -> List[MemorySearchResult]:
        """Search memories with text matching and filters.

        Uses MongoDB text search for content matching and applies
        additional filters for type, importance, and tags.

        Args:
            user_id: User ID to scope the search
            query: Text query for content matching
            memory_type: Optional filter by memory type
            limit: Maximum results to return
            min_importance: Minimum importance threshold
            tags: Optional list of tags to filter by
            include_expired: Whether to include expired memories

        Returns:
            List of MemorySearchResult objects sorted by relevance
        """
        try:
            # Build filter
            filter_query: Dict[str, Any] = {"user_id": user_id}

            if memory_type:
                filter_query["memory_type"] = memory_type.value

            if min_importance > 0:
                filter_query["importance"] = {"$gte": min_importance}

            if tags:
                filter_query["tags"] = {"$in": tags}

            if not include_expired:
                filter_query["$or"] = [
                    {"expires_at": None},
                    {"expires_at": {"$gt": datetime.now(timezone.utc)}}
                ]

            results: List[MemorySearchResult] = []

            if query and query.strip():
                # Use text search with score
                pipeline = [
                    {"$match": {**filter_query, "$text": {"$search": query}}},
                    {"$addFields": {"score": {"$meta": "textScore"}}},
                    {"$sort": {"score": -1, "importance": -1}},
                    {"$limit": limit}
                ]

                async for doc in self.collection.aggregate(pipeline):
                    memory = Memory.from_mongo_dict(doc)
                    score = doc.get("score", 1.0)
                    # Normalize score (text score can exceed 1.0)
                    normalized_score = min(1.0, score / 10.0)
                    results.append(MemorySearchResult(
                        memory=memory,
                        relevance_score=normalized_score
                    ))

            else:
                # No text query, just filter and sort by importance
                cursor = self.collection.find(filter_query)
                cursor = cursor.sort([("importance", -1), ("last_accessed", -1)])
                cursor = cursor.limit(limit)

                async for doc in cursor:
                    memory = Memory.from_mongo_dict(doc)
                    results.append(MemorySearchResult(
                        memory=memory,
                        relevance_score=memory.importance
                    ))

            # Fallback to regex search if text search returns no results
            if not results and query and query.strip():
                results = await self._regex_search(
                    user_id, query, filter_query, limit
                )

            return results

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            # Fallback to simple regex search
            return await self._regex_search(user_id, query, {"user_id": user_id}, limit)

    async def _regex_search(
        self,
        user_id: str,
        query: str,
        base_filter: Dict[str, Any],
        limit: int
    ) -> List[MemorySearchResult]:
        """Fallback regex-based search when text index is unavailable.

        Args:
            user_id: User ID to scope search
            query: Search query
            base_filter: Base filter to apply
            limit: Maximum results

        Returns:
            List of search results
        """
        try:
            # Build case-insensitive regex pattern
            pattern = re.escape(query)
            regex_filter = {
                **base_filter,
                "content": {"$regex": pattern, "$options": "i"}
            }

            results: List[MemorySearchResult] = []
            cursor = self.collection.find(regex_filter)
            cursor = cursor.sort([("importance", -1)])
            cursor = cursor.limit(limit)

            async for doc in cursor:
                memory = Memory.from_mongo_dict(doc)
                results.append(MemorySearchResult(
                    memory=memory,
                    relevance_score=memory.importance
                ))

            return results

        except Exception as e:
            logger.error(f"Regex search failed: {e}")
            return []

    async def get_by_type(
        self,
        user_id: str,
        memory_type: MemoryType,
        limit: int = 50
    ) -> List[Memory]:
        """Get all memories of a specific type for a user.

        Args:
            user_id: User ID
            memory_type: Type of memories to retrieve
            limit: Maximum memories to return

        Returns:
            List of Memory objects
        """
        try:
            memories: List[Memory] = []
            cursor = self.collection.find({
                "user_id": user_id,
                "memory_type": memory_type.value
            })
            cursor = cursor.sort([("importance", -1)])
            cursor = cursor.limit(limit)

            async for doc in cursor:
                memories.append(Memory.from_mongo_dict(doc))

            return memories

        except Exception as e:
            logger.error(f"Failed to get memories by type: {e}")
            return []

    async def consolidate(self, user_id: str) -> MemoryConsolidationResult:
        """Consolidate short-term memories into long-term storage.

        This process:
        1. Identifies high-importance short-term memories
        2. Promotes them to long-term storage
        3. Removes or archives low-importance short-term memories

        Args:
            user_id: User ID to consolidate memories for

        Returns:
            MemoryConsolidationResult with statistics
        """
        result = MemoryConsolidationResult()

        try:
            # Get all short-term memories for user
            short_term_memories = await self.get_by_type(
                user_id, MemoryType.SHORT_TERM, limit=100
            )

            for memory in short_term_memories:
                # High importance or frequently accessed -> promote to long-term
                if memory.importance >= 0.7 or memory.access_count >= 3:
                    memory.memory_type = MemoryType.LONG_TERM
                    memory.expires_at = None  # Remove expiration
                    await self.update(memory)
                    result.consolidated_count += 1
                    result.new_long_term_memories.append(memory.id)

                # Low importance and old -> discard
                elif memory.importance < 0.3:
                    age = datetime.now(timezone.utc) - memory.created_at
                    if age > timedelta(hours=24):
                        await self.delete(memory.id)
                        result.discarded_count += 1
                        result.discarded_memory_ids.append(memory.id)

            logger.info(
                f"Consolidated memories for user {user_id}: "
                f"{result.consolidated_count} promoted, "
                f"{result.discarded_count} discarded"
            )

            return result

        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            return result

    async def forget(
        self,
        user_id: str,
        importance_threshold: float = 0.2,
        age_days: int = 30
    ) -> int:
        """Forget (delete) low-importance memories.

        Removes memories that are:
        - Below the importance threshold
        - Older than the specified age
        - Not accessed recently

        Args:
            user_id: User ID
            importance_threshold: Maximum importance to forget
            age_days: Minimum age in days before forgetting

        Returns:
            Number of memories deleted
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=age_days)

            result = await self.collection.delete_many({
                "user_id": user_id,
                "importance": {"$lt": importance_threshold},
                "created_at": {"$lt": cutoff_date},
                "memory_type": {"$ne": MemoryType.LONG_TERM.value}  # Never forget long-term
            })

            deleted_count = result.deleted_count
            logger.info(f"Forgot {deleted_count} memories for user {user_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Forget operation failed: {e}")
            return 0

    async def apply_decay(
        self,
        user_id: str,
        decay_factor: float = 0.95,
        min_importance: float = 0.1
    ) -> int:
        """Apply importance decay to memories not recently accessed.

        Reduces importance of memories that haven't been accessed recently,
        simulating natural memory decay.

        Args:
            user_id: User ID
            decay_factor: Multiplier for importance (0.95 = 5% decay)
            min_importance: Minimum importance floor

        Returns:
            Number of memories decayed
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

            result = await self.collection.update_many(
                {
                    "user_id": user_id,
                    "last_accessed": {"$lt": cutoff_date},
                    "importance": {"$gt": min_importance}
                },
                [
                    {
                        "$set": {
                            "importance": {
                                "$max": [
                                    min_importance,
                                    {"$multiply": ["$importance", decay_factor]}
                                ]
                            }
                        }
                    }
                ]
            )

            logger.debug(f"Applied decay to {result.modified_count} memories")
            return result.modified_count

        except Exception as e:
            logger.error(f"Decay operation failed: {e}")
            return 0

    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with memory counts and statistics
        """
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$group": {
                        "_id": "$memory_type",
                        "count": {"$sum": 1},
                        "avg_importance": {"$avg": "$importance"},
                        "total_accesses": {"$sum": "$access_count"}
                    }
                }
            ]

            stats: Dict[str, Any] = {
                "total": 0,
                "by_type": {},
                "avg_importance": 0.0,
                "total_accesses": 0
            }

            total_importance = 0.0
            count = 0

            async for doc in self.collection.aggregate(pipeline):
                memory_type = doc["_id"]
                type_stats = {
                    "count": doc["count"],
                    "avg_importance": doc["avg_importance"],
                    "total_accesses": doc["total_accesses"]
                }
                stats["by_type"][memory_type] = type_stats
                stats["total"] += doc["count"]
                stats["total_accesses"] += doc["total_accesses"]
                total_importance += doc["avg_importance"] * doc["count"]
                count += doc["count"]

            if count > 0:
                stats["avg_importance"] = total_importance / count

            return stats

        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"total": 0, "by_type": {}, "avg_importance": 0.0}

    async def clear_user_memories(
        self,
        user_id: str,
        memory_type: Optional[MemoryType] = None
    ) -> int:
        """Clear all memories for a user.

        Args:
            user_id: User ID
            memory_type: Optional specific type to clear

        Returns:
            Number of memories deleted
        """
        try:
            filter_query = {"user_id": user_id}
            if memory_type:
                filter_query["memory_type"] = memory_type.value

            result = await self.collection.delete_many(filter_query)
            logger.info(f"Cleared {result.deleted_count} memories for user {user_id}")
            return result.deleted_count

        except Exception as e:
            logger.error(f"Failed to clear user memories: {e}")
            return 0
