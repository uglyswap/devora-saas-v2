"""
Enhanced Stripe Service with retry logic and robust webhook handling
Improvements over v1:
- Exponential backoff retry mechanism
- Idempotency key support
- Webhook event deduplication
- Comprehensive error handling
- Async batch operations
"""
import stripe
from typing import Optional, Dict, Any, List
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from config_service import ConfigService
from fastapi import HTTPException, status
import asyncio
from datetime import datetime, timezone, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)


class StripeNotConfiguredError(Exception):
    """Exception raised when Stripe is not configured"""
    pass


class StripeServiceV2:
    """Enhanced Stripe service with advanced features"""

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 1.0  # seconds
    RETRY_MULTIPLIER = 2.0

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.config_service = ConfigService(db)
        self._stripe_configured = False
        self._webhook_secret: Optional[str] = None

    async def _ensure_stripe_configured(self):
        """
        Configure Stripe with keys from database

        Raises:
            StripeNotConfiguredError: If Stripe is not configured
        """
        if not self._stripe_configured:
            api_key, webhook_secret, test_mode = await self.config_service.get_stripe_keys()
            if api_key:
                stripe.api_key = api_key
                self._webhook_secret = webhook_secret
                self._stripe_configured = True
                logger.info(f"Stripe configured in {'test' if test_mode else 'live'} mode")
            else:
                logger.error("Stripe API key not configured")
                raise StripeNotConfiguredError(
                    "Payment system not configured. Contact administrator."
                )

    async def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute Stripe API call with exponential backoff retry

        Args:
            func: Stripe API function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            API call result

        Raises:
            stripe.error.StripeError: If all retries fail
        """
        last_exception = None

        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except stripe.error.RateLimitError as e:
                last_exception = e
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY_BASE * (self.RETRY_MULTIPLIER ** attempt)
                    logger.warning(f"Rate limited. Retrying in {delay}s (attempt {attempt + 1}/{self.MAX_RETRIES})")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Max retries reached for rate limit")
            except stripe.error.APIConnectionError as e:
                last_exception = e
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY_BASE * (self.RETRY_MULTIPLIER ** attempt)
                    logger.warning(f"Connection error. Retrying in {delay}s (attempt {attempt + 1}/{self.MAX_RETRIES})")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Max retries reached for connection error")
            except stripe.error.StripeError as e:
                # Don't retry other Stripe errors
                raise e

        # All retries failed
        if last_exception:
            raise last_exception

    def _generate_idempotency_key(self, operation: str, **params) -> str:
        """
        Generate idempotency key for Stripe operations

        Args:
            operation: Operation name (e.g., 'create_customer')
            **params: Operation parameters

        Returns:
            Deterministic idempotency key
        """
        # Sort params for deterministic ordering
        sorted_params = sorted(params.items())
        key_data = json.dumps({"op": operation, "params": sorted_params}, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()[:24]  # Stripe limit: 24 chars

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create Stripe customer with idempotency

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Stripe customer ID

        Raises:
            stripe.error.StripeError: If creation fails
        """
        await self._ensure_stripe_configured()

        idempotency_key = self._generate_idempotency_key(
            "create_customer",
            email=email,
            name=name or ""
        )

        try:
            customer = await self._retry_with_backoff(
                stripe.Customer.create,
                email=email,
                name=name,
                metadata=metadata or {"source": "devora"},
                idempotency_key=idempotency_key
            )
            logger.info(f"Created Stripe customer: {customer.id} ({email})")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Error creating customer: {e}")
            raise

    async def create_checkout_session(
        self,
        customer_id: str,
        success_url: str,
        cancel_url: str,
        user_id: str,
        trial_days: int = 7,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Create Stripe checkout session with retry logic

        Args:
            customer_id: Stripe customer ID
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            user_id: Internal user ID
            trial_days: Free trial period
            metadata: Additional metadata

        Returns:
            Session ID and checkout URL

        Raises:
            stripe.error.StripeError: If session creation fails
        """
        await self._ensure_stripe_configured()
        billing_settings = await self.config_service.get_billing_settings()

        # Create price dynamically
        price = await self._retry_with_backoff(
            stripe.Price.create,
            unit_amount=int(billing_settings["price"] * 100),
            currency="eur",
            recurring={"interval": "month"},
            product_data={
                "name": "Devora Pro",
                "description": "Full access to Devora platform"
            }
        )

        # Generate idempotency key
        idempotency_key = self._generate_idempotency_key(
            "create_checkout",
            customer_id=customer_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc).strftime("%Y%m%d%H")  # Per-hour idempotency
        )

        try:
            session = await self._retry_with_backoff(
                stripe.checkout.Session.create,
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price.id, "quantity": 1}],
                mode="subscription",
                subscription_data={
                    "trial_period_days": trial_days,
                    "metadata": metadata or {}
                },
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                metadata={"user_id": user_id, **(metadata or {})},
                allow_promotion_codes=True,
                idempotency_key=idempotency_key
            )

            logger.info(f"Created checkout session: {session.id} for user {user_id}")

            return {
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {e}")
            raise

    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> str:
        """
        Create customer portal session

        Args:
            customer_id: Stripe customer ID
            return_url: Return URL after portal session

        Returns:
            Portal session URL

        Raises:
            stripe.error.StripeError: If creation fails
        """
        await self._ensure_stripe_configured()

        try:
            session = await self._retry_with_backoff(
                stripe.billing_portal.Session.create,
                customer=customer_id,
                return_url=return_url
            )
            logger.info(f"Created portal session for customer: {customer_id}")
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Error creating portal session: {e}")
            raise

    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True
    ) -> bool:
        """
        Cancel subscription (immediate or at period end)

        Args:
            subscription_id: Subscription ID to cancel
            cancel_at_period_end: If True, cancel at end of period (default)

        Returns:
            True if successful

        Raises:
            stripe.error.StripeError: If cancellation fails
        """
        await self._ensure_stripe_configured()

        try:
            if cancel_at_period_end:
                subscription = await self._retry_with_backoff(
                    stripe.Subscription.modify,
                    subscription_id,
                    cancel_at_period_end=True
                )
                logger.info(f"Subscription {subscription_id} will cancel at period end")
            else:
                subscription = await self._retry_with_backoff(
                    stripe.Subscription.delete,
                    subscription_id
                )
                logger.info(f"Subscription {subscription_id} canceled immediately")

            return True
        except stripe.error.StripeError as e:
            logger.error(f"Error canceling subscription: {e}")
            return False

    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription details

        Args:
            subscription_id: Subscription ID

        Returns:
            Subscription data or None if not found

        Raises:
            stripe.error.StripeError: If retrieval fails
        """
        await self._ensure_stripe_configured()

        try:
            subscription = await self._retry_with_backoff(
                stripe.Subscription.retrieve,
                subscription_id
            )

            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": subscription.canceled_at,
                "trial_end": subscription.trial_end
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription: {e}")
            return None

    async def list_invoices(
        self,
        customer_id: str,
        limit: int = 10,
        starting_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List customer invoices with pagination

        Args:
            customer_id: Customer ID
            limit: Number of invoices to retrieve
            starting_after: Pagination cursor

        Returns:
            List of invoice dictionaries

        Raises:
            stripe.error.StripeError: If list fails
        """
        await self._ensure_stripe_configured()

        try:
            params = {"customer": customer_id, "limit": limit}
            if starting_after:
                params["starting_after"] = starting_after

            invoices = await self._retry_with_backoff(
                stripe.Invoice.list,
                **params
            )

            return [
                {
                    "id": inv.id,
                    "amount": inv.amount_paid / 100,
                    "currency": inv.currency,
                    "status": inv.status,
                    "invoice_pdf": inv.invoice_pdf,
                    "created": inv.created,
                    "period_start": inv.period_start,
                    "period_end": inv.period_end
                }
                for inv in invoices.data
            ]
        except stripe.error.StripeError as e:
            logger.error(f"Error listing invoices: {e}")
            return []

    async def verify_webhook_signature(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature

        Args:
            payload: Raw webhook payload
            sig_header: Stripe signature header

        Returns:
            Verified webhook event

        Raises:
            ValueError: If signature verification fails
        """
        if not self._webhook_secret:
            await self._ensure_stripe_configured()

        if not self._webhook_secret:
            raise ValueError("Webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self._webhook_secret
            )
            return event
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")

    async def is_webhook_duplicate(self, event_id: str) -> bool:
        """
        Check if webhook event has already been processed

        Args:
            event_id: Stripe event ID

        Returns:
            True if event is duplicate, False otherwise
        """
        # Check if event exists in processed_webhooks collection
        existing = await self.db.processed_webhooks.find_one({"event_id": event_id})

        if existing:
            logger.warning(f"Duplicate webhook event: {event_id}")
            return True

        # Store event ID to prevent duplicates
        await self.db.processed_webhooks.insert_one({
            "event_id": event_id,
            "processed_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7)  # Auto-cleanup after 7 days
        })

        return False

    async def batch_retrieve_customers(self, customer_ids: List[str]) -> Dict[str, Any]:
        """
        Batch retrieve multiple customers (for admin dashboard)

        Args:
            customer_ids: List of customer IDs

        Returns:
            Dictionary mapping customer_id to customer data
        """
        await self._ensure_stripe_configured()

        results = {}
        for customer_id in customer_ids:
            try:
                customer = await self._retry_with_backoff(
                    stripe.Customer.retrieve,
                    customer_id
                )
                results[customer_id] = {
                    "email": customer.email,
                    "name": customer.name,
                    "created": customer.created
                }
            except stripe.error.StripeError as e:
                logger.error(f"Error retrieving customer {customer_id}: {e}")
                results[customer_id] = None

        return results
