"""
A/B Testing for Prompts and Models

Features:
- Run experiments comparing different prompts or models
- Track performance metrics for each variant
- Statistical significance testing
- Automatic winner selection
"""

import logging
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Experiment status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Variant:
    """Experiment variant"""
    name: str
    prompt_template: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    weight: float = 1.0  # Traffic allocation weight
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VariantResult:
    """Results for a variant"""
    variant_name: str
    impressions: int = 0
    successes: int = 0
    failures: int = 0
    total_latency_ms: float = 0.0
    total_cost: float = 0.0
    total_tokens: int = 0

    success_rate: float = 0.0
    avg_latency_ms: float = 0.0
    avg_cost: float = 0.0
    avg_tokens: float = 0.0

    def calculate_metrics(self):
        """Calculate derived metrics"""
        if self.impressions > 0:
            self.success_rate = self.successes / self.impressions
            self.avg_latency_ms = self.total_latency_ms / self.impressions
            self.avg_cost = self.total_cost / self.impressions
            self.avg_tokens = self.total_tokens / self.impressions


@dataclass
class Experiment:
    """A/B test experiment"""
    name: str
    description: str
    variants: List[Variant]
    status: ExperimentStatus = ExperimentStatus.DRAFT
    primary_metric: str = "success_rate"  # success_rate, latency, cost
    min_sample_size: int = 100
    confidence_level: float = 0.95
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    winner: Optional[str] = None


class ABTester:
    """A/B testing system for prompts and models"""

    def __init__(self):
        self._experiments: Dict[str, Experiment] = {}
        self._results: Dict[str, Dict[str, VariantResult]] = {}

    def create_experiment(self, experiment: Experiment) -> str:
        """Create a new experiment"""
        if experiment.name in self._experiments:
            raise ValueError(f"Experiment {experiment.name} already exists")

        if len(experiment.variants) < 2:
            raise ValueError("Experiment must have at least 2 variants")

        self._experiments[experiment.name] = experiment
        self._results[experiment.name] = {
            v.name: VariantResult(variant_name=v.name)
            for v in experiment.variants
        }

        logger.info(f"[ABTester] Created experiment: {experiment.name} with {len(experiment.variants)} variants")
        return experiment.name

    def start_experiment(self, experiment_name: str):
        """Start an experiment"""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            raise ValueError(f"Experiment {experiment_name} not found")

        if experiment.status == ExperimentStatus.RUNNING:
            logger.warning(f"[ABTester] Experiment {experiment_name} is already running")
            return

        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.utcnow()
        logger.info(f"[ABTester] Started experiment: {experiment_name}")

    def pause_experiment(self, experiment_name: str):
        """Pause an experiment"""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            raise ValueError(f"Experiment {experiment_name} not found")

        experiment.status = ExperimentStatus.PAUSED
        logger.info(f"[ABTester] Paused experiment: {experiment_name}")

    def complete_experiment(self, experiment_name: str, winner: Optional[str] = None):
        """Complete an experiment"""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            raise ValueError(f"Experiment {experiment_name} not found")

        experiment.status = ExperimentStatus.COMPLETED
        experiment.completed_at = datetime.utcnow()

        if winner:
            experiment.winner = winner
        else:
            # Auto-select winner
            winner = self._select_winner(experiment_name)
            experiment.winner = winner

        logger.info(f"[ABTester] Completed experiment: {experiment_name}, winner: {experiment.winner}")

    def get_variant(self, experiment_name: str) -> Optional[Variant]:
        """Get a variant for the experiment (using weighted random selection)"""
        experiment = self._experiments.get(experiment_name)
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return None

        # Weighted random selection
        total_weight = sum(v.weight for v in experiment.variants)
        rand = random.uniform(0, total_weight)

        cumulative_weight = 0
        for variant in experiment.variants:
            cumulative_weight += variant.weight
            if rand <= cumulative_weight:
                return variant

        # Fallback to first variant
        return experiment.variants[0]

    def track_result(
        self,
        experiment_name: str,
        variant_name: str,
        success: bool,
        latency_ms: float,
        cost: float = 0.0,
        tokens: int = 0,
    ):
        """Track a result for a variant"""
        if experiment_name not in self._results:
            logger.warning(f"[ABTester] Experiment {experiment_name} not found")
            return

        results = self._results[experiment_name]
        if variant_name not in results:
            logger.warning(f"[ABTester] Variant {variant_name} not found in {experiment_name}")
            return

        result = results[variant_name]
        result.impressions += 1

        if success:
            result.successes += 1
        else:
            result.failures += 1

        result.total_latency_ms += latency_ms
        result.total_cost += cost
        result.total_tokens += tokens

        # Recalculate metrics
        result.calculate_metrics()

        # Check if experiment should auto-complete
        experiment = self._experiments[experiment_name]
        if experiment.status == ExperimentStatus.RUNNING:
            self._check_auto_complete(experiment_name)

    def get_results(self, experiment_name: str) -> Optional[Dict[str, VariantResult]]:
        """Get results for an experiment"""
        return self._results.get(experiment_name)

    def get_experiment_summary(self, experiment_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive summary of an experiment"""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            return None

        results = self._results.get(experiment_name, {})

        # Calculate total impressions
        total_impressions = sum(r.impressions for r in results.values())

        # Build variant summaries
        variant_summaries = []
        for variant in experiment.variants:
            result = results.get(variant.name)
            if result:
                variant_summaries.append({
                    "name": variant.name,
                    "impressions": result.impressions,
                    "traffic_share": result.impressions / total_impressions if total_impressions > 0 else 0,
                    "success_rate": result.success_rate,
                    "avg_latency_ms": result.avg_latency_ms,
                    "avg_cost": result.avg_cost,
                    "avg_tokens": result.avg_tokens,
                    "model": variant.model,
                    "temperature": variant.temperature,
                })

        # Determine current leader
        leader = None
        if results:
            if experiment.primary_metric == "success_rate":
                leader = max(results.items(), key=lambda x: x[1].success_rate)[0]
            elif experiment.primary_metric == "latency":
                leader = min(results.items(), key=lambda x: x[1].avg_latency_ms)[0]
            elif experiment.primary_metric == "cost":
                leader = min(results.items(), key=lambda x: x[1].avg_cost)[0]

        # Check if statistically significant
        is_significant = self._is_statistically_significant(experiment_name)

        return {
            "name": experiment.name,
            "description": experiment.description,
            "status": experiment.status,
            "primary_metric": experiment.primary_metric,
            "total_impressions": total_impressions,
            "variants": variant_summaries,
            "current_leader": leader,
            "winner": experiment.winner,
            "is_statistically_significant": is_significant,
            "min_sample_size_reached": total_impressions >= experiment.min_sample_size,
            "created_at": experiment.created_at.isoformat(),
            "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
            "completed_at": experiment.completed_at.isoformat() if experiment.completed_at else None,
        }

    def _select_winner(self, experiment_name: str) -> Optional[str]:
        """Select winner based on primary metric"""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            return None

        results = self._results.get(experiment_name, {})
        if not results:
            return None

        # Filter variants with sufficient data
        valid_results = {
            name: result
            for name, result in results.items()
            if result.impressions >= experiment.min_sample_size
        }

        if not valid_results:
            logger.warning(f"[ABTester] No variant reached min sample size for {experiment_name}")
            return None

        # Select based on primary metric
        if experiment.primary_metric == "success_rate":
            winner = max(valid_results.items(), key=lambda x: x[1].success_rate)[0]
        elif experiment.primary_metric == "latency":
            winner = min(valid_results.items(), key=lambda x: x[1].avg_latency_ms)[0]
        elif experiment.primary_metric == "cost":
            winner = min(valid_results.items(), key=lambda x: x[1].avg_cost)[0]
        else:
            winner = max(valid_results.items(), key=lambda x: x[1].success_rate)[0]

        return winner

    def _is_statistically_significant(self, experiment_name: str) -> bool:
        """Check if results are statistically significant (simplified)"""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            return False

        results = self._results.get(experiment_name, {})

        # Need at least 2 variants with sufficient data
        valid_results = [
            r for r in results.values()
            if r.impressions >= experiment.min_sample_size
        ]

        if len(valid_results) < 2:
            return False

        # Simplified check: significant difference in success rates
        success_rates = [r.success_rate for r in valid_results]
        if len(success_rates) < 2:
            return False

        # Calculate standard deviation
        try:
            std_dev = statistics.stdev(success_rates)
            mean = statistics.mean(success_rates)

            # If variation is > 5% of mean, consider significant
            return (std_dev / mean) > 0.05 if mean > 0 else False

        except statistics.StatisticsError:
            return False

    def _check_auto_complete(self, experiment_name: str):
        """Check if experiment should auto-complete"""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            return

        results = self._results.get(experiment_name, {})
        total_impressions = sum(r.impressions for r in results.values())

        # Auto-complete if:
        # 1. Min sample size reached for all variants
        # 2. Results are statistically significant
        if (total_impressions >= experiment.min_sample_size * len(experiment.variants) and
            self._is_statistically_significant(experiment_name)):

            logger.info(f"[ABTester] Auto-completing experiment {experiment_name} (statistically significant)")
            self.complete_experiment(experiment_name)

    def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[str]:
        """List experiment names, optionally filtered by status"""
        if status:
            return [
                name for name, exp in self._experiments.items()
                if exp.status == status
            ]
        return list(self._experiments.keys())

    def delete_experiment(self, experiment_name: str):
        """Delete an experiment"""
        if experiment_name in self._experiments:
            del self._experiments[experiment_name]

        if experiment_name in self._results:
            del self._results[experiment_name]

        logger.info(f"[ABTester] Deleted experiment: {experiment_name}")

    def export_results(self, experiment_name: str) -> Optional[Dict[str, Any]]:
        """Export full experiment data for analysis"""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            return None

        results = self._results.get(experiment_name, {})

        return {
            "experiment": {
                "name": experiment.name,
                "description": experiment.description,
                "status": experiment.status,
                "primary_metric": experiment.primary_metric,
                "min_sample_size": experiment.min_sample_size,
                "confidence_level": experiment.confidence_level,
                "created_at": experiment.created_at.isoformat(),
                "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
                "completed_at": experiment.completed_at.isoformat() if experiment.completed_at else None,
                "winner": experiment.winner,
            },
            "variants": [
                {
                    "name": v.name,
                    "prompt_template": v.prompt_template,
                    "model": v.model,
                    "temperature": v.temperature,
                    "weight": v.weight,
                    "metadata": v.metadata,
                }
                for v in experiment.variants
            ],
            "results": {
                name: {
                    "impressions": r.impressions,
                    "successes": r.successes,
                    "failures": r.failures,
                    "success_rate": r.success_rate,
                    "avg_latency_ms": r.avg_latency_ms,
                    "avg_cost": r.avg_cost,
                    "avg_tokens": r.avg_tokens,
                }
                for name, r in results.items()
            },
        }
