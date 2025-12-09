"""
User-related Pydantic schemas with validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User full name")


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=128, description="User password (min 8 characters)")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema for user API responses"""
    id: str = Field(..., description="User unique identifier")
    is_active: bool = Field(default=True, description="Whether user account is active")
    is_admin: bool = Field(default=False, description="Whether user has admin privileges")
    subscription_status: str = Field(default="inactive", description="Current subscription status")
    current_period_end: Optional[datetime] = Field(None, description="Subscription period end date")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "usr_1234567890",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_admin": False,
                "subscription_status": "active",
                "current_period_end": "2024-12-31T23:59:59Z",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class UserInDB(UserResponse):
    """Internal schema with sensitive data (not exposed via API)"""
    hashed_password: str
    stripe_customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    updated_at: datetime


class Token(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Data extracted from JWT token"""
    user_id: str
    email: str
    exp: datetime
