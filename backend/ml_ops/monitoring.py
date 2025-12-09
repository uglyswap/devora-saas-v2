"""
ML Monitoring System

Tracks:
- Model performance metrics
- Latency and throughput
- Error rates and types
- Token usage
- Cost per request
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics to track"""
    LATENCY = "latency"
    COST = "cost"
    TOKENS = "tokens"
    ERROR = "error"
    SUCCESS = "success"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"


@dataclass
class MetricEvent:
    """Single metric event"""
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    model: str = ""
    agent: str = ""
    user_id: Optional[str] = None


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a time period"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

    avg_latency_ms: float = 0.0
    avg_cost_per_request: float = 0.0
    avg_tokens_per_request: float = 0.0
    success_rate: float = 0.0
    cache_hit_rate: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0

    error_breakdown: Dict[str, int] = field(default_factory=dict)
    model_breakdown: Dict[str, int] = field(default_factory=dict)


class MLMonitor:
    """Monitor ML/AI operations"""

    def __init__(
        self,
        retention_days: int = 30,
        alert_thresholds: Optional[Dict[str, float]] = None,
    ):
        self.retention_days = retention_days
        self.alert_thresholds = alert_thresholds or {
            "error_rate": 0.05,  # Alert if >5% errors
            "avg_latency_ms": 10000,  # Alert if avg latency >10s
            "cost_per_request": 0.50,  # Alert if cost >$0.50 per request
        }

        # In-memory storage (for production, use a database)
        self._events: List[MetricEvent] = []
        self._latency_values: List[float] = []

        # Real-time counters
        self._counters = defaultdict(int)
        self._sums = defaultdict(float)

    def track_event(self, event: MetricEvent):
        """Track a metric event"""
        self._events.append(event)

        # Update real-time counters
        if event.metric_type == MetricType.LATENCY:
            self._latency_values.append(event.value)
            self._sums["latency"] += event.value

        elif event.metric_type == MetricType.COST:
            self._sums["cost"] += event.value

        elif event.metric_type == MetricType.TOKENS:
            self._sums["tokens"] += event.value

        elif event.metric_type == MetricType.ERROR:
            self._counters["errors"] += 1
            error_type = event.metadata.get("error_type", "unknown")
            self._counters[f"error_{error_type}"] += 1

        elif event.metric_type == MetricType.SUCCESS:
            self._counters["success"] += 1

        elif event.metric_type == MetricType.CACHE_HIT:
            self._counters["cache_hits"] += 1

        elif event.metric_type == MetricType.CACHE_MISS:
            self._counters["cache_misses"] += 1

        # Increment request counter
        self._counters["total_requests"] += 1

        # Check alerts
        self._check_alerts()

        # Clean old events periodically
        if self._counters["total_requests"] % 1000 == 0:
            self._cleanup_old_events()

    def track_request(
        self,
        success: bool,
        latency_ms: float,
        cost: float = 0.0,
        tokens: int = 0,
        model: str = "",
        agent: str = "",
        error_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Convenience method to track a complete request

        Args:
            success: Whether the request succeeded
            latency_ms: Request latency in milliseconds
            cost: Cost of the request
            tokens: Number of tokens used
            model: Model name
            agent: Agent name
            error_type: Error type if failed
            metadata: Additional metadata
        """
        metadata = metadata or {}

        # Track success/error
        if success:
            self.track_event(MetricEvent(
                metric_type=MetricType.SUCCESS,
                value=1,
                model=model,
                agent=agent,
                metadata=metadata,
            ))
        else:
            self.track_event(MetricEvent(
                metric_type=MetricType.ERROR,
                value=1,
                model=model,
                agent=agent,
                metadata={**metadata, "error_type": error_type or "unknown"},
            ))

        # Track latency
        self.track_event(MetricEvent(
            metric_type=MetricType.LATENCY,
            value=latency_ms,
            model=model,
            agent=agent,
            metadata=metadata,
        ))

        # Track cost
        if cost > 0:
            self.track_event(MetricEvent(
                metric_type=MetricType.COST,
                value=cost,
                model=model,
                agent=agent,
                metadata=metadata,
            ))

        # Track tokens
        if tokens > 0:
            self.track_event(MetricEvent(
                metric_type=MetricType.TOKENS,
                value=tokens,
                model=model,
                agent=agent,
                metadata=metadata,
            ))

    def get_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        model: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> AggregatedMetrics:
        """
        Get aggregated metrics for a time period

        Args:
            start_time: Start of time range (default: 24h ago)
            end_time: End of time range (default: now)
            model: Filter by model
            agent: Filter by agent

        Returns:
            Aggregated metrics
        """
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if end_time is None:
            end_time = datetime.utcnow()

        # Filter events
        filtered_events = [
            e for e in self._events
            if start_time <= e.timestamp <= end_time
            and (model is None or e.model == model)
            and (agent is None or e.agent == agent)
        ]

        # Aggregate
        metrics = AggregatedMetrics()

        latencies = []
        costs = []
        tokens_list = []
        error_types = defaultdict(int)
        models = defaultdict(int)

        for event in filtered_events:
            if event.metric_type == MetricType.LATENCY:
                latencies.append(event.value)

            elif event.metric_type == MetricType.COST:
                costs.append(event.value)
                metrics.total_cost += event.value

            elif event.metric_type == MetricType.TOKENS:
                tokens_list.append(int(event.value))
                metrics.total_tokens += int(event.value)

            elif event.metric_type == MetricType.ERROR:
                metrics.failed_requests += 1
                error_type = event.metadata.get("error_type", "unknown")
                error_types[error_type] += 1

            elif event.metric_type == MetricType.SUCCESS:
                metrics.successful_requests += 1

            elif event.metric_type == MetricType.CACHE_HIT:
                metrics.cache_hits += 1

            elif event.metric_type == MetricType.CACHE_MISS:
                metrics.cache_misses += 1

            # Track model usage
            if event.model:
                models[event.model] += 1

        # Calculate aggregates
        metrics.total_requests = metrics.successful_requests + metrics.failed_requests

        if latencies:
            metrics.total_latency_ms = sum(latencies)
            metrics.avg_latency_ms = statistics.mean(latencies)
            metrics.p50_latency_ms = statistics.median(latencies)
            sorted_latencies = sorted(latencies)
            metrics.p95_latency_ms = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            metrics.p99_latency_ms = sorted_latencies[int(len(sorted_latencies) * 0.99)]

        if metrics.total_requests > 0:
            metrics.success_rate = metrics.successful_requests / metrics.total_requests
            metrics.avg_cost_per_request = metrics.total_cost / metrics.total_requests

            if tokens_list:
                metrics.avg_tokens_per_request = sum(tokens_list) / metrics.total_requests

            total_cache_requests = metrics.cache_hits + metrics.cache_misses
            if total_cache_requests > 0:
                metrics.cache_hit_rate = metrics.cache_hits / total_cache_requests

        metrics.error_breakdown = dict(error_types)
        metrics.model_breakdown = dict(models)

        return metrics

    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics (lightweight)"""
        total_requests = self._counters["total_requests"]

        return {
            "total_requests": total_requests,
            "successful_requests": self._counters["success"],
            "failed_requests": self._counters["errors"],
            "cache_hits": self._counters["cache_hits"],
            "cache_misses": self._counters["cache_misses"],
            "total_cost": self._sums["cost"],
            "total_tokens": int(self._sums["tokens"]),
            "total_latency_ms": self._sums["latency"],
            "avg_latency_ms": (
                self._sums["latency"] / len(self._latency_values)
                if self._latency_values
                else 0
            ),
            "success_rate": (
                self._counters["success"] / total_requests
                if total_requests > 0
                else 0
            ),
        }

    def _check_alerts(self):
        """Check if any alert thresholds are exceeded"""
        stats = self.get_real_time_stats()

        if stats["total_requests"] < 10:  # Need minimum data
            return

        # Check error rate
        if stats["success_rate"] < (1 - self.alert_thresholds["error_rate"]):
            error_rate = 1 - stats["success_rate"]
            logger.warning(
                f"[MLMonitor] ALERT: High error rate: {error_rate:.2%} "
                f"(threshold: {self.alert_thresholds['error_rate']:.2%})"
            )

        # Check latency
        if stats["avg_latency_ms"] > self.alert_thresholds["avg_latency_ms"]:
            logger.warning(
                f"[MLMonitor] ALERT: High latency: {stats['avg_latency_ms']:.0f}ms "
                f"(threshold: {self.alert_thresholds['avg_latency_ms']:.0f}ms)"
            )

        # Check cost
        avg_cost = stats["total_cost"] / stats["total_requests"] if stats["total_requests"] > 0 else 0
        if avg_cost > self.alert_thresholds["cost_per_request"]:
            logger.warning(
                f"[MLMonitor] ALERT: High cost per request: ${avg_cost:.4f} "
                f"(threshold: ${self.alert_thresholds['cost_per_request']:.4f})"
            )

    def _cleanup_old_events(self):
        """Remove events older than retention period"""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        original_count = len(self._events)

        self._events = [e for e in self._events if e.timestamp >= cutoff]

        removed = original_count - len(self._events)
        if removed > 0:
            logger.info(f"[MLMonitor] Cleaned up {removed} old events")

    def export_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Export raw metrics for external analysis"""
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(days=1)
        if end_time is None:
            end_time = datetime.utcnow()

        filtered_events = [
            e for e in self._events
            if start_time <= e.timestamp <= end_time
        ]

        return [
            {
                "metric_type": e.metric_type,
                "value": e.value,
                "timestamp": e.timestamp.isoformat(),
                "model": e.model,
                "agent": e.agent,
                "metadata": e.metadata,
            }
            for e in filtered_events
        ]

    def reset(self):
        """Reset all metrics (useful for testing)"""
        self._events.clear()
        self._latency_values.clear()
        self._counters.clear()
        self._sums.clear()
        logger.info("[MLMonitor] Reset all metrics")
