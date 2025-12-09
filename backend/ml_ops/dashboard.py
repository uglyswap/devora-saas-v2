"""
ML Ops Dashboard Manager

Aggregates metrics from monitoring, cost tracking, and A/B testing
to provide a unified dashboard view.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from .monitoring import MLMonitor, AggregatedMetrics
from .cost_tracker import CostTracker
from .ab_testing import ABTester

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    refresh_interval_seconds: int = 60
    metrics_retention_days: int = 90
    show_cost_forecast: bool = True
    show_ab_tests: bool = True
    alert_email: Optional[str] = None


class DashboardManager:
    """Manage ML Ops dashboard and metrics"""

    def __init__(
        self,
        monitor: MLMonitor,
        cost_tracker: CostTracker,
        ab_tester: Optional[ABTester] = None,
        config: Optional[DashboardConfig] = None,
    ):
        self.monitor = monitor
        self.cost_tracker = cost_tracker
        self.ab_tester = ab_tester or ABTester()
        self.config = config or DashboardConfig()

    def get_overview(self) -> Dict[str, Any]:
        """
        Get high-level overview of all metrics

        Returns:
            Dashboard overview with key metrics
        """
        # Real-time stats from monitor
        real_time = self.monitor.get_real_time_stats()

        # Last 24h metrics
        metrics_24h = self.monitor.get_metrics(
            start_time=datetime.utcnow() - timedelta(hours=24),
            end_time=datetime.utcnow(),
        )

        # Last 7d metrics for trends
        metrics_7d = self.monitor.get_metrics(
            start_time=datetime.utcnow() - timedelta(days=7),
            end_time=datetime.utcnow(),
        )

        # Cost report
        cost_report = self.cost_tracker.get_report(
            start_time=datetime.utcnow() - timedelta(days=30),
        )

        # Running experiments
        running_experiments = self.ab_tester.list_experiments(status="running")
        experiment_summaries = [
            self.ab_tester.get_experiment_summary(exp_name)
            for exp_name in running_experiments
        ]

        return {
            "overview": {
                "total_requests": real_time["total_requests"],
                "success_rate": real_time["success_rate"],
                "avg_latency_ms": real_time["avg_latency_ms"],
                "total_cost": real_time["total_cost"],
                "cache_hit_rate": (
                    real_time["cache_hits"] / (real_time["cache_hits"] + real_time["cache_misses"])
                    if (real_time["cache_hits"] + real_time["cache_misses"]) > 0
                    else 0
                ),
            },
            "last_24h": {
                "requests": metrics_24h.total_requests,
                "success_rate": metrics_24h.success_rate,
                "avg_latency_ms": metrics_24h.avg_latency_ms,
                "p95_latency_ms": metrics_24h.p95_latency_ms,
                "total_cost": metrics_24h.total_cost,
                "total_tokens": metrics_24h.total_tokens,
            },
            "trends_7d": {
                "requests": metrics_7d.total_requests,
                "avg_cost_per_request": metrics_7d.avg_cost_per_request,
                "error_rate": 1 - metrics_7d.success_rate,
            },
            "cost_summary": {
                "total_cost_30d": cost_report.total_cost,
                "avg_cost_per_request": cost_report.avg_cost_per_request,
                "top_models": list(cost_report.cost_by_model.items())[:5],
                "budget_alerts": [
                    status for status in cost_report.budget_status.values()
                    if status and status.get("alert_triggered")
                ],
            },
            "experiments": {
                "active_count": len(running_experiments),
                "experiments": experiment_summaries,
            },
            "recommendations": cost_report.recommendations,
        }

    def get_detailed_metrics(
        self,
        time_range: str = "24h",  # "1h", "24h", "7d", "30d"
        model: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get detailed metrics for a specific time range

        Args:
            time_range: Time range for metrics
            model: Filter by model
            agent: Filter by agent

        Returns:
            Detailed metrics
        """
        # Parse time range
        time_delta_map = {
            "1h": timedelta(hours=1),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
        }
        delta = time_delta_map.get(time_range, timedelta(hours=24))

        start_time = datetime.utcnow() - delta
        end_time = datetime.utcnow()

        # Get metrics from monitor
        metrics = self.monitor.get_metrics(
            start_time=start_time,
            end_time=end_time,
            model=model,
            agent=agent,
        )

        # Get cost data
        cost_report = self.cost_tracker.get_report(
            start_time=start_time,
            end_time=end_time,
        )

        return {
            "time_range": time_range,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "filters": {
                "model": model,
                "agent": agent,
            },
            "performance": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "success_rate": metrics.success_rate,
                "avg_latency_ms": metrics.avg_latency_ms,
                "p50_latency_ms": metrics.p50_latency_ms,
                "p95_latency_ms": metrics.p95_latency_ms,
                "p99_latency_ms": metrics.p99_latency_ms,
                "cache_hit_rate": metrics.cache_hit_rate,
            },
            "costs": {
                "total_cost": cost_report.total_cost,
                "avg_cost_per_request": cost_report.avg_cost_per_request,
                "cost_by_model": cost_report.cost_by_model,
                "cost_by_agent": cost_report.cost_by_agent,
                "daily_breakdown": cost_report.daily_costs,
            },
            "tokens": {
                "total_tokens": metrics.total_tokens,
                "avg_tokens_per_request": metrics.avg_tokens_per_request,
            },
            "errors": {
                "total_errors": metrics.failed_requests,
                "error_breakdown": metrics.error_breakdown,
            },
            "model_breakdown": metrics.model_breakdown,
        }

    def get_cost_analysis(self) -> Dict[str, Any]:
        """
        Get detailed cost analysis

        Returns:
            Cost analysis with forecasts and recommendations
        """
        # Last 30 days
        cost_report = self.cost_tracker.get_report(
            start_time=datetime.utcnow() - timedelta(days=30),
        )

        # Forecast next 30 days
        forecast = self.cost_tracker.forecast_costs(days_ahead=30)

        # Top spenders
        top_users = self.cost_tracker.get_top_spenders(limit=10, dimension="user")
        top_models = self.cost_tracker.get_top_spenders(limit=10, dimension="model")
        top_agents = self.cost_tracker.get_top_spenders(limit=10, dimension="agent")

        # Budget status
        budget_status = cost_report.budget_status

        return {
            "summary": {
                "total_cost_30d": cost_report.total_cost,
                "total_requests": cost_report.total_requests,
                "avg_cost_per_request": cost_report.avg_cost_per_request,
            },
            "breakdown": {
                "by_model": cost_report.cost_by_model,
                "by_agent": cost_report.cost_by_agent,
                "by_day": cost_report.daily_costs,
            },
            "top_spenders": {
                "users": top_users,
                "models": top_models,
                "agents": top_agents,
            },
            "forecast": forecast,
            "budgets": budget_status,
            "recommendations": cost_report.recommendations,
        }

    def get_experiments_dashboard(self) -> Dict[str, Any]:
        """
        Get A/B testing experiments dashboard

        Returns:
            Experiments overview and results
        """
        # Get all experiments by status
        running = self.ab_tester.list_experiments(status="running")
        completed = self.ab_tester.list_experiments(status="completed")
        draft = self.ab_tester.list_experiments(status="draft")

        # Get summaries
        running_summaries = [
            self.ab_tester.get_experiment_summary(name)
            for name in running
        ]

        completed_summaries = [
            self.ab_tester.get_experiment_summary(name)
            for name in completed
        ]

        return {
            "counts": {
                "running": len(running),
                "completed": len(completed),
                "draft": len(draft),
            },
            "running_experiments": running_summaries,
            "completed_experiments": completed_summaries,
            "insights": self._generate_experiment_insights(completed_summaries),
        }

    def _generate_experiment_insights(
        self,
        completed_experiments: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate insights from completed experiments"""
        insights = []

        if not completed_experiments:
            return ["No completed experiments yet."]

        # Count wins by model
        model_wins = {}
        for exp in completed_experiments:
            if exp and exp.get("winner"):
                # Find winner variant
                for variant in exp.get("variants", []):
                    if variant["name"] == exp["winner"]:
                        model = variant.get("model", "unknown")
                        model_wins[model] = model_wins.get(model, 0) + 1

        if model_wins:
            best_model = max(model_wins.items(), key=lambda x: x[1])
            insights.append(
                f"{best_model[0]} won {best_model[1]} out of {len(completed_experiments)} experiments"
            )

        # Analyze success rates
        avg_success_rates = []
        for exp in completed_experiments:
            if exp and exp.get("variants"):
                rates = [v.get("success_rate", 0) for v in exp["variants"]]
                if rates:
                    avg_success_rates.append(sum(rates) / len(rates))

        if avg_success_rates:
            overall_avg = sum(avg_success_rates) / len(avg_success_rates)
            insights.append(f"Average success rate across all experiments: {overall_avg:.2%}")

        return insights

    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        Get active alerts

        Returns:
            List of alert dictionaries
        """
        alerts = []

        # Get current metrics
        metrics = self.monitor.get_metrics(
            start_time=datetime.utcnow() - timedelta(hours=1),
        )

        # Check error rate
        if metrics.success_rate < 0.95:  # <95% success
            alerts.append({
                "severity": "high",
                "type": "error_rate",
                "message": f"High error rate: {(1-metrics.success_rate)*100:.1f}%",
                "value": 1 - metrics.success_rate,
                "threshold": 0.05,
            })

        # Check latency
        if metrics.p95_latency_ms > 10000:  # >10s
            alerts.append({
                "severity": "medium",
                "type": "latency",
                "message": f"High P95 latency: {metrics.p95_latency_ms:.0f}ms",
                "value": metrics.p95_latency_ms,
                "threshold": 10000,
            })

        # Check budget alerts
        cost_report = self.cost_tracker.get_report()
        for budget_name, status in cost_report.budget_status.items():
            if status and status.get("alert_triggered"):
                alerts.append({
                    "severity": "high" if status["percentage"] > 100 else "medium",
                    "type": "budget",
                    "message": f"Budget alert: {budget_name} at {status['percentage']:.1f}%",
                    "value": status["percentage"],
                    "threshold": 80,
                })

        return alerts

    def get_health_check(self) -> Dict[str, Any]:
        """
        Get system health status

        Returns:
            Health check results
        """
        # Get last hour metrics
        metrics = self.monitor.get_metrics(
            start_time=datetime.utcnow() - timedelta(hours=1),
        )

        # Determine health status
        health_checks = {
            "error_rate": {
                "status": "healthy" if metrics.success_rate > 0.95 else "degraded",
                "value": 1 - metrics.success_rate,
                "threshold": 0.05,
            },
            "latency": {
                "status": "healthy" if metrics.avg_latency_ms < 5000 else "degraded",
                "value": metrics.avg_latency_ms,
                "threshold": 5000,
            },
            "cache_performance": {
                "status": "healthy" if metrics.cache_hit_rate > 0.3 else "degraded",
                "value": metrics.cache_hit_rate,
                "threshold": 0.3,
            },
        }

        # Overall status
        statuses = [check["status"] for check in health_checks.values()]
        if all(s == "healthy" for s in statuses):
            overall_status = "healthy"
        elif any(s == "critical" for s in statuses):
            overall_status = "critical"
        else:
            overall_status = "degraded"

        return {
            "overall_status": overall_status,
            "checks": health_checks,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def export_dashboard_data(self) -> Dict[str, Any]:
        """
        Export all dashboard data for external use

        Returns:
            Complete dashboard data
        """
        return {
            "overview": self.get_overview(),
            "detailed_metrics": self.get_detailed_metrics(time_range="24h"),
            "cost_analysis": self.get_cost_analysis(),
            "experiments": self.get_experiments_dashboard(),
            "alerts": self.get_alerts(),
            "health": self.get_health_check(),
            "exported_at": datetime.utcnow().isoformat(),
        }
