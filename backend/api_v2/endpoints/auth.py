"""
Authentication endpoints with rate limiting
"""
from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from schemas.user_schemas import UserCreate, UserResponse, Token
from models import UserLogin
from auth import get_password_hash, verify_password, create_access_token
from config import settings
from api_v2.middleware import limiter, RateLimits
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# MongoDB connection
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password"
)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def register(user_data: UserCreate):
    """
    Register a new user

    Args:
        user_data: User registration data (email, password, full_name)

    Returns:
        Created user data (without password)

    Raises:
        HTTPException 400: Email already registered
        HTTPException 422: Invalid input data
    """
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )

    # Create new user
    from models import User
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )

    # Store in database
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['updated_at'] = user_dict['updated_at'].isoformat()

    await db.users.insert_one(user_dict)

    logger.info(f"New user registered: {user.email}")

    return UserResponse(**user.model_dump())


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user and receive JWT token"
)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login(credentials: UserLogin):
    """
    Authenticate user and return JWT token

    Args:
        credentials: User email and password

    Returns:
        JWT access token

    Raises:
        HTTPException 401: Invalid credentials
    """
    # Find user
    user = await db.users.find_one({"email": credentials.email})

    if not user or not verify_password(credentials.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if account is active
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé. Contactez le support."
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user['id'], "email": user['email']}
    )

    logger.info(f"User logged in: {user['email']}")

    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/password-reset",
    summary="Request password reset",
    description="Send password reset email"
)
@limiter.limit(RateLimits.AUTH_PASSWORD_RESET)
async def request_password_reset(email: str):
    """
    Request password reset (sends email with reset link)

    Args:
        email: User email address

    Returns:
        Success message

    Note:
        Always returns success to prevent email enumeration
    """
    user = await db.users.find_one({"email": email})

    if user:
        # TODO: Implement email sending with reset token
        logger.info(f"Password reset requested for: {email}")

    # Always return success (security best practice)
    return {
        "message": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."
    }
