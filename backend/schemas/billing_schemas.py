"""
Billing and subscription-related Pydantic schemas
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


class SubscriptionPlanResponse(BaseModel):
    """Available subscription plan details"""
    name: str = Field(default="Pro", description="Plan name")
    price: float = Field(..., ge=0, description="Plan price in EUR")
    currency: str = Field(default="eur", description="Currency code")
    interval: str = Field(default="month", description="Billing interval")
    features: List[str] = Field(..., description="List of included features")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Pro",
                "price": 9.90,
                "currency": "eur",
                "interval": "month",
                "features": [
                    "Unlimited agentic code generation",
                    "Unlimited projects",
                    "GitHub & Vercel export",
                    "Priority support"
                ]
            }
        }


class CheckoutSessionResponse(BaseModel):
    """Stripe checkout session response"""
    session_id: str = Field(..., description="Stripe checkout session ID")
    url: HttpUrl = Field(..., description="Checkout session URL")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "cs_test_1234567890",
                "url": "https://checkout.stripe.com/c/pay/cs_test_1234567890"
            }
        }


class PortalSessionResponse(BaseModel):
    """Stripe customer portal session response"""
    url: HttpUrl = Field(..., description="Customer portal URL")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://billing.stripe.com/p/session/test_1234567890"
            }
        }


class InvoiceResponse(BaseModel):
    """Invoice details response"""
    id: str = Field(..., description="Invoice ID")
    amount: float = Field(..., ge=0, description="Invoice amount")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="Invoice status (paid, open, void, uncollectible)")
    invoice_pdf: Optional[HttpUrl] = Field(None, description="PDF invoice URL")
    created: int = Field(..., description="Creation timestamp (Unix)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "in_1234567890",
                "amount": 9.90,
                "currency": "eur",
                "status": "paid",
                "invoice_pdf": "https://pay.stripe.com/invoice/1234567890/pdf",
                "created": 1704067200
            }
        }


class WebhookEvent(BaseModel):
    """Stripe webhook event data"""
    type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data object")
    created: int = Field(..., description="Event creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "customer.subscription.created",
                "data": {
                    "object": {
                        "id": "sub_1234567890",
                        "customer": "cus_1234567890",
                        "status": "active"
                    }
                },
                "created": 1704067200
            }
        }


class BillingSettings(BaseModel):
    """Billing configuration settings"""
    price: float = Field(default=9.90, ge=0, description="Subscription price")
    free_trial_days: int = Field(default=7, ge=0, le=90, description="Free trial period in days")
    max_failed_payments: int = Field(default=3, ge=1, description="Max failed payment attempts before blocking")

    class Config:
        json_schema_extra = {
            "example": {
                "price": 9.90,
                "free_trial_days": 7,
                "max_failed_payments": 3
            }
        }
