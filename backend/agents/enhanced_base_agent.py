"""
Enhanced Base Agent with AI/ML Infrastructure Integration

This is an enhanced version of BaseAgent that integrates:
- Advanced LLM service with retry logic
- Response caching
- Cost tracking
- Performance monitoring
- Prompt templates
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
import time

# Import AI/ML infrastructure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ai.llm_service import LLMService, LLMConfig, LLMProvider
from ai.cache import ResponseCache
from ai.prompts.template_manager import PromptTemplateManager
from ml_ops.monitoring import MLMonitor
from ml_ops.cost_tracker import CostTracker

logger = logging.getLogger(__name__)


class EnhancedBaseAgent(ABC):
    """
    Enhanced base class for all agents with AI/ML infrastructure integration

    Features:
    - Advanced LLM service with retry logic and failover
    - Automatic response caching
    - Cost tracking per agent
    - Performance monitoring
    - Prompt template management
    """

    # Shared infrastructure instances (initialized once)
    _llm_service: Optional[LLMService] = None
    _cache: Optional[ResponseCache] = None
    _monitor: Optional[MLMonitor] = None
    _cost_tracker: Optional[CostTracker] = None
    _template_manager: Optional[PromptTemplateManager] = None
    _initialized = False

    @classmethod
    async def initialize_infrastructure(
        cls,
        api_key: str,
        model: str = "openai/gpt-4o",
        enable_cache: bool = True,
        enable_monitoring: bool = True,
        enable_cost_tracking: bool = True,
    ):
        """
        Initialize shared AI/ML infrastructure (call once at startup)

        Args:
            api_key: OpenRouter API key
            model: Default model to use
            enable_cache: Enable response caching
            enable_monitoring: Enable performance monitoring
            enable_cost_tracking: Enable cost tracking
        """
        if cls._initialized:
            logger.info("[EnhancedAgent] Infrastructure already initialized")
            return

        logger.info("[EnhancedAgent] Initializing AI/ML infrastructure...")

        # Initialize LLM service
        config = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            api_key=api_key,
            model=model,
            max_retries=3,
            enable_cost_tracking=enable_cost_tracking,
            fallback_models=["openai/gpt-4o-mini", "anthropic/claude-3-haiku"],
        )
        cls._llm_service = LLMService(config)

        # Initialize cache
        if enable_cache:
            cls._cache = ResponseCache(
                max_size=1000,
                default_ttl_seconds=3600,  # 1 hour
            )

        # Initialize monitoring
        if enable_monitoring:
            cls._monitor = MLMonitor(retention_days=30)

        # Initialize cost tracking
        if enable_cost_tracking:
            cls._cost_tracker = CostTracker(retention_days=90)

        # Initialize template manager
        cls._template_manager = PromptTemplateManager()

        cls._initialized = True
        logger.info("[EnhancedAgent] Infrastructure initialized successfully")

    def __init__(self, name: str, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialize agent

        Args:
            name: Agent name
            api_key: API key (used for initialization if not already done)
            model: Model to use
        """
        self.name = name
        self.api_key = api_key
        self.model = model
        self.memory: List[Dict[str, Any]] = []

        # Stats for this agent
        self._agent_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "total_cost": 0.0,
            "total_latency_ms": 0.0,
        }

    def add_to_memory(self, role: str, content: str):
        """Add a message to agent's memory"""
        self.memory.append({
            "role": role,
            "content": content
        })

    def get_memory(self) -> List[Dict[str, Any]]:
        """Get agent's conversation memory"""
        return self.memory

    def clear_memory(self):
        """Clear agent's memory"""
        self.memory = []

    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        use_cache: bool = True,
        **kwargs
    ) -> str:
        """
        Call LLM with enhanced features

        Args:
            messages: List of messages
            system_prompt: Optional system prompt
            use_cache: Whether to use caching
            **kwargs: Additional arguments for LLM

        Returns:
            LLM response text
        """
        start_time = time.time()

        # Check cache first
        if use_cache and self._cache:
            cached = self._cache.get(
                messages,
                system_prompt=system_prompt,
                model=self.model,
            )
            if cached:
                self._agent_stats["cache_hits"] += 1
                logger.debug(f"[{self.name}] Cache HIT")

                # Track cache hit in monitoring
                if self._monitor:
                    from ml_ops.monitoring import MetricType, MetricEvent
                    self._monitor.track_event(MetricEvent(
                        metric_type=MetricType.CACHE_HIT,
                        value=1,
                        agent=self.name,
                    ))

                return cached

        # Call LLM
        try:
            if not self._llm_service:
                raise RuntimeError(
                    "Infrastructure not initialized. "
                    "Call EnhancedBaseAgent.initialize_infrastructure() first."
                )

            # Use the shared LLM service
            response, stats = await self._llm_service.complete(
                messages=messages,
                system_prompt=system_prompt,
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000

            # Update agent stats
            self._agent_stats["total_requests"] += 1
            self._agent_stats["total_cost"] += stats.estimated_cost
            self._agent_stats["total_latency_ms"] += latency_ms

            # Cache response
            if use_cache and self._cache:
                self._cache.set(
                    response,
                    messages,
                    system_prompt=system_prompt,
                    model=self.model,
                )

            # Track in monitoring
            if self._monitor:
                self._monitor.track_request(
                    success=True,
                    latency_ms=latency_ms,
                    cost=stats.estimated_cost,
                    tokens=stats.total_tokens,
                    model=self.model,
                    agent=self.name,
                )

            # Track cost
            if self._cost_tracker:
                self._cost_tracker.track_cost(
                    amount=stats.estimated_cost,
                    model=self.model,
                    agent=self.name,
                    tokens_used=stats.total_tokens,
                )

            logger.debug(
                f"[{self.name}] LLM call: {stats.total_tokens} tokens, "
                f"${stats.estimated_cost:.4f}, {latency_ms:.0f}ms"
            )

            return response

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000

            logger.error(f"[{self.name}] LLM call failed: {str(e)}")

            # Track error in monitoring
            if self._monitor:
                self._monitor.track_request(
                    success=False,
                    latency_ms=latency_ms,
                    cost=0.0,
                    tokens=0,
                    model=self.model,
                    agent=self.name,
                    error_type=type(e).__name__,
                )

            raise

    def get_template(self, template_name: str) -> Optional[str]:
        """
        Get a prompt template

        Args:
            template_name: Name of the template

        Returns:
            Template object or None
        """
        if self._template_manager:
            return self._template_manager.get_template(template_name)
        return None

    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Render a prompt template with variables

        Args:
            template_name: Name of the template
            **kwargs: Template variables

        Returns:
            Rendered template string
        """
        if self._template_manager:
            return self._template_manager.render(template_name, **kwargs)
        raise RuntimeError("Template manager not initialized")

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for this agent"""
        stats = self._agent_stats.copy()

        if stats["total_requests"] > 0:
            stats["avg_cost"] = stats["total_cost"] / stats["total_requests"]
            stats["avg_latency_ms"] = stats["total_latency_ms"] / stats["total_requests"]
            stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_requests"]
        else:
            stats["avg_cost"] = 0.0
            stats["avg_latency_ms"] = 0.0
            stats["cache_hit_rate"] = 0.0

        return stats

    @classmethod
    def get_global_stats(cls) -> Dict[str, Any]:
        """Get global statistics across all agents"""
        stats = {}

        if cls._llm_service:
            stats["llm"] = cls._llm_service.get_stats()

        if cls._cache:
            stats["cache"] = cls._cache.get_metrics()

        if cls._monitor:
            stats["monitoring"] = cls._monitor.get_real_time_stats()

        if cls._cost_tracker:
            stats["cost"] = {
                "total_cost": cls._cost_tracker._total_cost,
                "costs_by_model": dict(cls._cost_tracker._costs_by_model),
                "costs_by_agent": dict(cls._cost_tracker._costs_by_agent),
            }

        return stats

    @classmethod
    async def cleanup(cls):
        """Cleanup shared resources (call at shutdown)"""
        if cls._llm_service:
            await cls._llm_service.close()

        logger.info("[EnhancedAgent] Infrastructure cleaned up")

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task (must be implemented by subclasses)"""
        pass


# ═══════════════════════════════════════════════════════════════
# Example: Enhanced Coder Agent
# ═══════════════════════════════════════════════════════════════

class EnhancedCoderAgent(EnhancedBaseAgent):
    """Enhanced coder agent with template support"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code using templates

        Args:
            task: Task dict with 'type' and parameters

        Returns:
            Result dict with generated code
        """
        task_type = task.get("type", "component")

        try:
            if task_type == "component":
                # Use component template
                prompt = self.render_template(
                    "generate_component",
                    component_name=task.get("name", "MyComponent"),
                    description=task.get("description", "A React component"),
                    props=task.get("props", "{}"),
                )

            elif task_type == "api":
                # Use API route template
                prompt = self.render_template(
                    "generate_api_route",
                    route_path=task.get("path", "/api/example"),
                    method=task.get("method", "GET"),
                    description=task.get("description", "An API endpoint"),
                    auth_required=task.get("auth_required", "true"),
                )

            else:
                # Generic code generation
                prompt = f"Generate {task_type}: {task.get('description', '')}"

            # Generate code
            code = await self.call_llm(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are an expert software engineer. Generate clean, production-ready code.",
            )

            return {
                "success": True,
                "code": code,
                "stats": self.get_agent_stats(),
            }

        except Exception as e:
            logger.error(f"[EnhancedCoder] Error: {e}")
            return {
                "success": False,
                "error": str(e),
            }
