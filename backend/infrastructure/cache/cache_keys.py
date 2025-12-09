"""
Standardized Cache Key Management

Provides a centralized definition of all cache keys used in the application.
This ensures consistency and prevents key collisions across the codebase.

Usage:
    from infrastructure.cache import CacheKeys

    key = CacheKeys.user(user_id="123")
    # Returns: "user:123"

    key = CacheKeys.project_files(project_id="abc", path="/src")
    # Returns: "project:abc:files:/src"
"""

from typing import Optional
import hashlib


class CacheKeys:
    """
    Centralized cache key definitions.

    All keys follow the pattern: entity:id[:subentity:...]

    Naming conventions:
    - Use lowercase
    - Use colons (:) as separators
    - Entity first, then identifiers
    - Be specific to avoid collisions

    TTL recommendations (in seconds):
    - User data: 300-600 (5-10 min)
    - Project metadata: 300 (5 min)
    - Project files: 60-300 (1-5 min)
    - LLM responses: 3600+ (1h+)
    - Rate limits: 60 (1 min)
    - Sessions: 86400 (24h)
    """

    # ========================
    # Default TTLs (seconds)
    # ========================

    TTL_SHORT = 60          # 1 minute
    TTL_MEDIUM = 300        # 5 minutes
    TTL_LONG = 3600         # 1 hour
    TTL_EXTENDED = 86400    # 24 hours
    TTL_WEEK = 604800       # 7 days

    # ========================
    # User-related keys
    # ========================

    @staticmethod
    def user(user_id: str) -> str:
        """User profile data."""
        return f"user:{user_id}"

    @staticmethod
    def user_projects(user_id: str) -> str:
        """List of user's projects."""
        return f"user:{user_id}:projects"

    @staticmethod
    def user_settings(user_id: str) -> str:
        """User settings/preferences."""
        return f"user:{user_id}:settings"

    @staticmethod
    def user_subscription(user_id: str) -> str:
        """User subscription details."""
        return f"user:{user_id}:subscription"

    @staticmethod
    def user_usage(user_id: str, period: str = "daily") -> str:
        """User usage metrics (daily/weekly/monthly)."""
        return f"user:{user_id}:usage:{period}"

    @staticmethod
    def user_pattern(user_id: str) -> str:
        """Pattern to match all keys for a user."""
        return f"user:{user_id}:*"

    # ========================
    # Project-related keys
    # ========================

    @staticmethod
    def project(project_id: str) -> str:
        """Project metadata."""
        return f"project:{project_id}"

    @staticmethod
    def project_files(project_id: str, path: Optional[str] = None) -> str:
        """Project file tree or specific path."""
        if path:
            return f"project:{project_id}:files:{path}"
        return f"project:{project_id}:files"

    @staticmethod
    def project_agents(project_id: str) -> str:
        """Project agent configurations."""
        return f"project:{project_id}:agents"

    @staticmethod
    def project_tasks(project_id: str) -> str:
        """Project tasks list."""
        return f"project:{project_id}:tasks"

    @staticmethod
    def project_history(project_id: str) -> str:
        """Project generation history."""
        return f"project:{project_id}:history"

    @staticmethod
    def project_pattern(project_id: str) -> str:
        """Pattern to match all keys for a project."""
        return f"project:{project_id}:*"

    # ========================
    # Task-related keys
    # ========================

    @staticmethod
    def task(task_id: str) -> str:
        """Task details."""
        return f"task:{task_id}"

    @staticmethod
    def task_status(task_id: str) -> str:
        """Task execution status."""
        return f"task:{task_id}:status"

    @staticmethod
    def task_result(task_id: str) -> str:
        """Task execution result."""
        return f"task:{task_id}:result"

    # ========================
    # Generation/LLM keys
    # ========================

    @staticmethod
    def llm_response(prompt_hash: str, model: str = "default") -> str:
        """Cached LLM response."""
        return f"llm:{model}:{prompt_hash}"

    @staticmethod
    def generation(generation_id: str) -> str:
        """Generation job details."""
        return f"generation:{generation_id}"

    @staticmethod
    def generation_status(generation_id: str) -> str:
        """Generation status updates."""
        return f"generation:{generation_id}:status"

    @staticmethod
    def code_context(project_id: str, context_hash: str) -> str:
        """Cached code context for RAG."""
        return f"context:{project_id}:{context_hash}"

    # ========================
    # Rate limiting keys
    # ========================

    @staticmethod
    def rate_limit(identifier: str, action: str = "api") -> str:
        """Rate limit counter for an identifier (user_id, ip, api_key)."""
        return f"ratelimit:{action}:{identifier}"

    @staticmethod
    def rate_limit_window(identifier: str, window: str, action: str = "api") -> str:
        """Rate limit counter for a specific time window."""
        return f"ratelimit:{action}:{identifier}:{window}"

    # ========================
    # Session/Auth keys
    # ========================

    @staticmethod
    def session(session_id: str) -> str:
        """User session data."""
        return f"session:{session_id}"

    @staticmethod
    def refresh_token(token_hash: str) -> str:
        """Refresh token validation."""
        return f"refresh:{token_hash}"

    @staticmethod
    def api_key(key_hash: str) -> str:
        """API key validation and metadata."""
        return f"apikey:{key_hash}"

    # ========================
    # Analytics/Metrics keys
    # ========================

    @staticmethod
    def metrics(metric_name: str, date: str) -> str:
        """Daily metric aggregation."""
        return f"metrics:{metric_name}:{date}"

    @staticmethod
    def leaderboard(category: str) -> str:
        """Leaderboard/ranking data."""
        return f"leaderboard:{category}"

    # ========================
    # Feature flags / Config
    # ========================

    @staticmethod
    def feature_flag(flag_name: str) -> str:
        """Feature flag status."""
        return f"feature:{flag_name}"

    @staticmethod
    def config(config_key: str) -> str:
        """Dynamic configuration."""
        return f"config:{config_key}"

    # ========================
    # Utility methods
    # ========================

    @staticmethod
    def hash_content(content: str) -> str:
        """Generate a hash for content-based cache keys."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @staticmethod
    def hash_prompt(messages: list, system_prompt: str = "", model: str = "") -> str:
        """Generate a hash for LLM prompts (for response caching)."""
        import json
        key_data = {
            "messages": messages,
            "system": system_prompt,
            "model": model,
        }
        return hashlib.sha256(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()[:16]

    @classmethod
    def all_patterns(cls) -> dict:
        """Return all available pattern generators for documentation."""
        return {
            "user": "user:{user_id}:*",
            "project": "project:{project_id}:*",
            "task": "task:{task_id}:*",
            "generation": "generation:{generation_id}:*",
            "llm": "llm:*",
            "ratelimit": "ratelimit:*",
            "session": "session:*",
            "metrics": "metrics:*",
        }
