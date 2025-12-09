"""
PostHog Client Integration
===========================
Professional analytics integration for product metrics
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from posthog import Posthog
from functools import lru_cache
import asyncpg

logger = logging.getLogger(__name__)


class PostHogClient:
    """
    PostHog analytics client with local database backup

    Features:
    - Event tracking with automatic batching
    - User identification and traits
    - Local PostgreSQL backup for analytics
    - Offline mode fallback
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = "https://app.posthog.com",
        db_pool: Optional[asyncpg.Pool] = None,
        enable_local_backup: bool = True
    ):
        self.api_key = api_key or os.getenv('POSTHOG_API_KEY')
        self.host = host
        self.db_pool = db_pool
        self.enable_local_backup = enable_local_backup

        # Initialize PostHog if API key is provided
        if self.api_key:
            self.client = Posthog(
                project_api_key=self.api_key,
                host=host,
                debug=os.getenv('ENVIRONMENT') == 'development',
                on_error=self._handle_error
            )
            self.enabled = True
            logger.info("PostHog client initialized successfully")
        else:
            self.client = None
            self.enabled = False
            logger.warning("PostHog API key not found, analytics disabled")

    def _handle_error(self, error: Exception, batch: List[Dict]):
        """Error handler for PostHog client"""
        logger.error(f"PostHog error: {error}")
        logger.debug(f"Failed batch: {batch}")

    async def _backup_to_db(
        self,
        user_id: Optional[str],
        event_name: str,
        properties: Dict[str, Any],
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Backup event to local PostgreSQL database"""
        if not self.enable_local_backup or not self.db_pool:
            return

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO analytics_events (
                        user_id, event_name, event_properties,
                        session_id, ip_address, user_agent, timestamp
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ''',
                    user_id,
                    event_name,
                    properties,
                    session_id,
                    ip_address,
                    user_agent,
                    datetime.utcnow()
                )
        except Exception as e:
            logger.error(f"Failed to backup event to database: {e}")

    def capture(
        self,
        distinct_id: str,
        event: str,
        properties: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Capture an event

        Args:
            distinct_id: Unique identifier for the user
            event: Event name (e.g., 'project_created')
            properties: Event properties
            context: Additional context
            timestamp: Event timestamp (defaults to now)
            user_id: Database user ID for local backup
            session_id: Session identifier
            ip_address: User IP address
            user_agent: User agent string

        Returns:
            bool: True if event was captured successfully
        """
        properties = properties or {}

        # Add metadata
        properties['timestamp'] = (timestamp or datetime.utcnow()).isoformat()
        properties['environment'] = os.getenv('ENVIRONMENT', 'production')

        # Send to PostHog
        success = False
        if self.enabled and self.client:
            try:
                self.client.capture(
                    distinct_id=distinct_id,
                    event=event,
                    properties=properties,
                    context=context,
                    timestamp=timestamp
                )
                success = True
            except Exception as e:
                logger.error(f"Failed to send event to PostHog: {e}")

        # Backup to local database (async, don't wait)
        if self.enable_local_backup:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(
                    self._backup_to_db(
                        user_id, event, properties,
                        session_id, ip_address, user_agent
                    )
                )
            except RuntimeError:
                # No event loop, skip backup
                pass

        return success

    def identify(
        self,
        distinct_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Identify a user with their traits

        Args:
            distinct_id: Unique identifier for the user
            properties: User properties/traits

        Returns:
            bool: True if successful
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.identify(
                distinct_id=distinct_id,
                properties=properties or {}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to identify user: {e}")
            return False

    def group(
        self,
        group_type: str,
        group_key: str,
        distinct_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Associate a user with a group

        Args:
            group_type: Type of group (e.g., 'company', 'team')
            group_key: Group identifier
            distinct_id: User identifier
            properties: Group properties

        Returns:
            bool: True if successful
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.group_identify(
                group_type=group_type,
                group_key=group_key,
                properties=properties or {}
            )

            self.client.capture(
                distinct_id=distinct_id,
                event='$group',
                properties={
                    '$group_type': group_type,
                    '$group_key': group_key,
                    '$group_set': properties or {}
                }
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set group: {e}")
            return False

    def alias(self, previous_id: str, distinct_id: str) -> bool:
        """
        Alias two user identifiers

        Args:
            previous_id: Old identifier
            distinct_id: New identifier

        Returns:
            bool: True if successful
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.alias(
                previous_id=previous_id,
                distinct_id=distinct_id
            )
            return True
        except Exception as e:
            logger.error(f"Failed to alias user: {e}")
            return False

    def feature_enabled(
        self,
        key: str,
        distinct_id: str,
        default: bool = False
    ) -> bool:
        """
        Check if a feature flag is enabled for a user

        Args:
            key: Feature flag key
            distinct_id: User identifier
            default: Default value if check fails

        Returns:
            bool: True if feature is enabled
        """
        if not self.enabled or not self.client:
            return default

        try:
            return self.client.feature_enabled(
                key=key,
                distinct_id=distinct_id
            ) or default
        except Exception as e:
            logger.error(f"Failed to check feature flag: {e}")
            return default

    def get_feature_flag(
        self,
        key: str,
        distinct_id: str,
        default: Any = None
    ) -> Any:
        """
        Get feature flag value with variants

        Args:
            key: Feature flag key
            distinct_id: User identifier
            default: Default value

        Returns:
            Feature flag value (can be bool, string, number, etc.)
        """
        if not self.enabled or not self.client:
            return default

        try:
            return self.client.get_feature_flag(
                key=key,
                distinct_id=distinct_id
            ) or default
        except Exception as e:
            logger.error(f"Failed to get feature flag: {e}")
            return default

    def shutdown(self):
        """Flush and shutdown PostHog client"""
        if self.client:
            try:
                self.client.flush()
                self.client.shutdown()
                logger.info("PostHog client shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down PostHog: {e}")


# Singleton instance
_posthog_client: Optional[PostHogClient] = None


@lru_cache(maxsize=1)
def get_posthog_client(db_pool: Optional[asyncpg.Pool] = None) -> PostHogClient:
    """
    Get or create PostHog client singleton

    Args:
        db_pool: PostgreSQL connection pool for local backup

    Returns:
        PostHogClient instance
    """
    global _posthog_client

    if _posthog_client is None:
        _posthog_client = PostHogClient(db_pool=db_pool)

    return _posthog_client
