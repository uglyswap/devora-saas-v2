"""Persistent Memory Service using Memori SDK

This module provides intelligent, persistent memory for Devora's AI agents
using the Memori SDK. It enables:
- Cross-session memory persistence
- User preference learning
- Project context retention
- Intelligent context retrieval
"""
from typing import Dict, List, Optional, Any
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Check if memori is available
try:
    from memori import Memori
    MEMORI_AVAILABLE = True
except ImportError:
    MEMORI_AVAILABLE = False
    logger.warning("Memori SDK not installed. Run: pip install memorisdk")


# Global instance cache for memory objects
_memory_instances: Dict[str, 'DevoraMemory'] = {}


def get_memory_instance(user_id: str, project_id: Optional[str] = None) -> 'DevoraMemory':
    """Get or create a DevoraMemory instance for a user/project.
    
    This function caches instances to avoid creating multiple connections
    to the database for the same user/project combination.
    
    Args:
        user_id: The unique user identifier
        project_id: Optional project identifier for project-scoped memory
        
    Returns:
        DevoraMemory instance configured for the user/project
    """
    cache_key = f"{user_id}:{project_id or 'global'}"
    
    if cache_key not in _memory_instances:
        _memory_instances[cache_key] = DevoraMemory(user_id, project_id)
    
    return _memory_instances[cache_key]


def clear_memory_cache():
    """Clear the memory instance cache.
    
    Useful for testing or when you want to force reconnection.
    """
    global _memory_instances
    _memory_instances = {}


class DevoraMemory:
    """Intelligent persistent memory for Devora using Memori SDK
    
    Features:
    - Stores user interactions and preferences
    - Retrieves relevant context for new queries
    - Learns from project history
    - Supports multi-user isolation via namespaces
    """
    
    def __init__(self, user_id: str, project_id: Optional[str] = None):
        self.user_id = user_id
        self.project_id = project_id
        self.enabled = False
        self.memori = None
        
        if not MEMORI_AVAILABLE:
            logger.warning("Memory features disabled - Memori SDK not available")
            return
            
        try:
            # Use PostgreSQL (from docker-compose) or SQLite fallback
            db_url = os.getenv("MEMORI_DATABASE_URL") or os.getenv("DATABASE_URL")
            
            if not db_url:
                # Fallback to SQLite for development
                db_url = "sqlite:///devora_memory.db"
                logger.info("Using SQLite for memory storage (dev mode)")
            else:
                logger.info(f"Using PostgreSQL for memory storage")
            
            self.memori = Memori(
                database_connect=db_url,
                conscious_ingest=True,  # Enable working memory
                auto_ingest=True,       # Enable automatic context retrieval
            )
            
            # Set namespace for user isolation
            namespace = f"devora:user:{user_id}"
            if project_id:
                namespace = f"devora:user:{user_id}:project:{project_id}"
            
            self.memori.set_namespace(namespace)
            self.enabled = True
            logger.info(f"Memory initialized for user {user_id}, project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Memori: {e}")
            self.enabled = False
    
    def store_interaction(
        self, 
        user_message: str, 
        assistant_response: str, 
        files_generated: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Store a conversation interaction in memory
        
        Args:
            user_message: The user's request
            assistant_response: What the AI did/responded
            files_generated: List of file names that were generated
            metadata: Additional context to store
            
        Returns:
            True if stored successfully
        """
        if not self.enabled:
            return False
            
        try:
            base_metadata = {
                "project_id": self.project_id,
                "timestamp": datetime.utcnow().isoformat(),
                "files_generated": files_generated or []
            }
            if metadata:
                base_metadata.update(metadata)
            
            # Store user intent/request
            self.memori.add_memory(
                content=f"User requested: {user_message}",
                category="user_request",
                metadata=base_metadata
            )
            
            # Store what was accomplished
            if files_generated and len(files_generated) > 0:
                accomplishment = f"Generated {len(files_generated)} files: {', '.join(files_generated[:5])}"
                if len(files_generated) > 5:
                    accomplishment += f" and {len(files_generated) - 5} more"
                    
                self.memori.add_memory(
                    content=accomplishment,
                    category="accomplishment",
                    metadata=base_metadata
                )
            
            # Store any preferences detected
            preferences = self._extract_preferences(user_message)
            for pref in preferences:
                self.memori.add_memory(
                    content=pref,
                    category="preference",
                    metadata={"project_id": self.project_id}
                )
            
            logger.debug(f"Stored interaction with {len(files_generated or [])} files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    def _extract_preferences(self, message: str) -> List[str]:
        """Extract user preferences from message"""
        preferences = []
        message_lower = message.lower()
        
        # Detect style preferences
        if "dark" in message_lower or "sombre" in message_lower:
            preferences.append("User prefers dark theme/mode")
        if "minimal" in message_lower or "simple" in message_lower:
            preferences.append("User prefers minimal/simple design")
        if "modern" in message_lower or "moderne" in message_lower:
            preferences.append("User prefers modern design")
            
        # Detect tech preferences
        if "typescript" in message_lower or "ts" in message_lower:
            preferences.append("User prefers TypeScript")
        if "tailwind" in message_lower:
            preferences.append("User prefers Tailwind CSS")
        if "supabase" in message_lower:
            preferences.append("User uses Supabase")
        if "stripe" in message_lower:
            preferences.append("User needs Stripe integration")
            
        return preferences
    
    def get_relevant_context(
        self, 
        query: str, 
        limit: int = 5,
        include_preferences: bool = True
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for a query
        
        Args:
            query: The current user query
            limit: Maximum memories to retrieve
            include_preferences: Whether to include learned preferences
            
        Returns:
            List of relevant memory objects
        """
        if not self.enabled:
            return []
            
        try:
            results = []
            
            # Get memories related to the query
            memories = self.memori.search(
                query=query,
                limit=limit
            )
            
            for m in memories:
                results.append({
                    "content": m.content if hasattr(m, 'content') else str(m),
                    "category": getattr(m, 'category', 'general'),
                    "relevance": getattr(m, 'score', 1.0)
                })
            
            # Add user preferences if requested
            if include_preferences:
                prefs = self.get_user_preferences()
                for pref in prefs[:3]:  # Top 3 preferences
                    results.append({
                        "content": pref,
                        "category": "preference",
                        "relevance": 0.8
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    def get_user_preferences(self) -> List[str]:
        """Get learned user preferences"""
        if not self.enabled:
            return []
            
        try:
            prefs = self.memori.search(
                query="user preference",
                filters={"category": "preference"},
                limit=10
            )
            return [p.content if hasattr(p, 'content') else str(p) for p in prefs]
        except Exception as e:
            logger.warning(f"Failed to get preferences: {e}")
            return []
    
    def get_project_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get history for current project"""
        if not self.enabled or not self.project_id:
            return []
            
        try:
            history = self.memori.search(
                query="",
                filters={"project_id": self.project_id},
                limit=limit
            )
            return [
                {
                    "content": h.content if hasattr(h, 'content') else str(h),
                    "category": getattr(h, 'category', 'general'),
                    "timestamp": getattr(h, 'timestamp', None)
                }
                for h in history
            ]
        except Exception as e:
            logger.error(f"Failed to get project history: {e}")
            return []
    
    def clear_project_memory(self) -> bool:
        """Clear all memory for current project"""
        if not self.enabled or not self.project_id:
            return False
            
        try:
            # Note: Memori SDK may have different method name
            if hasattr(self.memori, 'clear_namespace'):
                self.memori.clear_namespace()
            logger.info(f"Cleared memory for project {self.project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False


def get_memory_for_request(
    user_id: str,
    project_id: Optional[str],
    query: str
) -> Dict[str, Any]:
    """Convenience function to get memory context for a request
    
    Returns dict with:
    - context: List of relevant memories
    - preferences: User preferences
    - system_prompt_addition: Ready-to-use context string
    """
    memory = get_memory_instance(user_id, project_id)
    
    if not memory.enabled:
        return {
            "context": [],
            "preferences": [],
            "system_prompt_addition": ""
        }
    
    context = memory.get_relevant_context(query, limit=5)
    preferences = memory.get_user_preferences()
    
    # Build system prompt addition
    prompt_parts = []
    
    if context:
        prompt_parts.append("## Contexte mémorisé:")
        for c in context[:3]:
            prompt_parts.append(f"- {c['content'][:200]}")
    
    if preferences:
        prompt_parts.append("\n## Préférences utilisateur:")
        for p in preferences[:3]:
            prompt_parts.append(f"- {p}")
    
    return {
        "context": context,
        "preferences": preferences,
        "system_prompt_addition": "\n".join(prompt_parts) if prompt_parts else ""
    }
