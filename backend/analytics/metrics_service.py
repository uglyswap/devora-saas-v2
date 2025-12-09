"""
Metrics Service
===============
Business metrics calculation and reporting service
"""

import asyncpg
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class MetricPeriod(str, Enum):
    """Time period for metrics calculation"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"


@dataclass
class UserMetrics:
    """User-related metrics"""
    total_users: int
    active_users_today: int
    active_users_week: int
    active_users_month: int
    new_users_today: int
    new_users_week: int
    new_users_month: int
    churned_users_month: int
    retention_rate_30d: float


@dataclass
class RevenueMetrics:
    """Revenue-related metrics"""
    total_revenue: Decimal
    revenue_today: Decimal
    revenue_week: Decimal
    revenue_month: Decimal
    revenue_last_month: Decimal
    mrr: Decimal  # Monthly Recurring Revenue
    arr: Decimal  # Annual Recurring Revenue
    average_revenue_per_user: Decimal
    lifetime_value: Decimal


@dataclass
class EngagementMetrics:
    """User engagement metrics"""
    total_projects: int
    projects_created_today: int
    projects_created_week: int
    projects_created_month: int
    total_conversations: int
    total_messages: int
    average_messages_per_conversation: float
    average_projects_per_user: float
    average_session_duration_minutes: float


@dataclass
class PerformanceMetrics:
    """System performance metrics"""
    average_query_time_ms: float
    slow_queries_count: int
    error_rate: float
    api_response_time_p95: float
    successful_deployments: int
    failed_deployments: int
    deployment_success_rate: float


@dataclass
class DashboardMetrics:
    """Complete dashboard metrics"""
    user_metrics: UserMetrics
    revenue_metrics: RevenueMetrics
    engagement_metrics: EngagementMetrics
    performance_metrics: PerformanceMetrics
    generated_at: datetime


class MetricsService:
    """
    Service for calculating business and product metrics

    Features:
    - Real-time metric calculation
    - Caching for expensive queries
    - Historical trend analysis
    - Cohort analysis support
    """

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_user_metrics(
        self,
        as_of_date: Optional[date] = None
    ) -> UserMetrics:
        """
        Calculate user-related metrics

        Args:
            as_of_date: Calculate metrics as of this date (defaults to today)

        Returns:
            UserMetrics with all user statistics
        """
        as_of_date = as_of_date or date.today()

        async with self.db_pool.acquire() as conn:
            # Total users
            total_users = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE deleted_at IS NULL"
            )

            # Active users (users who logged in or created events)
            active_today = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id)
                FROM analytics_events
                WHERE DATE(timestamp) = $1
            """, as_of_date)

            active_week = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id)
                FROM analytics_events
                WHERE timestamp >= $1
            """, datetime.combine(as_of_date - timedelta(days=7), datetime.min.time()))

            active_month = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id)
                FROM analytics_events
                WHERE timestamp >= $1
            """, datetime.combine(as_of_date - timedelta(days=30), datetime.min.time()))

            # New users
            new_today = await conn.fetchval("""
                SELECT COUNT(*) FROM users
                WHERE DATE(created_at) = $1
            """, as_of_date)

            new_week = await conn.fetchval("""
                SELECT COUNT(*) FROM users
                WHERE created_at >= $1
            """, datetime.combine(as_of_date - timedelta(days=7), datetime.min.time()))

            new_month = await conn.fetchval("""
                SELECT COUNT(*) FROM users
                WHERE created_at >= $1
            """, datetime.combine(as_of_date - timedelta(days=30), datetime.min.time()))

            # Churned users (canceled subscriptions this month)
            churned_month = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id)
                FROM analytics_events
                WHERE event_name = 'subscription_canceled'
                AND timestamp >= $1
            """, datetime.combine(as_of_date - timedelta(days=30), datetime.min.time()))

            # Retention rate (users who returned in last 30 days / users 30 days ago)
            users_30d_ago = await conn.fetchval("""
                SELECT COUNT(*) FROM users
                WHERE created_at <= $1
            """, datetime.combine(as_of_date - timedelta(days=30), datetime.min.time()))

            retention_rate = (active_month / users_30d_ago * 100) if users_30d_ago > 0 else 0.0

            return UserMetrics(
                total_users=total_users or 0,
                active_users_today=active_today or 0,
                active_users_week=active_week or 0,
                active_users_month=active_month or 0,
                new_users_today=new_today or 0,
                new_users_week=new_week or 0,
                new_users_month=new_month or 0,
                churned_users_month=churned_month or 0,
                retention_rate_30d=round(retention_rate, 2)
            )

    async def get_revenue_metrics(
        self,
        as_of_date: Optional[date] = None
    ) -> RevenueMetrics:
        """
        Calculate revenue-related metrics

        Args:
            as_of_date: Calculate metrics as of this date

        Returns:
            RevenueMetrics with all revenue statistics
        """
        as_of_date = as_of_date or date.today()

        async with self.db_pool.acquire() as conn:
            # Total revenue
            total_revenue = await conn.fetchval("""
                SELECT COALESCE(SUM(amount), 0)
                FROM invoices
                WHERE status = 'paid'
            """) or Decimal('0')

            # Revenue today
            revenue_today = await conn.fetchval("""
                SELECT COALESCE(SUM(amount), 0)
                FROM invoices
                WHERE status = 'paid'
                AND DATE(created_at) = $1
            """, as_of_date) or Decimal('0')

            # Revenue this week
            revenue_week = await conn.fetchval("""
                SELECT COALESCE(SUM(amount), 0)
                FROM invoices
                WHERE status = 'paid'
                AND created_at >= $1
            """, datetime.combine(as_of_date - timedelta(days=7), datetime.min.time())) or Decimal('0')

            # Revenue this month
            first_of_month = date(as_of_date.year, as_of_date.month, 1)
            revenue_month = await conn.fetchval("""
                SELECT COALESCE(SUM(amount), 0)
                FROM invoices
                WHERE status = 'paid'
                AND created_at >= $1
            """, datetime.combine(first_of_month, datetime.min.time())) or Decimal('0')

            # Revenue last month
            first_of_last_month = (first_of_month - timedelta(days=1)).replace(day=1)
            revenue_last_month = await conn.fetchval("""
                SELECT COALESCE(SUM(amount), 0)
                FROM invoices
                WHERE status = 'paid'
                AND created_at >= $1
                AND created_at < $2
            """,
                datetime.combine(first_of_last_month, datetime.min.time()),
                datetime.combine(first_of_month, datetime.min.time())
            ) or Decimal('0')

            # MRR (Monthly Recurring Revenue)
            # Active subscriptions * subscription price
            active_subs = await conn.fetchval("""
                SELECT COUNT(*)
                FROM users
                WHERE subscription_status = 'active'
            """) or 0

            sub_price = await conn.fetchval("""
                SELECT subscription_price
                FROM system_config
                WHERE id = 'system_config'
            """) or Decimal('9.90')

            mrr = Decimal(active_subs) * sub_price

            # ARR (Annual Recurring Revenue)
            arr = mrr * 12

            # ARPU (Average Revenue Per User)
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users") or 1
            arpu = total_revenue / Decimal(total_users)

            # LTV (Lifetime Value) - simplified calculation
            # LTV = ARPU * average customer lifetime (assume 12 months)
            ltv = arpu * 12

            return RevenueMetrics(
                total_revenue=total_revenue,
                revenue_today=revenue_today,
                revenue_week=revenue_week,
                revenue_month=revenue_month,
                revenue_last_month=revenue_last_month,
                mrr=mrr,
                arr=arr,
                average_revenue_per_user=round(arpu, 2),
                lifetime_value=round(ltv, 2)
            )

    async def get_engagement_metrics(self) -> EngagementMetrics:
        """Calculate user engagement metrics"""
        async with self.db_pool.acquire() as conn:
            # Projects
            total_projects = await conn.fetchval("""
                SELECT COUNT(*) FROM projects WHERE deleted_at IS NULL
            """) or 0

            projects_today = await conn.fetchval("""
                SELECT COUNT(*) FROM projects
                WHERE DATE(created_at) = CURRENT_DATE
            """) or 0

            projects_week = await conn.fetchval("""
                SELECT COUNT(*) FROM projects
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """) or 0

            projects_month = await conn.fetchval("""
                SELECT COUNT(*) FROM projects
                WHERE created_at >= NOW() - INTERVAL '30 days'
            """) or 0

            # Conversations and messages
            total_conversations = await conn.fetchval("""
                SELECT COUNT(*) FROM conversations WHERE deleted_at IS NULL
            """) or 0

            total_messages = await conn.fetchval("""
                SELECT COUNT(*) FROM messages
            """) or 0

            avg_messages = await conn.fetchval("""
                SELECT COALESCE(AVG(message_count), 0)
                FROM (
                    SELECT conversation_id, COUNT(*) as message_count
                    FROM messages
                    GROUP BY conversation_id
                ) sub
            """) or 0.0

            # Average projects per user
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users") or 1
            avg_projects = total_projects / total_users

            # Average session duration (from analytics events)
            avg_session = await conn.fetchval("""
                SELECT COALESCE(AVG(duration_minutes), 0)
                FROM (
                    SELECT
                        session_id,
                        EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) / 60 as duration_minutes
                    FROM analytics_events
                    WHERE session_id IS NOT NULL
                    AND timestamp >= NOW() - INTERVAL '7 days'
                    GROUP BY session_id
                    HAVING COUNT(*) > 1
                ) sub
            """) or 0.0

            return EngagementMetrics(
                total_projects=total_projects,
                projects_created_today=projects_today,
                projects_created_week=projects_week,
                projects_created_month=projects_month,
                total_conversations=total_conversations,
                total_messages=total_messages,
                average_messages_per_conversation=round(float(avg_messages), 2),
                average_projects_per_user=round(avg_projects, 2),
                average_session_duration_minutes=round(float(avg_session), 2)
            )

    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Calculate system performance metrics"""
        async with self.db_pool.acquire() as conn:
            # Query performance (from pg_stat_statements)
            avg_query_time = await conn.fetchval("""
                SELECT COALESCE(AVG(mean_exec_time), 0)
                FROM pg_stat_statements
                WHERE calls > 10
            """) or 0.0

            slow_queries = await conn.fetchval("""
                SELECT COUNT(*)
                FROM pg_stat_statements
                WHERE mean_exec_time > 100
            """) or 0

            # Error rate (from analytics events)
            total_events = await conn.fetchval("""
                SELECT COUNT(*)
                FROM analytics_events
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
            """) or 1

            error_events = await conn.fetchval("""
                SELECT COUNT(*)
                FROM analytics_events
                WHERE event_name IN ('error_occurred', 'api_error')
                AND timestamp >= NOW() - INTERVAL '24 hours'
            """) or 0

            error_rate = (error_events / total_events * 100)

            # Deployment metrics (from analytics events)
            deploy_success = await conn.fetchval("""
                SELECT COUNT(*)
                FROM analytics_events
                WHERE event_name IN ('vercel_deploy_succeeded', 'github_push_succeeded')
                AND timestamp >= NOW() - INTERVAL '30 days'
            """) or 0

            deploy_failed = await conn.fetchval("""
                SELECT COUNT(*)
                FROM analytics_events
                WHERE event_name IN ('vercel_deploy_failed', 'github_push_failed')
                AND timestamp >= NOW() - INTERVAL '30 days'
            """) or 0

            total_deploys = deploy_success + deploy_failed
            deploy_success_rate = (deploy_success / total_deploys * 100) if total_deploys > 0 else 100.0

            # API response time (simplified - from search queries)
            api_p95 = await conn.fetchval("""
                SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms)
                FROM search_queries
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
            """) or 0.0

            return PerformanceMetrics(
                average_query_time_ms=round(float(avg_query_time), 2),
                slow_queries_count=slow_queries,
                error_rate=round(error_rate, 2),
                api_response_time_p95=round(float(api_p95), 2),
                successful_deployments=deploy_success,
                failed_deployments=deploy_failed,
                deployment_success_rate=round(deploy_success_rate, 2)
            )

    async def get_dashboard_metrics(
        self,
        as_of_date: Optional[date] = None
    ) -> DashboardMetrics:
        """
        Get all metrics for admin dashboard

        Args:
            as_of_date: Calculate metrics as of this date

        Returns:
            DashboardMetrics with all statistics
        """
        user_metrics = await self.get_user_metrics(as_of_date)
        revenue_metrics = await self.get_revenue_metrics(as_of_date)
        engagement_metrics = await self.get_engagement_metrics()
        performance_metrics = await self.get_performance_metrics()

        return DashboardMetrics(
            user_metrics=user_metrics,
            revenue_metrics=revenue_metrics,
            engagement_metrics=engagement_metrics,
            performance_metrics=performance_metrics,
            generated_at=datetime.utcnow()
        )

    async def get_cohort_retention(
        self,
        cohort_date: date,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate retention for a specific user cohort

        Args:
            cohort_date: Date when users signed up
            period_days: Number of days to track retention

        Returns:
            Retention data for the cohort
        """
        async with self.db_pool.acquire() as conn:
            # Users in cohort
            cohort_users = await conn.fetch("""
                SELECT id, email
                FROM users
                WHERE DATE(created_at) = $1
            """, cohort_date)

            cohort_size = len(cohort_users)
            if cohort_size == 0:
                return {"cohort_date": cohort_date, "cohort_size": 0, "retention": []}

            user_ids = [user['id'] for user in cohort_users]

            # Calculate retention for each day
            retention_data = []
            for day in range(1, period_days + 1):
                check_date = cohort_date + timedelta(days=day)

                active_count = await conn.fetchval("""
                    SELECT COUNT(DISTINCT user_id)
                    FROM analytics_events
                    WHERE user_id = ANY($1)
                    AND DATE(timestamp) = $2
                """, user_ids, check_date)

                retention_rate = (active_count / cohort_size * 100) if cohort_size > 0 else 0

                retention_data.append({
                    "day": day,
                    "date": check_date.isoformat(),
                    "active_users": active_count,
                    "retention_rate": round(retention_rate, 2)
                })

            return {
                "cohort_date": cohort_date.isoformat(),
                "cohort_size": cohort_size,
                "retention": retention_data
            }


# Singleton instance
_metrics_service: Optional[MetricsService] = None


def get_metrics_service(db_pool: asyncpg.Pool) -> MetricsService:
    """
    Get or create MetricsService singleton

    Args:
        db_pool: PostgreSQL connection pool

    Returns:
        MetricsService instance
    """
    global _metrics_service

    if _metrics_service is None:
        _metrics_service = MetricsService(db_pool)

    return _metrics_service
