"""
Agent Memory System - Complete memory management for AI agents.

Provides a unified interface for agents to:
- Store and retrieve memories across sessions
- Learn from user interactions and preferences
- Access relevant historical context for current tasks
- Build contextual prompts with memory-enhanced information
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import hashlib

from .memory_types import (
    Memory,
    MemoryType,
    MemoryMetadata,
    MemorySearchResult,
)
from .memory_store import MemoryStore

logger = logging.getLogger(__name__)


class AgentMemorySystem:
    """Complete memory system for an AI agent.

    Manages three types of memory:
    - Short-term: Current conversation context (session-scoped)
    - Long-term: Learned patterns, user preferences (persistent)
    - Episodic: Historical records of past generations (persistent)

    The system provides:
    - Memory storage with automatic categorization
    - Intelligent recall based on current context
    - Memory consolidation (short-term -> long-term)
    - Context building for agent prompts

    Example:
        memory = AgentMemorySystem(user_id="user_123", store=memory_store)

        # Remember something
        await memory.remember(
            content="User prefers TypeScript",
            metadata={"source": "preference"},
            importance=0.8
        )

        # Recall relevant memories
        memories = await memory.recall("typescript project", k=5)

        # Get context for an agent
        context = await memory.get_context_for_agent("Build a REST API")
    """

    # Configuration
    MAX_SHORT_TERM_MEMORIES = 50
    SHORT_TERM_EXPIRY_HOURS = 24
    CONSOLIDATION_THRESHOLD = 20

    def __init__(self, user_id: str, store: MemoryStore):
        """Initialize the agent memory system.

        Args:
            user_id: Unique identifier for the user
            store: MemoryStore instance for persistence
        """
        self.user_id = user_id
        self.store = store

        # In-memory short-term cache for fast access
        self.short_term: List[Dict[str, Any]] = []

        # Track what's been recalled this session for importance boosting
        self._accessed_memories: set = set()

    async def remember(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        tags: Optional[List[str]] = None
    ) -> str:
        """Store a new memory.

        Args:
            content: The content to remember
            metadata: Additional context (source, project_id, etc.)
            importance: Importance score (0.0 to 1.0)
            memory_type: Type of memory (default: SHORT_TERM)
            tags: Optional tags for categorization

        Returns:
            The ID of the stored memory
        """
        # Check for duplicate content to avoid redundant storage
        content_hash = self._hash_content(content)
        existing = await self._find_duplicate(content_hash)
        if existing:
            # Boost importance of existing memory instead
            existing.boost_importance(0.1)
            await self.store.update(existing)
            logger.debug(f"Boosted existing memory {existing.id}")
            return existing.id

        # Build metadata
        mem_metadata = MemoryMetadata()
        if metadata:
            mem_metadata.source = metadata.get("source")
            mem_metadata.agent_id = metadata.get("agent_id")
            mem_metadata.project_id = metadata.get("project_id")
            mem_metadata.project_type = metadata.get("project_type")
            mem_metadata.files_generated = metadata.get("files_generated", [])
            mem_metadata.technologies = metadata.get("technologies", [])
            mem_metadata.was_successful = metadata.get("was_successful")
            mem_metadata.user_feedback = metadata.get("user_feedback")
            mem_metadata.extra = {
                k: v for k, v in metadata.items()
                if k not in ["source", "agent_id", "project_id", "project_type",
                             "files_generated", "technologies", "was_successful",
                             "user_feedback"]
            }

        # Set expiration for short-term memories
        expires_at = None
        if memory_type == MemoryType.SHORT_TERM:
            expires_at = datetime.now(timezone.utc) + timedelta(
                hours=self.SHORT_TERM_EXPIRY_HOURS
            )

        # Create memory
        memory = Memory(
            user_id=self.user_id,
            memory_type=memory_type,
            content=content,
            metadata=mem_metadata,
            importance=importance,
            tags=tags or [],
            expires_at=expires_at
        )

        # Store in database
        memory_id = await self.store.add(memory)

        # Add to short-term cache if applicable
        if memory_type == MemoryType.SHORT_TERM:
            self.short_term.append({
                "id": memory_id,
                "content": content,
                "importance": importance,
                "timestamp": datetime.now(timezone.utc)
            })

            # Trigger consolidation if cache is full
            if len(self.short_term) >= self.CONSOLIDATION_THRESHOLD:
                await self._auto_consolidate()

        logger.debug(f"Remembered: {content[:50]}... (type={memory_type.value})")
        return memory_id

    async def recall(
        self,
        query: str,
        k: int = 10,
        memory_types: Optional[List[MemoryType]] = None,
        min_importance: float = 0.0,
        include_short_term_cache: bool = True
    ) -> List[Memory]:
        """Recall memories relevant to a query.

        Searches across memory types and combines results based on relevance.

        Args:
            query: The search query
            k: Maximum number of memories to return
            memory_types: Types to search (default: all types)
            min_importance: Minimum importance threshold
            include_short_term_cache: Include in-memory cache

        Returns:
            List of relevant Memory objects
        """
        all_results: List[MemorySearchResult] = []

        # Search each memory type
        types_to_search = memory_types or [
            MemoryType.LONG_TERM,
            MemoryType.EPISODIC,
            MemoryType.SHORT_TERM
        ]

        for mem_type in types_to_search:
            results = await self.store.search(
                user_id=self.user_id,
                query=query,
                memory_type=mem_type,
                limit=k,
                min_importance=min_importance
            )
            all_results.extend(results)

        # Sort by relevance and importance
        all_results.sort(
            key=lambda x: (x.relevance_score * 0.6 + x.memory.importance * 0.4),
            reverse=True
        )

        # Get unique memories (deduplicate)
        seen_ids = set()
        unique_memories: List[Memory] = []

        for result in all_results:
            if result.memory.id not in seen_ids:
                seen_ids.add(result.memory.id)
                unique_memories.append(result.memory)

                # Track access for importance boosting
                self._accessed_memories.add(result.memory.id)

                if len(unique_memories) >= k:
                    break

        # Boost importance of accessed memories
        for memory in unique_memories:
            memory.boost_importance(0.05)
            await self.store.update(memory)

        logger.debug(f"Recalled {len(unique_memories)} memories for query: {query[:30]}...")
        return unique_memories

    async def get_context_for_agent(
        self,
        current_task: str,
        max_tokens: int = 2000,
        include_preferences: bool = True,
        include_history: bool = True
    ) -> str:
        """Build a context string for an agent based on memories.

        Constructs a formatted context that can be injected into agent prompts.

        Args:
            current_task: Description of the current task
            max_tokens: Approximate maximum tokens for context
            include_preferences: Include user preferences
            include_history: Include relevant historical context

        Returns:
            Formatted context string for agent prompts
        """
        context_parts: List[str] = []
        estimated_tokens = 0
        tokens_per_char = 0.25  # Rough estimate

        # 1. User Preferences (Long-term memories)
        if include_preferences:
            preferences = await self.store.get_by_type(
                self.user_id,
                MemoryType.LONG_TERM,
                limit=10
            )

            if preferences:
                pref_lines = ["## User Preferences & Patterns"]
                for pref in preferences:
                    if estimated_tokens >= max_tokens * 0.3:
                        break
                    line = f"- {pref.content}"
                    pref_lines.append(line)
                    estimated_tokens += len(line) * tokens_per_char

                context_parts.append("\n".join(pref_lines))

        # 2. Relevant Historical Context (Episodic memories)
        if include_history:
            relevant_history = await self.recall(
                query=current_task,
                k=5,
                memory_types=[MemoryType.EPISODIC],
                min_importance=0.3
            )

            if relevant_history:
                history_lines = ["## Relevant History"]
                for mem in relevant_history:
                    if estimated_tokens >= max_tokens * 0.6:
                        break
                    # Truncate long content
                    content = mem.content[:300] + "..." if len(mem.content) > 300 else mem.content
                    line = f"- {content}"
                    history_lines.append(line)
                    estimated_tokens += len(line) * tokens_per_char

                context_parts.append("\n".join(history_lines))

        # 3. Current Session Context (Short-term)
        if self.short_term:
            session_lines = ["## Current Session Context"]
            for item in reversed(self.short_term[-5:]):  # Last 5 items
                if estimated_tokens >= max_tokens * 0.9:
                    break
                content = item["content"][:200]
                line = f"- {content}"
                session_lines.append(line)
                estimated_tokens += len(line) * tokens_per_char

            context_parts.append("\n".join(session_lines))

        if not context_parts:
            return ""

        return "\n\n".join(context_parts)

    async def remember_generation(
        self,
        prompt: str,
        files_generated: List[str],
        technologies: List[str],
        was_successful: bool = True,
        project_id: Optional[str] = None,
        project_type: Optional[str] = None
    ) -> str:
        """Remember a code generation event as episodic memory.

        Args:
            prompt: The user's generation prompt
            files_generated: List of files that were generated
            technologies: Technologies/frameworks used
            was_successful: Whether generation was successful
            project_id: Associated project ID
            project_type: Type of project

        Returns:
            Memory ID
        """
        # Build summary content
        tech_str = ", ".join(technologies[:5]) if technologies else "various"
        file_count = len(files_generated)

        content = (
            f"Generated {file_count} files using {tech_str} "
            f"for: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
        )

        # Higher importance for successful generations
        importance = 0.7 if was_successful else 0.4

        return await self.remember(
            content=content,
            metadata={
                "source": "generation",
                "project_id": project_id,
                "project_type": project_type,
                "files_generated": files_generated[:20],  # Limit stored files
                "technologies": technologies,
                "was_successful": was_successful
            },
            importance=importance,
            memory_type=MemoryType.EPISODIC,
            tags=["generation"] + technologies[:5]
        )

    async def remember_preference(
        self,
        preference: str,
        source: str = "extracted",
        importance: float = 0.7
    ) -> str:
        """Remember a user preference as long-term memory.

        Args:
            preference: The preference content
            source: Where preference was detected
            importance: Importance score

        Returns:
            Memory ID
        """
        return await self.remember(
            content=preference,
            metadata={"source": source},
            importance=importance,
            memory_type=MemoryType.LONG_TERM,
            tags=["preference"]
        )

    async def remember_feedback(
        self,
        feedback: str,
        related_memory_id: Optional[str] = None,
        positive: bool = True
    ) -> str:
        """Remember user feedback.

        Args:
            feedback: The feedback content
            related_memory_id: ID of related memory (if applicable)
            positive: Whether feedback is positive

        Returns:
            Memory ID
        """
        importance = 0.8 if positive else 0.6

        return await self.remember(
            content=feedback,
            metadata={
                "source": "feedback",
                "related_memory_id": related_memory_id,
                "positive": positive
            },
            importance=importance,
            memory_type=MemoryType.LONG_TERM,
            tags=["feedback", "positive" if positive else "negative"]
        )

    async def extract_and_remember_preferences(self, message: str) -> List[str]:
        """Extract and store preferences from a user message.

        Detects common preference patterns in user messages and stores them.

        Args:
            message: User message to analyze

        Returns:
            List of extracted preference memory IDs
        """
        preferences: List[str] = []
        message_lower = message.lower()

        # Technology preferences
        tech_patterns = {
            "typescript": "User prefers TypeScript over JavaScript",
            "tailwind": "User prefers Tailwind CSS for styling",
            "react": "User prefers React for frontend",
            "vue": "User prefers Vue.js for frontend",
            "next": "User prefers Next.js framework",
            "supabase": "User uses Supabase for backend/database",
            "prisma": "User prefers Prisma as ORM",
            "mongodb": "User uses MongoDB for database",
            "postgresql": "User prefers PostgreSQL database",
        }

        for pattern, preference in tech_patterns.items():
            if pattern in message_lower:
                preferences.append(preference)

        # Style preferences
        if "dark" in message_lower or "sombre" in message_lower:
            preferences.append("User prefers dark theme/mode")
        if "minimal" in message_lower or "simple" in message_lower:
            preferences.append("User prefers minimal, simple designs")
        if "modern" in message_lower or "moderne" in message_lower:
            preferences.append("User prefers modern, contemporary design")
        if "professional" in message_lower:
            preferences.append("User prefers professional, business-like design")

        # Store preferences
        memory_ids = []
        for pref in preferences:
            mem_id = await self.remember_preference(pref, source="message_extraction")
            memory_ids.append(mem_id)

        return memory_ids

    async def consolidate(self) -> Dict[str, int]:
        """Consolidate short-term memories to long-term.

        Should be called periodically or at session end.

        Returns:
            Statistics about consolidation
        """
        result = await self.store.consolidate(self.user_id)

        # Clear short-term cache
        self.short_term = []

        return {
            "consolidated": result.consolidated_count,
            "discarded": result.discarded_count
        }

    async def cleanup(
        self,
        forget_threshold: float = 0.2,
        age_days: int = 30,
        apply_decay: bool = True
    ) -> Dict[str, int]:
        """Perform memory cleanup operations.

        Args:
            forget_threshold: Importance threshold for forgetting
            age_days: Minimum age for forgetting
            apply_decay: Whether to apply importance decay

        Returns:
            Statistics about cleanup
        """
        stats = {"forgotten": 0, "decayed": 0}

        # Apply decay to old memories
        if apply_decay:
            stats["decayed"] = await self.store.apply_decay(self.user_id)

        # Forget low-importance old memories
        stats["forgotten"] = await self.store.forget(
            self.user_id,
            importance_threshold=forget_threshold,
            age_days=age_days
        )

        return stats

    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this user.

        Returns:
            Dictionary with memory counts and statistics
        """
        stats = await self.store.get_stats(self.user_id)
        stats["short_term_cache_size"] = len(self.short_term)
        stats["accessed_this_session"] = len(self._accessed_memories)
        return stats

    async def clear_short_term(self) -> int:
        """Clear short-term memory cache.

        Returns:
            Number of memories cleared
        """
        count = len(self.short_term)
        self.short_term = []
        cleared = await self.store.clear_user_memories(
            self.user_id,
            MemoryType.SHORT_TERM
        )
        return cleared

    async def _auto_consolidate(self) -> None:
        """Automatically consolidate when short-term is full."""
        logger.debug("Auto-consolidating short-term memories")
        await self.consolidate()

    async def _find_duplicate(self, content_hash: str) -> Optional[Memory]:
        """Find a memory with the same content hash.

        Args:
            content_hash: Hash of the content to find

        Returns:
            Existing Memory if found, None otherwise
        """
        # Check recent memories for duplicates
        results = await self.store.search(
            user_id=self.user_id,
            query="",
            limit=20,
            min_importance=0.0
        )

        for result in results:
            if self._hash_content(result.memory.content) == content_hash:
                return result.memory

        return None

    def _hash_content(self, content: str) -> str:
        """Generate a hash for content comparison.

        Args:
            content: Content to hash

        Returns:
            SHA256 hash of normalized content
        """
        normalized = content.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]


# Factory function for easy instantiation
async def create_agent_memory(
    user_id: str,
    db,
    initialize_indexes: bool = False
) -> AgentMemorySystem:
    """Create an AgentMemorySystem instance.

    Factory function that handles store initialization.

    Args:
        user_id: User identifier
        db: MongoDB database instance
        initialize_indexes: Whether to create indexes (first run only)

    Returns:
        Configured AgentMemorySystem instance
    """
    store = MemoryStore(db)

    if initialize_indexes:
        await store.initialize_indexes()

    return AgentMemorySystem(user_id=user_id, store=store)
