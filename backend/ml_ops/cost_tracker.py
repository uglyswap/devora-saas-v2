"""
Cost Tracking and Optimization

Features:
- Track costs per model, agent, user
- Budget alerts and limits
- Cost optimization recommendations
- Cost forecasting
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CostEntry:
    """Single cost entry"""
    amount: float
    model: str
    agent: str
    user_id: Optional[str]
    tokens_used: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Budget:
    """Budget configuration"""
    name: str
    limit: float
    period: str  # "daily", "weekly", "monthly"
    scope: str  # "global", "user", "model", "agent"
    scope_value: Optional[str] = None  # e.g., user_id, model name
    alert_threshold: float = 0.8  # Alert at 80% of budget


@dataclass
class CostReport:
    """Cost analysis report"""
    total_cost: float = 0.0
    total_requests: int = 0
    avg_cost_per_request: float = 0.0
    cost_by_model: Dict[str, float] = field(default_factory=dict)
    cost_by_agent: Dict[str, float] = field(default_factory=dict)
    cost_by_user: Dict[str, float] = field(default_factory=dict)
    daily_costs: List[Dict[str, Any]] = field(default_factory=list)
    budget_status: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class CostTracker:
    """Track and optimize AI/ML costs"""

    # Updated pricing (cost per 1M tokens)
    MODEL_PRICING = {
        "openai/gpt-4o": {"input": 5.0, "output": 15.0},
        "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
        "anthropic/claude-3-opus": {"input": 15.0, "output": 75.0},
        "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
        "google/gemini-pro-1.5": {"input": 1.25, "output": 5.0},
        "text-embedding-3-small": {"input": 0.02, "output": 0.0},
        "text-embedding-3-large": {"input": 0.13, "output": 0.0},
    }

    def __init__(self, retention_days: int = 90):
        self.retention_days = retention_days

        # Storage
        self._entries: List[CostEntry] = []
        self._budgets: Dict[str, Budget] = {}

        # Cache for quick lookups
        self._total_cost = 0.0
        self._costs_by_model = defaultdict(float)
        self._costs_by_agent = defaultdict(float)
        self._costs_by_user = defaultdict(float)

    def track_cost(
        self,
        amount: float,
        model: str,
        agent: str = "",
        user_id: Optional[str] = None,
        tokens_used: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Track a cost entry"""
        entry = CostEntry(
            amount=amount,
            model=model,
            agent=agent,
            user_id=user_id,
            tokens_used=tokens_used,
            metadata=metadata or {},
        )

        self._entries.append(entry)

        # Update caches
        self._total_cost += amount
        self._costs_by_model[model] += amount
        if agent:
            self._costs_by_agent[agent] += amount
        if user_id:
            self._costs_by_user[user_id] += amount

        # Check budgets
        self._check_budgets(entry)

        # Cleanup periodically
        if len(self._entries) % 1000 == 0:
            self._cleanup_old_entries()

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost for a request"""
        pricing = self.MODEL_PRICING.get(model, {"input": 5.0, "output": 15.0})

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def add_budget(self, budget: Budget):
        """Add a budget"""
        self._budgets[budget.name] = budget
        logger.info(f"[CostTracker] Added budget: {budget.name} (${budget.limit} per {budget.period})")

    def get_budget_status(self, budget_name: str) -> Optional[Dict[str, Any]]:
        """Get current budget status"""
        budget = self._budgets.get(budget_name)
        if not budget:
            return None

        # Calculate period
        now = datetime.utcnow()
        if budget.period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == "weekly":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now - timedelta(days=1)

        # Filter entries
        filtered_entries = [
            e for e in self._entries
            if e.timestamp >= start
        ]

        # Apply scope filter
        if budget.scope == "model" and budget.scope_value:
            filtered_entries = [e for e in filtered_entries if e.model == budget.scope_value]
        elif budget.scope == "agent" and budget.scope_value:
            filtered_entries = [e for e in filtered_entries if e.agent == budget.scope_value]
        elif budget.scope == "user" and budget.scope_value:
            filtered_entries = [e for e in filtered_entries if e.user_id == budget.scope_value]

        # Calculate total
        spent = sum(e.amount for e in filtered_entries)
        remaining = budget.limit - spent
        percentage = (spent / budget.limit) * 100 if budget.limit > 0 else 0

        return {
            "budget_name": budget.name,
            "limit": budget.limit,
            "spent": spent,
            "remaining": remaining,
            "percentage": percentage,
            "period": budget.period,
            "scope": budget.scope,
            "alert_triggered": percentage >= (budget.alert_threshold * 100),
        }

    def _check_budgets(self, entry: CostEntry):
        """Check if any budgets are exceeded"""
        for budget in self._budgets.values():
            status = self.get_budget_status(budget.name)
            if not status:
                continue

            # Alert if threshold exceeded
            if status["alert_triggered"]:
                logger.warning(
                    f"[CostTracker] BUDGET ALERT: {budget.name} at {status['percentage']:.1f}% "
                    f"(${status['spent']:.2f} / ${budget.limit:.2f})"
                )

    def get_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> CostReport:
        """Generate cost analysis report"""
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(days=30)
        if end_time is None:
            end_time = datetime.utcnow()

        # Filter entries
        filtered_entries = [
            e for e in self._entries
            if start_time <= e.timestamp <= end_time
        ]

        report = CostReport()

        # Calculate totals
        report.total_cost = sum(e.amount for e in filtered_entries)
        report.total_requests = len(filtered_entries)
        if report.total_requests > 0:
            report.avg_cost_per_request = report.total_cost / report.total_requests

        # Group by dimensions
        cost_by_model = defaultdict(float)
        cost_by_agent = defaultdict(float)
        cost_by_user = defaultdict(float)
        cost_by_day = defaultdict(float)

        for entry in filtered_entries:
            cost_by_model[entry.model] += entry.amount
            if entry.agent:
                cost_by_agent[entry.agent] += entry.amount
            if entry.user_id:
                cost_by_user[entry.user_id] += entry.amount

            day = entry.timestamp.date().isoformat()
            cost_by_day[day] += entry.amount

        report.cost_by_model = dict(cost_by_model)
        report.cost_by_agent = dict(cost_by_agent)
        report.cost_by_user = dict(cost_by_user)

        # Daily breakdown
        report.daily_costs = [
            {"date": date, "cost": cost}
            for date, cost in sorted(cost_by_day.items())
        ]

        # Budget status
        report.budget_status = {
            name: self.get_budget_status(name)
            for name in self._budgets.keys()
        }

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: CostReport) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []

        # Check for expensive models
        if report.cost_by_model:
            most_expensive_model = max(report.cost_by_model.items(), key=lambda x: x[1])
            model_name, model_cost = most_expensive_model

            if "gpt-4" in model_name and model_cost > report.total_cost * 0.5:
                recommendations.append(
                    f"Consider using GPT-4o-mini for simpler tasks. "
                    f"{model_name} accounts for {(model_cost/report.total_cost)*100:.1f}% of costs."
                )

            if "claude-3-opus" in model_name:
                recommendations.append(
                    "Consider using Claude 3.5 Sonnet or Haiku for cost savings "
                    "on tasks that don't require Opus-level performance."
                )

        # Check for high-frequency users
        if report.cost_by_user:
            total_users = len(report.cost_by_user)
            sorted_users = sorted(report.cost_by_user.items(), key=lambda x: x[1], reverse=True)

            if total_users > 10:
                top_10_cost = sum(cost for _, cost in sorted_users[:10])
                if top_10_cost > report.total_cost * 0.8:
                    recommendations.append(
                        "Top 10 users account for 80%+ of costs. "
                        "Consider implementing user-specific rate limits or tiered pricing."
                    )

        # Check for caching opportunities
        if report.avg_cost_per_request > 0.01:
            recommendations.append(
                f"Average cost per request is ${report.avg_cost_per_request:.4f}. "
                "Implement response caching to reduce duplicate LLM calls."
            )

        # Check for RAG opportunities
        if report.total_requests > 1000:
            recommendations.append(
                "With high request volume, consider implementing RAG "
                "to reduce context size and token usage."
            )

        return recommendations

    def forecast_costs(
        self,
        days_ahead: int = 30,
    ) -> Dict[str, Any]:
        """Forecast future costs based on historical data"""
        # Get last 30 days
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)

        historical_entries = [
            e for e in self._entries
            if start_time <= e.timestamp <= end_time
        ]

        if not historical_entries:
            return {
                "forecast_days": days_ahead,
                "estimated_cost": 0.0,
                "confidence": "low",
                "note": "Insufficient historical data",
            }

        # Calculate daily average
        total_cost = sum(e.amount for e in historical_entries)
        daily_avg = total_cost / 30

        # Project forward
        estimated_cost = daily_avg * days_ahead

        return {
            "forecast_days": days_ahead,
            "estimated_cost": estimated_cost,
            "daily_average": daily_avg,
            "confidence": "medium" if len(historical_entries) > 100 else "low",
            "based_on_days": 30,
        }

    def get_top_spenders(
        self,
        limit: int = 10,
        dimension: str = "user",  # "user", "model", "agent"
    ) -> List[Dict[str, Any]]:
        """Get top spenders by dimension"""
        if dimension == "user":
            costs = self._costs_by_user
        elif dimension == "model":
            costs = self._costs_by_model
        elif dimension == "agent":
            costs = self._costs_by_agent
        else:
            return []

        sorted_costs = sorted(costs.items(), key=lambda x: x[1], reverse=True)

        return [
            {"name": name, "total_cost": cost}
            for name, cost in sorted_costs[:limit]
        ]

    def _cleanup_old_entries(self):
        """Remove entries older than retention period"""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        original_count = len(self._entries)

        self._entries = [e for e in self._entries if e.timestamp >= cutoff]

        removed = original_count - len(self._entries)
        if removed > 0:
            logger.info(f"[CostTracker] Cleaned up {removed} old entries")

    def export_data(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Export cost data for external analysis"""
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(days=30)
        if end_time is None:
            end_time = datetime.utcnow()

        filtered_entries = [
            e for e in self._entries
            if start_time <= e.timestamp <= end_time
        ]

        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "amount": e.amount,
                "model": e.model,
                "agent": e.agent,
                "user_id": e.user_id,
                "tokens_used": e.tokens_used,
                "metadata": e.metadata,
            }
            for e in filtered_entries
        ]

    def reset(self):
        """Reset all data (useful for testing)"""
        self._entries.clear()
        self._total_cost = 0.0
        self._costs_by_model.clear()
        self._costs_by_agent.clear()
        self._costs_by_user.clear()
        logger.info("[CostTracker] Reset all data")
