"""
AI Memory Module - Persistent Memory System for Devora Agents

This module provides a sophisticated memory system for AI agents with:
- Short-term memory: Current conversation context
- Long-term memory: Learned patterns and user preferences
- Episodic memory: Historical generation records

The system uses MongoDB for persistence and supports:
- Semantic search via embeddings
- Memory consolidation (short-term to long-term)
- Automatic forgetting of low-importance memories
- User-isolated namespaces
"""

from .memory_types import Memory, MemoryType, MemoryMetadata
from .memory_store import MemoryStore
from .agent_memory import AgentMemorySystem

__all__ = [
    "Memory",
    "MemoryType",
    "MemoryMetadata",
    "MemoryStore",
    "AgentMemorySystem",
]
