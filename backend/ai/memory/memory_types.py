"""
Memory Types Module - Data models for the agent memory system.

Defines the core data structures:
- MemoryType: Enum for categorizing memories (short-term, long-term, episodic)
- MemoryMetadata: Additional context for memories
- Memory: The primary memory entity with content, type, and importance
"""

from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import uuid


class MemoryType(str, Enum):
    """Types of memory in the agent memory system.

    SHORT_TERM: Current conversation context, typically cleared after session
    LONG_TERM: Learned patterns, user preferences, persistent knowledge
    EPISODIC: Historical records of generations, interactions, and outcomes
    """
    SHORT_TERM = "short_term"    # Current conversation context
    LONG_TERM = "long_term"      # Learned patterns, preferences
    EPISODIC = "episodic"        # Historical generation records


class MemoryMetadata(BaseModel):
    """Metadata associated with a memory.

    Provides additional context for memory retrieval and categorization.
    """
    # Source information
    source: Optional[str] = None  # e.g., "conversation", "generation", "feedback"
    agent_id: Optional[str] = None  # Which agent created this memory

    # Project context
    project_id: Optional[str] = None
    project_type: Optional[str] = None  # e.g., "saas", "ecommerce", "api"

    # Generation context
    files_generated: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

    # Feedback and learning
    was_successful: Optional[bool] = None
    user_feedback: Optional[str] = None
    error_message: Optional[str] = None

    # Embedding for semantic search (stored separately in vector index)
    embedding_id: Optional[str] = None

    # Custom data
    extra: Dict[str, Any] = Field(default_factory=dict)


class Memory(BaseModel):
    """Primary memory entity for the agent memory system.

    Represents a single piece of information stored in memory with:
    - Unique identifier
    - User association for isolation
    - Content and categorization
    - Importance scoring for retrieval prioritization
    - Timestamps for lifecycle management

    Example:
        memory = Memory(
            user_id="user_123",
            memory_type=MemoryType.LONG_TERM,
            content="User prefers TypeScript with Tailwind CSS",
            importance=0.8,
            metadata=MemoryMetadata(
                source="preference_extraction",
                technologies=["typescript", "tailwind"]
            )
        )
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    memory_type: MemoryType
    content: str
    metadata: MemoryMetadata = Field(default_factory=MemoryMetadata)

    # Importance score for prioritization (0.0 = low, 1.0 = high)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)

    # Access tracking for memory decay
    access_count: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None  # Optional expiration for short-term memories

    # Tags for categorization and filtering
    tags: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True

    def to_mongo_dict(self) -> Dict[str, Any]:
        """Convert to MongoDB-compatible dictionary.

        Handles datetime serialization and nested model conversion.
        """
        data = self.model_dump()
        # Ensure memory_type is stored as string
        data["memory_type"] = self.memory_type.value if isinstance(self.memory_type, MemoryType) else self.memory_type
        return data

    @classmethod
    def from_mongo_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create Memory instance from MongoDB document.

        Handles the _id field conversion and type reconstruction.
        """
        if "_id" in data:
            del data["_id"]

        # Convert memory_type string to enum if needed
        if "memory_type" in data and isinstance(data["memory_type"], str):
            data["memory_type"] = MemoryType(data["memory_type"])

        return cls(**data)

    def update_access(self) -> None:
        """Update access tracking when memory is retrieved."""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)

    def decay_importance(self, factor: float = 0.95) -> None:
        """Apply importance decay based on time since last access.

        Args:
            factor: Decay multiplier (default 0.95 = 5% decay)
        """
        self.importance = max(0.1, self.importance * factor)

    def boost_importance(self, boost: float = 0.1) -> None:
        """Boost importance when memory is accessed or reinforced.

        Args:
            boost: Amount to add to importance (default 0.1)
        """
        self.importance = min(1.0, self.importance + boost)


class MemorySearchResult(BaseModel):
    """Result from a memory search operation.

    Includes the memory and a relevance score for ranking.
    """
    memory: Memory
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)

    class Config:
        arbitrary_types_allowed = True


class MemoryConsolidationResult(BaseModel):
    """Result of a memory consolidation operation.

    Tracks what was consolidated and what was discarded.
    """
    consolidated_count: int = 0
    discarded_count: int = 0
    new_long_term_memories: List[str] = Field(default_factory=list)
    discarded_memory_ids: List[str] = Field(default_factory=list)
